"""Write HTML format"""
# pylint: disable=missing-function-docstring

import sys
import process

from share import Mode, Processing

class Context:
    """Context manager"""
    def __init__(self):
        self.file = None
        self.mode = None
        self.tag_stack = []

    def open(self):
        # pylint: disable=consider-using-with
        self.file = open('out.html', mode='w', encoding='utf-8')

    def close(self):
        self.file.close()

        assert len(self.tag_stack) == 0

    def print(self, string):
        self.file.write(string)

def start(tag, attributes=None, newline=False):
    context.tag_stack.append(tag)

    if newline:
        context.print('\n')

    if attributes:
        context.print(f'<{tag} {attributes}>')
    else:
        context.print(f'<{tag}>')

def end(tag, newline=False):
    match = context.tag_stack.pop()
    assert tag == match

    if newline:
        context.print('\n')

    context.print(f'</{tag}>')

def empty(tag, attributes=None, newline=False):
    if newline:
        context.print('\n')

    if attributes:
        context.print(f'<{tag} {attributes}>')
    else:
        context.print(f'<{tag}>')

def data(text):
    # prevent & from escaping the next HTML character
    text = text.replace('&','&amp;')

    # replace 4 hyphens with two-em dash, and 2 hyphens with em dash
    text = text.replace('----', '\u2e3a')
    text = text.replace('--',   '\u2014')

    context.print(text)

def blockquote_open(_elem):
    start('div', 'class="blockquot"', newline=True)

def blockquote_close(_elem):
    end('div')

def book_open(elem):
    title = elem.find('title')

    if title is None:
        print('Missing title element', file=sys.stderr)
        sys.exit()

    full_title = f'{title.text} | Project Gutenberg'
    elem.remove(title)

    context.print('<!DOCTYPE html>')
    start('html', 'lang="en"', newline=True)
    start('head', newline=True)

    empty('meta', 'charset="UTF-8"', True)

    start('title', newline=True)
    data(full_title)
    end('title')

    empty('link', 'rel="icon" href="images/cover.jpg" type="image/x-cover"', True)
    start('style', newline=True)

    with open('style.css', encoding='utf-8') as css:
        style = css.read()
        context.print('\n')
        context.print(style)

    end('style')
    end('head', newline=True)
    start('body', newline=True)

def br_open(_elem):
    empty('br')

def head_open(_elem):
    start('h2', 'class="nobreak"')

def head_close(_elem):
    end('h2')

def headgroup_open(_elem):
    start('div', 'class="chapter"')

def headgroup_close(_elem):
    end('div')

def ill_open(elem):
    src = elem.get('src')

    start('figure')
    empty('img', f'src="{src}" alt=""')

    if len(elem):
        start('figcaption')

def ill_close(elem):
    if len(elem):
        end('figcaption')

    end('figure')

def nowrap_open(_elem):
    start('div', 'class="nowrap"')

def nowrap_close(_elem):
    end('div')

def pb_open(elem):
    page_number = elem.get('n')

    if page_number:
        start('a', f'id="Page_{page_number}"')
        end('a')

def sc_open(elem):
    # Is the child text all upper case?
    text = ''
    for child in elem.iter():
        if child.text:
            text += child.text

        if child.tail:
            text += child.tail

    if text.isupper():
        span_class = 'allsmcap'
    else:
        span_class = 'smcap'

    start('span', f'class="{span_class}"')

def sc_close(_elem):
    end('span')

def dflt_open(elem):
    attr = elem.items()

    if attr:
        a = attr[0]
        start(elem.tag, f'{a[0]}="{a[1]}"')
    else:
        start(elem.tag)

def dflt_close(elem):
    end(elem.tag)

def tn_open(elem):
    skip = None

    if context.mode in (Mode.NORMAL, Mode.FOOTNOTES):
        # Add an anchor for this correction
        index = elem.get('index')
        start('a', f'id="corr{index}"')
    elif context.mode in (Mode.TN_DEL, Mode.TN_INS):
        start('li', newline=True)
        skip = Processing.SKIP_TAIL

    return skip

def tn_close(_elem):
    if context.mode in (Mode.NORMAL, Mode.FOOTNOTES):
        end('a')
    elif context.mode in (Mode.TN_DEL, Mode.TN_INS):
        end('li')

def del_open(_elem):
    if context.mode == Mode.TN_DEL:
        start('del')
        skip = None
    else:
        skip = Processing.SKIP_DATA

    return skip

def del_close(_elem):
    if context.mode == Mode.TN_DEL:
        end('del')

def ins_open(_elem):
    skip = None

    if context.mode == Mode.TN_INS:
        start('ins')
    elif context.mode == Mode.TN_DEL:
        skip = Processing.SKIP_DATA

    return skip

def ins_close(_elem):
    if context.mode == Mode.TN_INS:
        end('ins')

def fn_open(elem):
    if context.mode == Mode.FOOTNOTES:
        index = elem.get('index')
        start('div', newline=True)
        start('a', f'id="Footnote_{index}" href="#FNanchor_{index}"')
        data(f'[{index}]')
        end('a')
        skip = Processing.SKIP_TAIL
    else:
        skip = Processing.SKIP_DATA

    return skip

def fn_close(_elem):
    if context.mode == Mode.FOOTNOTES:
        end('div')

def anchor_open(elem):
    index = elem.get('index')
    start('a', f'id="FNanchor_{index}" href="#Footnote_{index}" class="fnanchor"')
    data(f'[{index}]')

def anchor_close(_elem):
    end('a')

def sectionbreak_open(_elem):
    start('div', 'class="section-break"', newline=True)

def sectionbreak_close(_elem):
    end('div')

def tb_open(_elem):
    empty('hr')

handlers = {
    'anchor':       (anchor_open, anchor_close),
    'b':            (dflt_open,   dflt_close  ),
    'blockquote':   (blockquote_open, blockquote_close  ),
    'book':         (book_open,   None        ),
    'br':           (br_open,     None        ),
    'del':          (del_open,    del_close   ),
    'div':          (dflt_open,   dflt_close  ),
    'footnote':     (fn_open,     fn_close    ),
    'h1':           (dflt_open,   dflt_close  ),
    'head':         (head_open,   head_close  ),
    'headgroup':    (headgroup_open, headgroup_close ),
    'i':            (dflt_open,   dflt_close  ),
    'illustration': (ill_open,    ill_close   ),
    'ins':          (ins_open,    ins_close   ),
    'nowrap':       (nowrap_open, nowrap_close ),
    'p':            (dflt_open,   dflt_close  ),
    'pb':           (pb_open,     None        ),
    'sc':           (sc_open,     sc_close    ),
    'sectionbreak': (sectionbreak_open, sectionbreak_close ),
    'span':         (dflt_open,   dflt_close  ),
    'tb':           (tb_open,     None        ),
    'tn':           (tn_open,     tn_close    ),
}

def write_footnotes(fn_list):
    start('div', 'id="footnotes"', newline=True)
    start('h2', 'class="nobreak"', newline=True)
    data('Footnotes')
    end('h2')

    for elem in fn_list:
        process.process(elem, handlers, data)

    end('div')

def write_transnote(tn_list):
    start('div', 'id="transnote"', newline=True)
    start('h2', 'class="nobreak"', newline=True)
    data('Transcriber’s Notes')
    end('h2')
    start('p', newline=True)
    data('This eBook makes the following corrections to the printed text:')
    end('p')
    start('ul', newline=True)

    for elem in tn_list:
        # Link to the correction anchor
        start('li', newline=True)
        index = elem.get('index')
        start('a', f'href="#corr{index}"')
        data(elem.get('loc'))
        end('a')
        start('ul')

        context.mode = Mode.TN_DEL
        process.process(elem, handlers, data)

        context.mode = Mode.TN_INS
        process.process(elem, handlers, data)

        end('ul')
        end('li')

    end('ul')
    end('div')

context = Context()

def write_book(book, fn_list, tn_list):
    context.open()

    context.mode = Mode.NORMAL
    process.process(book, handlers, data)

    if fn_list:
        context.mode = Mode.FOOTNOTES
        write_footnotes(fn_list)

    if tn_list:
        write_transnote(tn_list)

    end('body', newline=True)
    end('html', newline=True)

    context.print('\n')
    context.close()
