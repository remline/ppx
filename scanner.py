from typing import NamedTuple
import re

class Token(NamedTuple):
    type: str
    value: str
    line: int
    column: int

def tokenize(code):
    keywords = {'IF', 'THEN', 'ENDIF', 'FOR', 'NEXT', 'GOSUB', 'RETURN'}
    token_specification = [
      ('Anchor',    r"abc"),
      ('Blank',    r"Blank Page"),
      ('FnStart',    r"Footnote 0-9A-Z: "),
      ('Ill',    r"Illustration"        ),
      ('IllStart',    r"Illustration: "       ),
      ('SnStart',    r"Sidenote: "           ),
      ('Pb',    r"-----File: .*-----"  ),
      ('TnChange',    r"old"          ),
      #  ('NUMBER',   r'\d+(\.\d*)?'),  # Integer or decimal number
      #  ('ASSIGN',   r':='),           # Assignment operator
      #  ('END',      r';'),            # Statement terminator
      #  ('ID',       r'[A-Za-z]+'),    # Identifiers
      #  ('OP',       r'[+\-*/]'),      # Arithmetic operators
      #  ('NEWLINE',  r'\n'),           # Line endings
      #  ('SKIP',     r'[ \t]+'),       # Skip over spaces and tabs
      #  ('MISMATCH', r'.'),            # Any other character
    ]
    tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
    obj = re.compile(tok_regex)

    line_num = 1
    line_start = 0
    for mo in obj.finditer(code):
        kind = mo.lastgroup
        value = mo.group()
        column = mo.start() - line_start
        if kind == 'NUMBER':
            value = float(value) if '.' in value else int(value)
        elif kind == 'ID' and value in keywords:
            kind = value
        elif kind == 'NEWLINE':
            line_start = mo.end()
            line_num += 1
            continue
        elif kind == 'SKIP':
            continue
        elif kind == 'MISMATCH':
            continue
        yield Token(kind, value, line_num, column)

with open('/home/remline/pg/dreams/projectID5e94a1a7620cd.txt') as proj:
    ttt = proj.read()

zz=1

for token in tokenize(ttt):
    zz += 1

print(zz)
