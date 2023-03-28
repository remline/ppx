all: quotes syntax xml

quotes: quotes.c
	cc -Wall -Wno-unused-function -o quotes quotes.c
syntax: syntax.c
	cc -Wall -Wno-unused-function -o syntax syntax.c
xml: xml.c
	cc -Wall -Wno-unused-function -o xml xml.c
quotes.c: quotes.l
	flex quotes.l
syntax.c: syntax.l
	flex syntax.l
xml.c: xml.l
	flex xml.l
