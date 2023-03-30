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
    ("Isn't James' car", 'Isn’t James’ car'),
    ("It's 'okay' and 'fine'", 'It’s ‘okay’ and ‘fine’'),
    ("''Ere, young gen'l'men.'", '‘’Ere, young gen’l’men.’'),
    ("He said: ''Ere, young gen'l'men.'", 'He said: ‘’Ere, young gen’l’men.’'),
    ("'That's James'', he said", '‘That’s James’’, he said'),
    ])
def test_quote_conversion(line, curly):
    """Curly quote conversion."""
    assert get_output(line) == curly

@pytest.mark.parametrize('line, curly', [
    ('''Say "'American'".''', 'Say “‘American’”.'),
    ('''Say '"British"'.''', 'Say ‘“British”’.'),
    ('''"'American'"''', '“‘American’”'),
    ("""'"British"'""", '‘“British”’'),
    ('''said "'we' are 'okay'"?''', 'said “‘we’ are ‘okay’”?'),
    ('''"I'm fine."''', '“I’m fine.”'),
    ('''said "I'm fine."''', 'said “I’m fine.”'),
    ])
def test_combinations(line, curly):
    """Combinations of single and double quotes."""
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
    ("sentence.' Then,", 'sentence.’ Then,'),
    ("word'. Although", 'word’. Although'),
    ("continue,' he said.", 'continue,’ he said.'),
    ("yes', indeed", 'yes’, indeed'),
    ])
def test_punctuation(line, curly):
    """Quotation marks next to punctuation."""
    assert get_output(line) == curly

@pytest.mark.parametrize('line, curly', [
    ('doors--"The Holy Doors"--that', 'doors--“The Holy Doors”--that'),
    ("doors--'The Holy Doors'--that", 'doors--‘The Holy Doors’--that'),
    ('"well I--"', '“well I--”'),
    ("'well I--'", '‘well I--’'),
    ('"well I--" ...', '“well I--” ...'),
    ("'well I--' ...", '‘well I--’ ...'),
    ('"But"--she looked--"I am!"', '“But”--she looked--“I am!”'),
    ("'But'--she looked--'I am!'", '‘But’--she looked--‘I am!’'),
    ('"<i>And ... away.</i>"--Source.', '“<i>And ... away.</i>”--Source.'),
    ('"What reforms?"--what unprecedented', '“What reforms?”--what unprecedented'),
    ('the apse--"<i>Nunc rutilat ...</i>"', 'the apse--“<i>Nunc rutilat ...</i>”'),
    ])
def test_em_dashes_ascii(line, curly):
    """Quotation marks next to ASCII em dashes."""
    assert get_output(line) == curly

@pytest.mark.parametrize('line, curly', [
    ('doors—"The Holy Doors"—that', 'doors—“The Holy Doors”—that'),
    ("doors—'The Holy Doors'—that", 'doors—‘The Holy Doors’—that'),
    ('"well I—"', '“well I—”'),
    ("'well I—'", '‘well I—’'),
    ('"well I—" ...', '“well I—” ...'),
    ("'well I—' ...", '‘well I—’ ...'),
    ('"But"—she looked—"I am!"', '“But”—she looked—“I am!”'),
    ("'But'—she looked—'I am!'", '‘But’—she looked—‘I am!’'),
    ('"<i>And ... away.</i>"—Source.', '“<i>And ... away.</i>”—Source.'),
    ('"What reforms?"—what unprecedented', '“What reforms?”—what unprecedented'),
    ('the apse—"<i>Nunc rutilat ...</i>"', 'the apse—“<i>Nunc rutilat ...</i>”'),
    ])
def test_em_dashes_unicode(line, curly):
    """Quotation marks next to Unicode em dashes."""
    assert get_output(line) == curly

@pytest.mark.parametrize('line, curly', [
    ("'Em is an apostrophe", '’Em is an apostrophe'),
    ("'Em 'gainst 'tis 'twas 'TWERE 'twould", '’Em ’gainst ’tis ’twas ’TWERE ’twould'),
    ("said, ‘'Em was rough'’", 'said, ‘’Em was rough’’'),
    ])
def test_contractions(line, curly):
    """Contractions should yield apostrophes."""
    assert get_output(line) == curly

@pytest.mark.parametrize('line, curly', [
    ("“'abc'” or “'xyz'”", '“‘abc’” or “‘xyz’”'),
    ('"‘abc’" or "‘xyz’"', '“‘abc’” or “‘xyz’”'),
    ("'“abc”' or '“xyz”'", '‘“abc”’ or ‘“xyz”’'),
    ('‘"abc"’ or ‘"xyz"’', '‘“abc”’ or ‘“xyz”’'),
    ])
def test_partials(line, curly):
    """The input has been partially manually converted to curly quotes.
    Ensure the remaining straight quotes are converted.
    """
    assert get_output(line) == curly
