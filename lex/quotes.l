%option noyywrap stack warn
%option outfile="quotes.c"

%{
/*
Convert straight quotes (" and ') to curly quotes (“” and ‘’).

The basic idea is to detect all conditions for opening quotation marks (“ and ‘).
All remaining quotation marks are assumed to be closing (” and ’).
*/

#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static void open_qs();
static void close_qs();
static void open_ambiguous();
static void open_with_apostrophe();
%}

EM_DASH         --|—
LBRACKET        [(\[{]
TAG_CHARS       [[:alnum:] ]
OPEN_TAG        <{TAG_CHARS}+>

PRE_OPEN        {LBRACKET}|[ ]|{EM_DASH}|{OPEN_TAG}|“|‘
POST_OPEN       [^[:space:]'"]
QUOTE           ['"]

CONTRACTION     '(em|im|gainst|tis|twas|twere|twould)[[:^alnum:]]

%%
{PRE_OPEN}''{POST_OPEN}         |
^''{POST_OPEN}                  open_with_apostrophe();

{PRE_OPEN}{QUOTE}+{POST_OPEN}   |
^{QUOTE}+{POST_OPEN}            open_qs();

{QUOTE}                         close_qs();

(?i:{PRE_OPEN}?{CONTRACTION})   close_qs();
(?i:["]{CONTRACTION})           open_with_apostrophe();

{EM_DASH}{QUOTE}{EM_DASH}       open_ambiguous();
%%

typedef enum {
    OPEN_SINGLE,
    CLOSE_SINGLE,
    OPEN_DOUBLE,
    CLOSE_DOUBLE
} quote_type;

typedef enum {
    CLOSE,
    OPEN
} side_type;

static side_type prev_single;
static side_type prev_double;

int main() {
    yylex();
    return 0;
}

/* Print the given quotation mark */
static void printq(quote_type q) {
    switch (q) {
        case OPEN_SINGLE:  printf("‘"); prev_single = OPEN;  break;
        case CLOSE_SINGLE: printf("’"); prev_single = CLOSE; break;
        case OPEN_DOUBLE:  printf("“"); prev_double = OPEN;  break;
        case CLOSE_DOUBLE: printf("”"); prev_double = CLOSE; break;
    }
}

/* Print the match with straight quotes converted to opening curly quotes */
static void open_qs() {
    for (int i = 0; i < yyleng; i++) {
        switch (yytext[i]) {
            case '"':  printq(OPEN_DOUBLE); break;
            case '\'': printq(OPEN_SINGLE); break;
            default:
                putchar(yytext[i]);
                break;
        }
    }
}

/* Print the match with straight quotes converted to closing curly quotes */
static void close_qs() {
    for (int i = 0; i < yyleng; i++) {
        switch (yytext[i]) {
            case '"':  printq(CLOSE_DOUBLE); break;
            case '\'': printq(CLOSE_SINGLE); break;
            default:
                putchar(yytext[i]);
                break;
        }
    }
}

/* Decide which quote to use in ambiguous cases such as: --"--. */
/* To decide, use our memory of the previously selected quote type. */
static void open_ambiguous() {
    side_type prev;

    prev = memchr(yytext, '"', yyleng) ? prev_double : prev_single;

    if (prev == OPEN) {
        close_qs();
    } else {
        open_qs();
    }
}

/* Print the match, treating the first quotation mark as an open */
/* and all remaining quotation marks as closes. */
static void open_with_apostrophe() {
    bool found = false;

    for (int i = 0; i < yyleng; i++) {
        switch (yytext[i]) {
            case '"':
                printq(found ? CLOSE_DOUBLE : OPEN_DOUBLE);
                found = true;
                break;
            case '\'':
                printq(found ? CLOSE_SINGLE : OPEN_SINGLE);
                found = true;
                break;
            default:
                putchar(yytext[i]);
                break;
        }
    }
}
