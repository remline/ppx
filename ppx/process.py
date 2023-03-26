"""XML processor"""

from share import Processing

def process(elem, handlers, write_data):
    """Process XML tags and data"""
    try:
        open_handler  = handlers[elem.tag][0]
        close_handler = handlers[elem.tag][1]
    except KeyError:
        open_handler = None
        close_handler = None

    if open_handler:
        skip = open_handler(elem)
    else:
        skip = None

    if skip != Processing.SKIP_DATA:
        if elem.text:
            write_data(elem.text)

        for child in elem:
            process(child, handlers, write_data)

    if close_handler:
        close_handler(elem)

    if skip != Processing.SKIP_TAIL:
        if elem.tail:
            write_data(elem.tail)
