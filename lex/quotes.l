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
POST_OPEN       [^[:space:]'")\]}]
QUOTE           ['"]

CON_LIST        em|im|gainst|tis|twas|twere|twould
PRE_CON         {PRE_OPEN}{QUOTE}?
CON             '(?i:{CON_LIST})

%%
{PRE_CON}''{POST_OPEN}          |
^{QUOTE}?''{POST_OPEN}          open_with_apostrophe();
{PRE_CON}{CON}/[[:^alnum:]]     open_with_apostrophe();
^{QUOTE}?{CON}/[[:^alnum:]]     open_with_apostrophe();

{PRE_OPEN}{QUOTE}+{POST_OPEN}   |
^{QUOTE}+{POST_OPEN}            open_qs();

{QUOTE}                         close_qs();

{EM_DASH}{QUOTE}{EM_DASH}       open_ambiguous();
%%

typedef enum {
    OPEN_SINGLE,
    CLOSE_SINGLE,
    OPEN_DOUBLE,
    CLOSE_DOUBLE,
    APOSTROPHE,
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
        case APOSTROPHE:   printf("’"); break;
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

/* Print the match, treating the final single quote as an apostrophe */
/* and all other quotation marks as opens. */
static void open_with_apostrophe() {
    int ap_index;

    /* Find the final single quote. If not found, */
    /* the index will be -1. */
    for(ap_index = yyleng - 1; ap_index >= 0; ap_index--) {
        if (yytext[ap_index] == '\'') {
            break;
        }
    }

    /* Convert to open quotes and an apostrophe */
    for (int i = 0; i < yyleng; i++) {
        if (i == ap_index) {
            printq(APOSTROPHE);
        } else if(yytext[i] == '"') {
            printq(OPEN_DOUBLE);
        } else if(yytext[i] == '\'') {
            printq(OPEN_SINGLE);
        } else {
            putchar(yytext[i]);
        }
    }
}
