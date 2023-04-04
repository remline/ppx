"""
Test curly quote conversion.
"""
import subprocess
import pytest

def check_syntax(line):
    """Get the syntax checker's output for the given input line.
    Verify that the checker reports no error.
    """
    line = f'{line}\n'
    result = subprocess.run('lex/syntax', input=line, encoding='utf-8',
                            stdout=subprocess.PIPE, check=False)
    assert result.stdout == ''

def get_output(line):
    """Get standard output for the given input line."""
    line = f'{line}\n'
    result = subprocess.run('lex/quotes', input=line, encoding='utf-8',
                            stdout=subprocess.PIPE, check=False)
    return result.stdout.rstrip('\n')

def verify(line, expect):
    """Verify that the input line converts to the expected output."""
    # The output should match as a complete line
    assert get_output(line) == expect

    # The output should match as part of a line, so surround with spaces
    assert get_output(f' {line} ') == f' {expect} '

    # The output should match when surrounded by parentheses
    assert get_output(f'({line})') == f'({expect})'

    # The syntax checker should be happy, too
    check_syntax(line)

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
    ("said: ''Ere, young gen'l'men.'", 'said: ‘’Ere, young gen’l’men.’'),
    ("'That's James'', he said", '‘That’s James’’, he said'),
    ('"a" or "b" "c"', '“a” or “b” “c”'),
    ("'a' or 'b' 'c'", '‘a’ or ‘b’ ‘c’'),
    ])
def test_quote_conversion(line, curly):
    """Curly quote conversion."""
    verify(line, curly)

@pytest.mark.parametrize('line, curly', [
    ('''Say "'American'".''', 'Say “‘American’”.'),
    ('''Say '"British"'.''', 'Say ‘“British”’.'),
    ('''"'American'"''', '“‘American’”'),
    ("""'"British"'""", '‘“British”’'),
    ('''said "'we' are 'okay'"?''', 'said “‘we’ are ‘okay’”?'),
    ('''"'okay'?"''', '“‘okay’?”'),
    ('''"I'm fine."''', '“I’m fine.”'),
    ('''said "I'm fine."''', 'said “I’m fine.”'),
    ])
def test_combinations(line, curly):
    """Combinations of single and double quotes."""
    verify(line, curly)

@pytest.mark.parametrize('line', [
    '“word”',
    '‘word’',
    '“‘word’”',
    'That’s fine',
    ])
def test_curly_input(line):
    """Input curly quotes should be passed through unmodified."""
    verify(line, line)

@pytest.mark.parametrize('line, curly', [
    ("θπ'ς", 'θπ’ς'),
    ('greek "αβγ" means', 'greek “αβγ” means'),
    ("greek 'αβγ' means", 'greek ‘αβγ’ means'),
    ])
def test_unicode(line, curly):
    """Unicode input."""
    verify(line, curly)

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
    ('{"noted"}', '{“noted”}'),
    ("['noted']", '[‘noted’]'),
    ("('noted')", '(‘noted’)'),
    ('well "[as if]" it', 'well “[as if]” it'),
    ('sentence." Then,', 'sentence.” Then,'),
    ('word". Although', 'word”. Although'),
    ('continue," he said.', 'continue,” he said.'),
    ('yes", indeed', 'yes”, indeed'),
    ("yes'!", 'yes’!'),
    ("really'?", 'really’?'),
    ("yes';", 'yes’;'),
    ("yes;' and", 'yes;’ and'),
    ("yes':", 'yes’:'),
    ("yes:' and", 'yes:’ and'),
    ("well '[as if]' it", 'well ‘[as if]’ it'),
    ("sentence.' Then,", 'sentence.’ Then,'),
    ("word'. Although", 'word’. Although'),
    ("continue,' he said.", 'continue,’ he said.'),
    ("yes', indeed", 'yes’, indeed'),
    ("Nor'-Westers", 'Nor’-Westers'),
    ("will-o'-the-wisp", 'will-o’-the-wisp'),
    ("'but'-ing and 'and'-ing", '‘but’-ing and ‘and’-ing'),
    ])
def test_punctuation(line, curly):
    """Quotation marks next to punctuation."""
    verify(line, curly)

@pytest.mark.parametrize('line, curly', [
    ('footnote."[5]', 'footnote.”[5]'),
    ("footnote.'[5]", 'footnote.’[5]'),
    ])
def test_footnotes(line, curly):
    """Quotation marks next to footnotes."""
    verify(line, curly)

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
    ('''"Ky's so--"--she paused--"tired."''', '“Ky’s so--”--she paused--“tired.”'),
    ("""'Was too--'--she paused--'tired.'""", '‘Was too--’--she paused--‘tired.’'),
    ('''"Is: 'medicus quisquam--'"''', '“Is: ‘medicus quisquam--’”'),
    ("no matter--'tis but resting", 'no matter--’tis but resting'),
    ('["I--"]', '[“I--”]'),
    ("'Quote.'--Source.", '‘Quote.’--Source.'),
    ])
def test_em_dashes(line, curly):
    """Quotation marks next to em dashes."""
    # Test ASCII em dashes
    verify(line, curly)

    # Test Unicode em dashes
    line = line.replace('--','—')
    curly = curly.replace('--','—')
    verify(line, curly)

@pytest.mark.parametrize('line, curly', [
    ("'Em is an apostrophe", '’Em is an apostrophe'),
    ("'Em 'gainst 'tis 'twas 'TWERE 'twould", '’Em ’gainst ’tis ’twas ’TWERE ’twould'),
    ("'tisn't 'twasn't 'tweren't 'twouldn't", '’tisn’t ’twasn’t ’tweren’t ’twouldn’t'),
    ("'twon't", '’twon’t'),
    ("'undred 'undreds 'undredth", '’undred ’undreds ’undredth'),
    ("'ead 'Eads 'Eadbald 'er 'ers", '’ead ’Eads ‘Eadbald ’er ‘ers'),
    ("said, ‘'Em was rough'’", 'said, ‘’Em was rough’’'),
    ("<sc>'gainst", '<sc>’gainst'),
    ("--'twas", '--’twas'),
    ("['twere]", '[’twere]'),
    ("“'twould", '“’twould'),
    ("'emit a full word'", '‘emit a full word’'),
    ('''"'Tis that...''', '“’Tis that...'),
    ('''said, "'Tis that...''', 'said, “’Tis that...'),
    ('''"'twas nothin'--"--he''', '“’twas nothin’--”--he'),
    ('''"''t''', '“‘’t'),
    ('''"''im''', '“‘’im'),
    ('''"get 'im"''', '“get ’im”'),
    ('''"'im"''', '“’im”'),
    ])
def test_contractions(line, curly):
    """Contractions should yield apostrophes."""
    verify(line, curly)

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
    verify(line, curly)

@pytest.mark.parametrize('line, curly', [
    ('a <b>"bold"</b> tag', 'a <b>“bold”</b> tag'),
    ("a <b>'bold'</b> tag", 'a <b>‘bold’</b> tag'),
    ('a "<b>bold</b>" tag', 'a “<b>bold</b>” tag'),
    ("a '<b>bold</b>' tag", 'a ‘<b>bold</b>’ tag'),
    ('"<div>word</div>"', '“<div>word</div>”'),
    ("'<div>word</div>'", '‘<div>word</div>’'),
    ])
def test_tags(line, curly):
    """HTML-like tags."""
    verify(line, curly)
