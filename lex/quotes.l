%option noyywrap stack warn
%option outfile="quotes.c"

%{
#include <stdlib.h>

static void open_qs();
static void close_qs();
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
