"""
Test curly quote conversion.
"""
import subprocess
import pytest

def check_syntax(line):
    """Get the syntax checker's output for the given input line.
    Verify that the checker reports no error.
    """
    result = subprocess.run('lex/syntax', input=line, encoding='utf-8',
                            stdout=subprocess.PIPE, check=False)
    assert result.stdout == ''

def get_output(line):
    """Get standard output for the given input line."""
    # All tests are designed to work on a complete line
    line += '\n'
    result = subprocess.run('lex/quotes', input=line, encoding='utf-8',
                            stdout=subprocess.PIPE, check=False)
    check_syntax(line)
    return result.stdout.rstrip('\n')

@pytest.mark.parametrize('line, curly', [
    ('"Quote at start', '“Quote at start'),
    ("'Quote at start", '‘Quote at start'),
    ('quote at end"', 'quote at end”'),
    ("quote at end'", 'quote at end’'),
    ('Multiple "words" "quoted" "here"', 'Multiple “words” “quoted” “here”'),
    ("Multiple 'words' 'quoted' 'here'", 'Multiple ‘words’ ‘quoted’ ‘here’'),
    ('("Hmm...")', '(“Hmm...”)'),
    ('''Say "'American'".''', 'Say “‘American’”.'),
    ('''Say '"British"'.''', 'Say ‘“British”’.'),
    ('''"'American'"''', '“‘American’”'),
    ('''\'"British"\'''', '‘“British”’'),
    ('''Isn't James' car''', 'Isn’t James’ car'),
    ('''It's the 'best' we can 'do\'''', 'It’s the ‘best’ we can ‘do’'),
    ('''the "'best' we can 'do'", he said.''', 'the “‘best’ we can ‘do’”, he said.'),
    ("''Ere, young gen'l'men.'", '‘’Ere, young gen’l’men.’'),
    ("He said: ''Ere, young gen'l'men.'", 'He said: ‘’Ere, young gen’l’men.’'),
    ("'That's James'', he said", '‘That’s James’’, he said'),
    ])
def test_quote_conversion(line, curly):
    """Curly quote conversion."""
    assert get_output(line) == curly

@pytest.mark.parametrize('line', [
    '“word”',
    '‘word’',
    '“‘word’”',
    'That’s fine',
    ])
def test_curly_input(line):
    """Input curly quotes should be passed through unmodified."""
    assert get_output(line) == line

@pytest.mark.parametrize('line, curly', [
    ("θπ'ς", 'θπ’ς'),
    ('greek "αβγ" means', 'greek “αβγ” means'),
    ("greek 'αβγ' means", 'greek ‘αβγ’ means'),
    ])
def test_unicode(line, curly):
    """Unicode input."""
    assert get_output(line) == curly

@pytest.mark.parametrize('line, curly', [
    ('[Illustration: "Lively."]', '[Illustration: “Lively.”]'),
    ('("what")', '(“what”)'),
    ('yes"!', 'yes”!'),
    ('really"?', 'really”?'),
    ('yes";', 'yes”;'),
    ('yes;" and', 'yes;” and'),
    ('yes":', 'yes”:'),
    ('yes:" and', 'yes:” and'),
    ('["noted"]', '[“noted”]'),
    ('well "[as if]" it', 'well “[as if]” it'),
    ('doors--"The Holy Doors"--that', 'doors--“The Holy Doors”--that'),
    ('sentence." Then,', 'sentence.” Then,'),
    ('word". Although', 'word”. Although'),
    ('continue," he said.', 'continue,” he said.'),
    ('yes", indeed', 'yes”, indeed'),
    ("('what')", '(‘what’)'),
    ("yes'!", 'yes’!'),
    ("really'?", 'really’?'),
    ("yes';", 'yes’;'),
    ("yes;' and", 'yes;’ and'),
    ("yes':", 'yes’:'),
    ("yes:' and", 'yes:’ and'),
    ("['noted']", '[‘noted’]'),
    ("well '[as if]' it", 'well ‘[as if]’ it'),
    ("doors--'The Holy Doors'--that", 'doors--‘The Holy Doors’--that'),
    ("sentence.' Then,", 'sentence.’ Then,'),
    ("word'. Although", 'word’. Although'),
    ("continue,' he said.", 'continue,’ he said.'),
    ("yes', indeed", 'yes’, indeed'),
    ('"well I--" ...', '“well I--” ...'),
    ("'well I--' ...", '‘well I--’ ...'),
    ('"a little"--these are his own words--"about', '“a little”--these are his own words--“about'),
    ('"<i>And ... away.</i>"--Source.', '“<i>And ... away.</i>”--Source.'),
    ('"What reforms?"--what unprecedented...', '“What reforms?”--what unprecedented...'),
    ('the apse--"<i>Nunc rutilat ...</i>"', 'the apse--“<i>Nunc rutilat ...</i>”'),
    ])
def test_punctuation(line, curly):
    """Quotation marks next to punctuation."""
    assert get_output(line) == curly

@pytest.mark.parametrize('line, curly', [
    ("'Em is an apostrophe", '’Em is an apostrophe'),
    ("'Em 'gainst 'tis 'twas 'TWERE 'twould", '’Em ’gainst ’tis ’twas ’TWERE ’twould'),
    ("said, ‘'Em was rough'’", 'said, ‘’Em was rough’’'),
    ])
def test_contractions(line, curly):
    """Contractions should yield apostrophes."""
    assert get_output(line) == curly
