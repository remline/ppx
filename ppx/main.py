#!/usr/bin/python

"""Generate HTML and Text books from an XML book."""

import glob
import xml.etree.ElementTree as ET

import html
import text

def number_pages(book):
    """Set page numbers relative to the explicitly defined page breaks"""
    page = None

    for elem in book.iter():
        if elem.tag == 'pb':
            n = elem.get('n')

            if n:
                page = int(n)
            elif page:
                page += 1
                elem.set('n', page)

        elif elem.tag == 'tn':
            elem.set('loc', f'Page {page}')

def number_fns(fn_list, anchor_list):
    """Set footnote numbers from 1 to n"""
    assert(len(fn_list) == len(anchor_list))

    for i, fn in enumerate(fn_list):
        fn.set('index', i + 1)

    for i, anchor in enumerate(anchor_list):
        anchor.set('index', i + 1)

def number_tns(tn_list):
    """Set transcriber's note numbers from 1 to n"""
    index = 1

    for elem in tn_list:
        elem.set('index', index)
        index += 1

def source_images(book):
    """Assign file names to the illustration XML tags"""
    illustrations = book.findall('.//illustration')
    files = glob.glob('images/*')
    files.sort()

    for i, ill in enumerate(illustrations):
        ill.set('src', files[i])

def parse_book():
    """Parse the XML book into Python data structures"""
    #tree = ET.parse(sys.stdin)
    tree = ET.parse('x.xml')
    book = tree.getroot()
    number_pages(book)

    fn_list = book.findall('.//footnote')
    anchor_list = book.findall('.//anchor')
    number_fns(fn_list, anchor_list)

    tn_list = book.findall('.//tn')
    number_tns(tn_list)

    source_images(book)
    return book, fn_list, tn_list

def main():
    """Generate the two book formats"""
    book, fn_list, tn_list = parse_book()
    html.write_book(book, fn_list, tn_list)
    text.write_book(book, fn_list, tn_list)

main()
