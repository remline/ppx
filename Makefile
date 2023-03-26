all: punc xml

punc: punc.c
	cc -Wall -Wno-unused-function -o punc punc.c
xml: xml.c
	cc -Wall -Wno-unused-function -o xml xml.c
punc.c: punc.l
	flex punc.l
xml.c: xml.l
	flex xml.l
