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

%%
" \" "              |
^"\" "              error();
" \""$              |
" ' "               |
^"' "               error();
" '"$               |
[[:alnum:]]‘        |
[[:alnum:]]“        |
”[[:alnum:]]        |
" ."                |
" ,"                |
[ ][!?;:]           |
[!?;:][[:alpha:]]   |
,[[:alpha:]]        |
"....."             |
[ ]?\"\"            |
.?''                |
".."                |
",,"                |
";;"                |
"::"                |
"**"                |
"-*"                |
"-----"             |
"---"               |
" ...."             |
"...."[[:alnum:]]   |
"  ..."             |
"...  "             |
"....  "            error();

[ ]$            error_str("Trailing space");

[ ]?"..."       ECHO;
"----"          ECHO;

{OPEN}          check_pair(yytext[0]); ECHO;
{CLOS}          check_pair(yytext[0]); ECHO;
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
    fprintf(stderr, "End of file: Unclosed '%c'\n", stack[cnt-1]);
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
        fprintf(stderr, "line %i: Found '%c' without '%c'\n", yylineno, c, pair);
        is_error = 1;
        }
    else if (actual != pair) {
        fprintf(stderr, "line %i: Found '%c' after '%c'\n", yylineno, c, actual);
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
    fprintf(stderr, "line %i: Bad sequence <%s>\n", yylineno, yytext);
    is_error = 1;
    ECHO;
}

static void error_str(const char * s) {
    fprintf(stderr, "line %i: %s\n", yylineno, s);
    is_error = 1;
    ECHO;
}
