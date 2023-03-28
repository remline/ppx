"""
Test the syntax checker.
"""
import subprocess
import pytest

def build_generic_error(message):
    """Generate the error string that the syntax checker will output for the
    given message.
    """
    return f'line 1: {message}'

def build_sequence_error(sequence):
    """Generate the error string that the syntax checker will output for the
    given error sequence.
    """
    return build_generic_error(f'Bad sequence <{sequence}>')

def get_output(line):
    """Get the syntax checker's stderr output for the given input line."""
    # All tests are designed to work on a complete line
    line += '\n'
    result = subprocess.run('lex/syntax', input=line, encoding='utf-8',
                            stderr=subprocess.PIPE, check=False)
    return result.stderr.rstrip('\n')

@pytest.mark.parametrize('line, sequence', [
    ('Sentence one,continued', ',c'),
    ('Sentence one!Sentence two', '!S'),
    ('Sentence one?Sentence two', '?S'),
    ('Sentence one;continued', ';c'),
    ('Sentence one:continued', ':c'),
    ])
def test_unspaced_punctuation(line, sequence):
    """Missing a space between two sentences"""
    assert get_output(line) == build_sequence_error(sequence)

@pytest.mark.parametrize('line, sequence', [
    ('Sentence .', ' .'),
    ('Sentence ,', ' ,'),
    ('Sentence !', ' !'),
    ('Sentence ?', ' ?'),
    ('Sentence ;', ' ;'),
    ('Sentence :', ' :'),
    ])
def test_trailing_space(line, sequence):
    """Space after the end of the sentence before the punctuation mark"""
    assert get_output(line) == build_sequence_error(sequence)

@pytest.mark.parametrize('line, sequence', [
    ('two..', '..'),
    ('two,,', ',,'),
    ('two;;', ';;'),
    ('two::', '::'),
    ('Too many..... dots', '.....'),
    ('consecutive "" quote', ' ""'),
    ("consecutive '' quote", " ''"),
    ('""start of line', '""'),
    ("''start of line", "''"),
    ('end of line""', '""'),
    ("end of line''", "e''"),
    ('merged""quote', '""'),
    ("merged''quote", "d''"),
    ])
def test_duplicate_punctuation(line, sequence):
    """Duplicate punctuation marks."""
    assert get_output(line) == build_sequence_error(sequence)

@pytest.mark.parametrize('line, sequence', [
    ('quote " word', ' " '),
    ("quote ' word", " ' "),
    ('" start of line', '" '),
    ("' start of line", "' "),
    ('end of line "', ' "'),
    ("end of line '", " '"),
    ('“two lquotes“', 's“'),
    ('”two rquotes”', '”t'),
    ('Isn‘t correct apostrophe', 'n‘'),
    ])
def test_quote_problems(line, sequence):
    """Quotation marks in the wrong place."""
    assert get_output(line) == build_sequence_error(sequence)

@pytest.mark.parametrize('line, sequence', [
    ('[**proofing note]', '**'),
    ('[Illustration:Caption.]', ':C'),
    ])
def test_proofing_marks(line, sequence):
    """Problems with PGDP proofreading syntax."""
    assert get_output(line) == build_sequence_error(sequence)

@pytest.mark.parametrize('line, message', [
    (')', "Found ')' without '('"),
    ('([)', "Found ')' after '['"),
    ('[{]', "Found ']' after '{'"),
    ('"[quotes)"', "Found ')' after '['"),
    ('["quotes")', "Found ')' after '['"),
    ('{<}', "Found '}' after '<'"),
    ('<(>', "Found '>' after '('"),
    ])
def test_nesting(line, message):
    """Incorrectly nested brackets."""
    # These patterns also generate 'End of file' errors which we test separately.
    # So we only want to examine the first error.
    output = get_output(line)
    first_error = output.splitlines()[0]
    assert first_error == build_generic_error(message)

def test_nesting_eof():
    """Brackets left open at the end of file."""
    assert get_output('[[[]') == "End of file: Unclosed '['"

def test_end_of_line_space():
    """Trailing space at the end of a line."""
    assert get_output('End of line ') == build_generic_error('Trailing space')

@pytest.mark.parametrize('line', [
    'End punctuation. Next',
    'End punctuation, Next',
    'End punctuation; Next',
    'End punctuation: Next',
    'End punctuation! Next',
    'End punctuation? Next',
    'word space.',
    'word space,',
    'word space;',
    'word space:',
    'word space!',
    'word space?',
    'An ellipsis ... is fine.',
    'An ellipsis.... is fine.',
    'Floating point 3.14 number.',
    'Floating point 3,14 number.',
    'Time is 7:50 A.M.',
    'The U.S.A.',
    'Nesting [{[<<([([])])>>]}]',
    '[Illustration: Caption.]',
    '()',
    '[]',
    '{}',
    '<>',
    '<i>italics</i>',
    '<b>bold</b>',
    ])
def test_valid(line):
    """Valid syntax which should generate no error."""
    assert get_output(line) == ''