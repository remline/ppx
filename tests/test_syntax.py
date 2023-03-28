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
    result = subprocess.run('lex/punc', input=line, encoding='utf-8',
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
    ('end of line""\n', '""'),
    ("end of line''\n", "e''"),
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
    ('end of line "\n', ' "'),
    ("end of line '\n", " '"),
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
    assert get_output('End of line \n') == build_generic_error('Trailing space')
