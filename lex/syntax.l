%option noyywrap warn yylineno
%option outfile="syntax.c"

%{
#include <stdlib.h>

static void check_pair(char c);
static void error();
static void error_str(const char * s);
%}

OPEN            [(\[{<]
CLOS            [)\]}>]

A               [[:alpha:]]
AN              [[:alnum:]]
ANP             {AN}|{P}
D               [[:digit:]]
P               [.,!?;:]

EM_DASH         --|—|―
LQUOTE          “|‘
RQUOTE          ”|’
QUOTE           ["']|{LQUOTE}|{RQUOTE}
APOSTROPHE      '|’
ARTICLE         (?i:the|an)

%%
M'
M‘
[[:upper:]][.]{APOSTROPHE}s
{LQUOTE}"..."
"*** "(START|END).*\n?.*"***"
" ."{D}

[ ]["'][ ]          |
^["'][ ]            |
^”                  |
^’[ ]               |
{ANP}\"{AN}         |
{AN}''{AN}          |
{P}{APOSTROPHE}{AN} |
" '' "              |
{P}''               |
{ANP}{LQUOTE}       |
{LQUOTE}{P}         |
”{AN}               |
{LQUOTE}[ ]         |
" ”"                |
" ."{1,}            |
" ,"{1,}            |
[ ][!?;:]           |
[!?;:]{A}           |
,{A}                |
"....."             |
". ..."             |
[ ]?\"\"            |
{A}{D}{A}           |
".."                |
",,"                |
";;"                |
"::"                |
"““"                |
"‘‘"                |
"””"                |
"**"                |
"-*"                |
-{5,}               |
-{3}                |
"—-"                |
"-—"                |
" ...."             |
"...."{AN}          |
"...  "             |
"....  "            |
{EM_DASH}[ ]        |
[ ]{EM_DASH}        |
[[:^alnum:]]{ARTICLE}{P} |
^{ARTICLE}{P}       error();
"''"$               error();
[ ]{QUOTE}$         error();

[ ]$                error_str("Trailing space");

{EM_DASH}{QUOTE}
{QUOTE}{EM_DASH}
{EM_DASH}{APOSTROPHE}[[:^alnum:]]
[[:^alnum:]]{APOSTROPHE}{EM_DASH}
{EM_DASH}{2}[ ]
[ ]{EM_DASH}{2}

-(["]|“|”|‘)                |
(["]|“|”|‘)-                |
-{APOSTROPHE}[[:^alnum:]]   |
[[:^alnum:]]{APOSTROPHE}-   error();

[ ]?"..."
"----"
"-----File: ".+

{OPEN}              |
{CLOS}              check_pair(yytext[0]);
{OPEN}[ ]           check_pair(yytext[0]); error();
[ ]{CLOS}           check_pair(yytext[1]); error();

\n                  /* needed to count line numbers */
.                   /* ignore all other tokens */
%%

enum {
    STACK_SZ = 32
    };

static unsigned cnt;
static char stack[STACK_SZ];

int main() {
yylex();

if (cnt) {
    printf("End of file: Unclosed '%c'\n", stack[cnt-1]);
    }

return 0;
}

static void pop(char c) {
    char actual = 0;
    char pair = 0;

    switch (c) {
        case ')': pair = '('; break;
        case ']': pair = '['; break;
        case '}': pair = '{'; break;
        case '>': pair = '<'; break;
        default:
            error_str("Fatal: Unhandled character in pop()");
            exit(1);
        }

    if (cnt) {
        actual = stack[cnt - 1];
        cnt--;
        }

    if (actual == 0) {
        printf("line %i: Found '%c' without '%c'\n", yylineno, c, pair);
        }
    else if (actual != pair) {
        printf("line %i: Found '%c' after '%c'\n", yylineno, c, actual);
        }
}

static void push(char c) {
    if (cnt < STACK_SZ ) {
        stack[cnt] = c;
        cnt++;
        }
    else {
        error_str("Fatal: Stack full");
        exit(1);
        }
}

static void check_pair(char c) {
    if (c == '(' || c == '[' || c == '{' || c == '<' ) {
        push(c);
        }
    else if (c == ')' || c == ']' || c == '}' || c == '>' ) {
        pop(c);
        }
}

static void error() {
    printf("line %i: Bad sequence <%s>\n", yylineno, yytext);
}

static void error_str(const char * s) {
    printf("line %i: %s\n", yylineno, s);
}
