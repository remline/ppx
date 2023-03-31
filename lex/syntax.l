%option noyywrap stack warn yylineno
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

EM_DASH         --|—
QUOTE           ['"]|“|”|‘|’
ROMAN_NUM       [IVXLCDM]

%%
M'
M‘
{ROMAN_NUM}".'s"
{ROMAN_NUM}".’s"
{QUOTE}{EM_DASH}
{EM_DASH}{QUOTE}

" \" "              |
^"\" "              |
" ' "               |
^"' "               |
^"”"                |
^"’ "               |
{ANP}\"{AN}         |
{AN}''{AN}          |
{P}'{AN}            |
{P}’{AN}            |
" '' "              |
[[:punct:]]''       |
{ANP}‘              |
{ANP}“              |
‘{P}                |
“{P}                |
”{AN}               |
"“ "                |
"‘ "                |
" ”"                |
" ."                |
" ,"                |
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
"-----"             |
"---"               |
"—-"                |
"-—"                |
-{QUOTE}            |
{QUOTE}-            |
" ...."             |
"...."{AN}          |
"  ..."             |
"...  "             |
"....  "            error();
" \""$              error();
" '"$               error();
"''"$               error();
" ’"$               error();
" “"$               error();
" ‘"$               error();

[ ]$                error_str("Trailing space");

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
static char is_error;
static char stack[STACK_SZ];

int main() {
yylex();

if (cnt) {
    printf("End of file: Unclosed '%c'\n", stack[cnt-1]);
    is_error = 1;
    }

return is_error;
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
        is_error = 1;
        }
    else if (actual != pair) {
        printf("line %i: Found '%c' after '%c'\n", yylineno, c, actual);
        is_error = 1;
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
    is_error = 1;
}

static void error_str(const char * s) {
    printf("line %i: %s\n", yylineno, s);
    is_error = 1;
}
