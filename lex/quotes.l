%option noyywrap stack warn yylineno
%option outfile="quotes.c"

%{
#include <stdlib.h>

static void open_qs();
static void close_qs();
%}

OPEN            [(\[{<]
CLOS            [)\]}>]
PREQUOTE        {OPEN}|[ \-]
POSTQUOTE       {CLOS}|[ \-.,!?;:]
QS              '|\"|'\"|\"'
CONTRACTION     em|gainst|tis|twas|twere|twould

%%
{PREQUOTE}{QS}  open_qs();
^{QS}           open_qs();
-?{QS}{POSTQUOTE} close_qs();
{QS}$           close_qs();

[^ "\n]'        close_qs();
(?i:[ ]?'{CONTRACTION}) close_qs();
'               open_qs();
\"              open_qs();
\n              ECHO;
%%

int main() {
    yylex();
    return 0;
}

static void open_qs() {
    for (int i = 0; i < yyleng; i++) {
        switch (yytext[i]) {
            case '"':  printf("“"); break;
            case '\'': printf("‘"); break;
            default:
                printf("%c", yytext[i]);
                break;
        }
    }
}

static void close_qs() {
    for (int i = 0; i < yyleng; i++) {
        switch (yytext[i]) {
            case '"':  printf("”"); break;
            case '\'': printf("’"); break;
            default:
                printf("%c", yytext[i]);
                break;
        }
    }
}
