%option noyywrap stack warn yylineno
%option outfile="xml.c"

%{
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>

/* tagged items in [brackets] */
typedef enum {
    TAG_FOOTNOTE,
    TAG_SIDENOTE,
    TAG_ILLUSTRATION,
    TAG_PLAIN_TEXT
} tag_type;

static const char * const tag_names[] = {
    /* TAG_FOOTNOTE     */ "footnote",
    /* TAG_SIDENOTE     */ "sidenote",
    /* TAG_ILLUSTRATION */ "illustration",
    /* TAG_PLAIN_TEXT   */ "[bracketed text]"
};

static tag_type pop_tag();
static void add_brs();
static void anchor();
static void check_p_start();
static void class_start();
static void close_bracket();
static void close_text();
static void error(char const * str);
static void footnote();
static void four_blanks();
static void illustration();
static void internal_error(char const * str);
static void one_blank();
static void page();
static void push_tag(tag_type t);
static void sidenote();
static void start_p();
static void start_p_merge();
static void tn();
static void two_blanks();
%}

%s          PRE
%s          TN

Anchor      \[[0-9A-Z]\]
Blank       "[Blank Page]"
BqStart     ^"/#\n"
NowrapStart ^"/*\n"
BqEnd       "\n#/"
NowrapEnd   "\n*/"
ClassStart  "<"[dps]" "[[:alnum:] ]*>
DivEnd      "</d>"
SpanEnd     "</s>"
FnStart     "[Footnote "[0-9A-Z]": "
Ill         "[Illustration]"
IllStart    "[Illustration: "
SnStart     "[Sidenote: "
Pb          "-----File: ".*"-----"
TnIns       "["[^\]\n]+"]"
TnDel       "{"[^{\n]+"}"
TnChange    {TnIns}|{TnDel}

%%
{Anchor}        anchor();
{Pb}            page();
{Blank}
{BqStart}       printf("<blockquote>");
{BqEnd}         close_text(); printf("</blockquote>");
{Ill}           printf("<illustration />");
{FnStart}       footnote();
{IllStart}      illustration();
{SnStart}       sidenote();
{ClassStart}    class_start();
{DivEnd}        close_text(); printf("</div>");
{SpanEnd}       printf("</span>");
"<h1>"          ECHO;
"<tb>"          printf("<tb />");
"<title>"       ECHO;

{NowrapStart}   printf("<nowrap>");  yy_push_state(PRE);
{NowrapEnd}     printf("</nowrap>"); yy_pop_state();
<PRE>\n+        add_brs();
<PRE>^.         ECHO;

^"<tn>"         check_p_start(); ECHO; yy_push_state(TN);
"<tn>"                           ECHO; yy_push_state(TN);
"</tn>"         ECHO; yy_pop_state();
<TN>{TnChange}  tn();

^\[             check_p_start(); ECHO; push_tag(TAG_PLAIN_TEXT);
\[                               ECHO; push_tag(TAG_PLAIN_TEXT);
]               close_bracket();

\n\n\n\n\n      four_blanks();
\n\n\n          two_blanks();
\n\n            one_blank(); ECHO;
^&              check_p_start(); printf("&amp;");
&                                printf("&amp;");
^.              check_p_start(); ECHO;
\n              ECHO;
%%

enum {
    TAG_STACK_SZ = 32
    };

/* text items */
typedef enum
    {
    TXT_NONE,   /* tagged object (e.g., footnote) */
    TXT_HEAD,   /* chapter heading */
    TXT_P       /* paragraph */
    } txt_type;

static bool     s_is_headgroup;
static bool     s_is_error;
static unsigned s_pb_line;
static unsigned s_tag_cnt;
static tag_type s_tag_stack[TAG_STACK_SZ];
static txt_type s_txt;

static tag_type pop_tag() {
    tag_type t;

    if (s_tag_cnt) {
        t = s_tag_stack[s_tag_cnt - 1];
        s_tag_cnt--;
        }
    else {
        error("Tag stack empty");
        exit(1);
        }

    return t;
}

static void push_tag(tag_type t) {
    if (s_tag_cnt < TAG_STACK_SZ ) {
        s_tag_stack[s_tag_cnt] = t;
        s_tag_cnt++;
        }
    else {
        internal_error("Tag stack full");
        }
}

static void close_bracket() {
    tag_type tag = pop_tag();

    switch (tag) {
        case TAG_FOOTNOTE:
        case TAG_SIDENOTE:
        case TAG_ILLUSTRATION:
            close_text();
            printf("</%s>", tag_names[tag]);
            break;
        case TAG_PLAIN_TEXT:
            printf("]");
            break;
        default:
            internal_error("Tag stack corrupt");
            break;
    }
}

/* add line break tags, for use in pre-formatted mode */
static void add_brs() {
    int i;

    for (i = 0; i < yyleng; i++ ) {
        printf("<br />\n");
    }
}

static void anchor() {
    printf("<anchor n='%c' />", yytext[1]);
}

/* add the start tag for a div, paragraph, or span
   div syntax:       <d classname classname ...>
   paragraph syntax: <p classname classname ...>
   span syntax:      <s classname classname ...>
*/
static void class_start() {
    char const * class;
    char const * tag;
    size_t class_len;
    char type;

    /* min length: <d c> */
    if (yyleng < 5) {
        internal_error("Incomplete class tag");
        return;
    }

    type = yytext[1];
    class = &yytext[3];
    class_len = yyleng - 4;

    switch (type) {
        case 'd': tag = "div";  break;
        case 'p': tag = "p";    break;
        case 's': tag = "span"; break;
        default:
            internal_error("Unhandled tag abbreviation");
            return;
    }

    if (type == 'd') {
        close_text();
    }

    if (type == 'p') {
        close_text();
        s_txt = TXT_P;
    }

    printf("<%s class='", tag);
    fwrite(class, 1, class_len, stdout);
    printf("'>");
}

static void footnote() {
    close_text();
    printf("<footnote n='%c'>", yytext[yyleng-3]);
    push_tag(TAG_FOOTNOTE);
    start_p();
}

static void close_headgroup() {
    if (s_is_headgroup) {
        close_text();
        printf("</headgroup>\n");
        s_is_headgroup = false;
    }
}

static void close_text() {
    static char const * const xml[] =
        {
        /* TXT_NONE */ "",
        /* TXT_HEAD */ "</head>",
        /* TXT_P    */ "</p>"
        };

    if (s_txt != TXT_NONE)
        {
        printf("%s", xml[s_txt]);
        s_txt = TXT_NONE;
        }
}

/* Four blank lines start a chapter heading group */
static void four_blanks() {
    close_text();
    close_headgroup();

    printf("\n<headgroup><head>");
    s_txt = TXT_HEAD;
    s_is_headgroup = true;
}

/* Two blank lines ends a chapter head group
   or starts a section */
static void two_blanks() {
    if (s_is_headgroup) {
        close_headgroup();
    } else {
        close_text();
        printf("\n<sectionbreak />\n");
    }
}

/* One blank line ends a paragraph or heading */
static void one_blank() {
    close_text();
}

static void start_p() {
    printf("<p>");
    s_txt = TXT_P;
}

static void start_p_merge() {
    printf("<p type='merge'>");
    s_txt = TXT_P;
}

static void check_p_start() {
    if (s_txt == TXT_NONE) {
        if (yylineno == s_pb_line + 1) {
            start_p_merge();
        }
        else {
            start_p();
        }
    }
}

static void illustration() {
    close_text();
    printf("<illustration>");
    push_tag(TAG_ILLUSTRATION);
    start_p();
}

static void sidenote() {
    close_text();
    printf("<sidenote>");
    push_tag(TAG_SIDENOTE);
    start_p();
}

/* Page Beginning
     Auto number:
     -----File: filename.png-----

     Manual number:
     -----File: filename.png page-----
*/
static void page() {
    static const char filename_end[] = "png ";

    char * page_start = strstr(yytext, filename_end);
    char * page_end = 0;

    close_headgroup();

    if (page_start) {
        page_start += sizeof(filename_end) - 1;
        page_end = strchr(page_start, '-');

        if (page_end) {
            *page_end = 0; /* terminate page number string */
            }
        }

    if (page_start && page_end) {
        printf("<pb n='%s' />", page_start);
        }
    else {
        printf("<pb />");
        }

    s_pb_line = yylineno;
}

static void error(char const * str) {
    fprintf(stderr, "line %i: %s\n", yylineno, str);
    s_is_error = true;
}

static void internal_error(char const * str) {
    fprintf(stderr, "line %i: Internal error: %s\n", yylineno, str);
    exit(1);
}

/* Transcriber's Note
    Insertion:
    Add a [word]

    Deletion:
    Remove a {word}
*/
static void tn() {
    size_t len;
    char const * tag;
    char const * text;

    /* min length: [] */
    if (yyleng < 2) {
        internal_error("Incomplete TN");
        return;
    }

    text = &yytext[1];
    len = yyleng - 2;

    switch(yytext[0]) {
        case '[': tag = "ins"; break;
        case '{': tag = "del"; break;
        default:
            internal_error("Invalid TN change");
            return;
    }

    printf("<%s>", tag);
    fwrite(text, 1, len, stdout);
    printf("</%s>", tag);
}

int main() {
printf("<book>\n");

yylex();

close_headgroup();
close_text();

printf("</book>\n");

if (s_tag_cnt) {
    fprintf(stderr, "End of file: Unclosed %s\n", tag_names[pop_tag()]);
    s_is_error = true;
    }

return s_is_error;
}
