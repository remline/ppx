%option noyywrap stack warn
%option outfile="quotes.c"

%{
#include <stdlib.h>
#include <string.h>

static void open_qs();
static void close_qs();
static void open_ambiguous();
static void open_with_apostrophe();
%}

EMDASH          —
OPEN            [(\[{<]
CLOS            [)\]}>]
PREQUOTE        {OPEN}|[ \-]|{EMDASH}|“
POSTQUOTE       {CLOS}|[ \-.,!?;:]|{EMDASH}|’
QUOTE           ['"]|'\"|\"'
NON_QUOTE       [^'"\n]
CONTRACTION     em|gainst|tis|twas|twere|twould

%%
\"                      |
{PREQUOTE}{QUOTE}[^ ]   |
^{QUOTE}                open_qs();

'                       |
{QUOTE}{POSTQUOTE}      close_qs();
{NON_QUOTE}*{QUOTE}$    close_qs();

^''                     |
{PREQUOTE}''[^ ]        open_with_apostrophe();

[^ "\n]'                |
(?i:[ ]?'{CONTRACTION}) close_qs();

{EMDASH}['"]{EMDASH}    |
--['"]--                open_ambiguous();
%%

enum {
    LEFT,
    RIGHT
};

static int prev_single;
static int prev_double;

int main() {
    yylex();
    return 0;
}

/* Print the match with straight quotes converted to opening curly quotes */
static void open_qs() {
    for (int i = 0; i < yyleng; i++) {
        switch (yytext[i]) {
            case '"':  printf("“"); prev_double = LEFT; break;
            case '\'': printf("‘"); prev_single = LEFT; break;
            default:
                printf("%c", yytext[i]);
                break;
        }
    }
}

/* Print the match with straight quotes converted to closing curly quotes */
static void close_qs() {
    for (int i = 0; i < yyleng; i++) {
        switch (yytext[i]) {
            case '"':  printf("”"); prev_double = RIGHT; break;
            case '\'': printf("’"); prev_single = RIGHT; break;
            default:
                printf("%c", yytext[i]);
                break;
        }
    }
}

/* Decide which quote to use in ambiguous cases such as: --"--. */
/* To decide, use our memory of the previously selected quote type. */
static void open_ambiguous() {
    int prev;

    if (memchr(yytext, '"', yyleng)) {
        prev = prev_double;
    } else {
        prev = prev_single;
    }

    if (prev == LEFT) {
        close_qs();
    } else {
        open_qs();
    }
}

/* Print the match with an opening single quote and an apostrophe */
static void open_with_apostrophe() {
    static char const * const chars[] = {"‘", "’"};
    int c = 0;

    for (int i = 0; i < yyleng; i++) {
        switch (yytext[i]) {
            case '\'':
                printf(chars[c]);
                c = (c + 1) % 2;
                break;
            default:
                printf("%c", yytext[i]);
                break;
        }
    }
}
