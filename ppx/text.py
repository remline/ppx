"""Write Plain Text format"""
# pylint: disable=missing-function-docstring

import textwrap
import process
from share import Mode, Processing

INDENT_SIZE = 2

class BufferedFile:
    """
    Buffered file writer. Wraps text as it flushes unless the
    nowrap flag is on.
    """
    def __init__(self, file):
        self.buffer = ''
        # pylint: disable=consider-using-with
        self.file = open(file, mode='w', encoding='utf-8')
        self.indent = 0
        self.next_indent = 0
        self.nowrap = False
        self.wrapper = textwrap.TextWrapper(width=71, break_on_hyphens=False)

    def close(self):
        self._flush()
        self.file.close()

    def print(self, string):
        if self.buffer.endswith('\n\n'):
            self._flush()

        self.buffer += string

    def set_indent(self, indent):
        self.next_indent = indent

    def set_nowrap(self, enabled):
        self._flush()
        self.nowrap = enabled

    def _flush(self):
        if self.nowrap:
            self._write_nowrap(self.buffer)
        else:
            self._write_wrap(self.buffer)

        self.buffer = ''

    def _update_indent(self, indent):
        if self.indent != indent:
            self.indent = indent

            chars = ' ' * indent
            self.wrapper.initial_indent = chars
            self.wrapper.subsequent_indent = chars

    def _write_nowrap(self, s):
        indent_chars = ' ' * (self.indent + INDENT_SIZE)

        # Indent each line, but not empty lines (which consist of
        # a single newline character)
        for line in s.splitlines(keepends=True):
            if line != '\n':
                line = indent_chars + line

            self.file.write(line)

    def _write_wrap(self, s):
        len0 = len(s)
        s = s.lstrip('\n')
        len1 = len(s)
        prefix = '\n' * (len0 - len1)

        s = s.rstrip('\n')
        len2 = len(s)
        suffix = '\n' * (len1 - len2)

        wrapped = self.wrapper.fill(s)
        self.file.write(f'{prefix}{wrapped}{suffix}')
        self._update_indent(self.next_indent)

class Context:
    """Context manager"""
    def __init__(self):
        self.buffer = BufferedFile('out.txt')
        self.caps = False
        self.indent_level = 0
        self.inside_paragraph = False
        self.mode = None
        self.suppress_newline = False
        self.suppress_paragraph = False

    def close(self):
        self.buffer.close()

    def print(self, string):
        self.buffer.print(string)

    def indent(self):
        self.indent_level += INDENT_SIZE
        self.buffer.set_indent(self.indent_level)

    def dedent(self):
        self.indent_level -= INDENT_SIZE
        self.buffer.set_indent(self.indent_level)

        assert self.indent_level >= 0

    def set_nowrap(self, enabled):
        self.buffer.set_nowrap(enabled)

def data(text):
    if context.inside_paragraph:
        if context.suppress_newline and text.startswith('\n'):
            text = text[1:]
            context.suppress_newline = False
    else:
        text = text.strip('\n')

    if context.caps:
        text = text.upper()

    context.print(text)

def bold(_elem):
    context.print('=')

def blockquote_open(_elem):
    context.indent()

def blockquote_close(_elem):
    context.dedent()

def br(_elem):
    print_newline()

def h1_open(_elem):
    print_newlines(4)

def h1_close(_elem):
    print_newline()

def head_close(_elem):
    print_newline()

def headgroup_open(_elem):
    print_newlines(4)

def headgroup_close(_elem):
    print_newline()

def ill_open(elem):
    print_newline()
    context.print('[Illustration')

    if len(elem):
        context.print(': ')

    context.suppress_paragraph = True

def ill_close(_elem):
    context.print(']')
    print_newline()
    context.suppress_paragraph = False

def italic(_elem):
    context.print('_')

def nowrap_open(_elem):
    print_newline()
    context.set_nowrap(True)

def nowrap_close(_elem):
    context.set_nowrap(False)
    print_newline()

def p_open(_elem):
    context.inside_paragraph = True

    if not context.suppress_paragraph:
        print_newline()

def p_close(_elem):
    context.inside_paragraph = False

    if not context.suppress_paragraph:
        print_newline()

def pb_open(_elem):
    # Page breaks are represented in the XML as:
    #   <p>line 1
    #   <pb />
    #   line 2</p>
    # Avoid duplicating the newline character around page breaks
    if context.inside_paragraph:
        context.suppress_newline = True
    else:
        context.suppress_newline = False

def print_newline():
    print_newlines(1)

def print_newlines(count):
    if context.suppress_newline:
        count -= 1
        context.suppress_newline = False

    context.print('\n' * count)

def sc_open(_elem):
    context.caps = True

def sc_close(_elem):
    context.caps = False

def tn_open(_elem):
    if context.mode in (Mode.TN_DEL, Mode.TN_INS):
        skip = Processing.SKIP_TAIL
    else:
        skip = None

    return skip

def del_open(_elem):
    if context.mode == Mode.TN_DEL:
        skip = None
    else:
        skip = Processing.SKIP_DATA

    return skip

def ins_open(_elem):
    if context.mode == Mode.TN_DEL:
        skip = Processing.SKIP_DATA
    else:
        skip = None

    return skip

def fn_open(elem):
    if context.mode == Mode.FOOTNOTES:
        context.suppress_paragraph = True
        print_newline()

        index = elem.get('index')
        data(f'[{index}] ')
        skip = Processing.SKIP_TAIL
    else:
        skip = Processing.SKIP_DATA

    return skip

def fn_close(_elem):
    if context.mode == Mode.FOOTNOTES:
        context.suppress_paragraph = False
        print_newline()

def anchor(elem):
    index = elem.get('index')
    context.print(f'[{index}]')

def sectionbreak_open(_elem):
    print_newline()

def tb(_elem):
    print_newline()
    context.print('       *' * 5)
    print_newline()

handlers = {
    'anchor':       (anchor, None ),
    'b':            (bold,   bold  ),
    'blockquote':   (blockquote_open, blockquote_close  ),
    'br':           (br,     None        ),
    'del':          (del_open,    None        ),
    'footnote':     (fn_open,     fn_close    ),
    'h1':           (h1_open,   h1_close  ),
    'head':         (None,      head_close  ),
    'headgroup':    (headgroup_open, headgroup_close ),
    'i':            (italic,   italic  ),
    'illustration': (ill_open,    ill_close   ),
    'ins':          (ins_open,    None   ),
    'nowrap':       (nowrap_open, nowrap_close ),
    'p':            (p_open,   p_close  ),
    'pb':           (pb_open,  None  ),
    'sc':           (sc_open,     sc_close    ),
    'sectionbreak': (sectionbreak_open, None ),
    'tb':           (tb,     None        ),
    'tn':           (tn_open,     None    ),
}

def write_footnotes(fn_list):
    print_newlines(4)
    context.print('Footnotes')
    print_newlines(2)

    for elem in fn_list:
        process.process(elem, handlers, data)

def write_transnote(tn_list):
    print_newlines(4)
    data('Transcriber’s Notes')
    print_newlines(3)
    data('This eBook makes the following corrections to the printed text:')
    print_newlines(2)

    context.set_nowrap(True)

    for elem in tn_list:
        data(elem.get('loc'))
        print_newline()

        data('  -')
        context.mode = Mode.TN_DEL
        process.process(elem, handlers, data)
        print_newline()

        data('  +')
        context.mode = Mode.TN_INS
        process.process(elem, handlers, data)
        print_newline()

context = Context()

def write_book(book, fn_list, tn_list):
    context.mode = Mode.NORMAL
    process.process(book, handlers, data)

    if fn_list:
        context.mode = Mode.FOOTNOTES
        write_footnotes(fn_list)

    if tn_list:
        write_transnote(tn_list)

    context.close()
