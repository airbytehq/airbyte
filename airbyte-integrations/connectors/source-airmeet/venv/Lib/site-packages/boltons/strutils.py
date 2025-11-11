# Copyright (c) 2013, Mahmoud Hashemi
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#
#    * Redistributions in binary form must reproduce the above
#      copyright notice, this list of conditions and the following
#      disclaimer in the documentation and/or other materials provided
#      with the distribution.
#
#    * The names of the contributors may not be used to endorse or
#      promote products derived from this software without specific
#      prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""So much practical programming involves string manipulation, which
Python readily accommodates. Still, there are dozens of basic and
common capabilities missing from the standard library, several of them
provided by ``strutils``.
"""


import builtins
import re
import sys
import uuid
import zlib
import string
import unicodedata
import collections
from collections.abc import Mapping
from gzip import GzipFile
from html.parser import HTMLParser
from html import entities as htmlentitydefs
from io import BytesIO as StringIO


__all__ = ['camel2under', 'under2camel', 'slugify', 'split_punct_ws',
           'unit_len', 'ordinalize', 'cardinalize', 'pluralize', 'singularize',
           'asciify', 'is_ascii', 'is_uuid', 'html2text', 'strip_ansi',
           'bytes2human', 'find_hashtags', 'a10n', 'gzip_bytes', 'gunzip_bytes',
           'iter_splitlines', 'indent', 'escape_shell_args',
           'args2cmd', 'args2sh', 'parse_int_list', 'format_int_list',
           'complement_int_list', 'int_ranges_from_int_list', 'MultiReplace',
           'multi_replace', 'unwrap_text', 'removeprefix']


_punct_ws_str = string.punctuation + string.whitespace
_punct_re = re.compile('[' + _punct_ws_str + ']+')
_camel2under_re = re.compile('((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))')


def camel2under(camel_string):
    """Converts a camelcased string to underscores. Useful for turning a
    class name into a function name.

    >>> camel2under('BasicParseTest')
    'basic_parse_test'
    """
    return _camel2under_re.sub(r'_\1', camel_string).lower()


def under2camel(under_string):
    """Converts an underscored string to camelcased. Useful for turning a
    function name into a class name.

    >>> under2camel('complex_tokenizer')
    'ComplexTokenizer'
    """
    return ''.join(w.capitalize() or '_' for w in under_string.split('_'))


def slugify(text, delim='_', lower=True, ascii=False):
    """
    A basic function that turns text full of scary characters
    (i.e., punctuation and whitespace), into a relatively safe
    lowercased string separated only by the delimiter specified
    by *delim*, which defaults to ``_``.

    The *ascii* convenience flag will :func:`asciify` the slug if
    you require ascii-only slugs.

    >>> slugify('First post! Hi!!!!~1    ')
    'first_post_hi_1'

    >>> slugify("Kurt Gödel's pretty cool.", ascii=True) == \
        b'kurt_goedel_s_pretty_cool'
    True

    """
    ret = delim.join(split_punct_ws(text)) or delim if text else ''
    if ascii:
        ret = asciify(ret)
    if lower:
        ret = ret.lower()
    return ret


def split_punct_ws(text):
    """While :meth:`str.split` will split on whitespace,
    :func:`split_punct_ws` will split on punctuation and
    whitespace. This used internally by :func:`slugify`, above.

    >>> split_punct_ws('First post! Hi!!!!~1    ')
    ['First', 'post', 'Hi', '1']
    """
    return [w for w in _punct_re.split(text) if w]


def unit_len(sized_iterable, unit_noun='item'):  # TODO: len_units()/unitize()?
    """Returns a plain-English description of an iterable's
    :func:`len()`, conditionally pluralized with :func:`cardinalize`,
    detailed below.

    >>> print(unit_len(range(10), 'number'))
    10 numbers
    >>> print(unit_len('aeiou', 'vowel'))
    5 vowels
    >>> print(unit_len([], 'worry'))
    No worries
    """
    count = len(sized_iterable)
    units = cardinalize(unit_noun, count)
    if count:
        return f'{count} {units}'
    return f'No {units}'


_ORDINAL_MAP = {'1': 'st',
                '2': 'nd',
                '3': 'rd'}  # 'th' is the default


def ordinalize(number, ext_only=False):
    """Turns *number* into its cardinal form, i.e., 1st, 2nd,
    3rd, 4th, etc. If the last character isn't a digit, it returns the
    string value unchanged.

    Args:
        number (int or str): Number to be cardinalized.
        ext_only (bool): Whether to return only the suffix. Default ``False``.

    >>> print(ordinalize(1))
    1st
    >>> print(ordinalize(3694839230))
    3694839230th
    >>> print(ordinalize('hi'))
    hi
    >>> print(ordinalize(1515))
    1515th
    """
    numstr, ext = str(number), ''
    if numstr and numstr[-1] in string.digits:
        try:
            # first check for teens
            if numstr[-2] == '1':
                ext = 'th'
            else:
                # all other cases
                ext = _ORDINAL_MAP.get(numstr[-1], 'th')
        except IndexError:
            # single digit numbers (will reach here based on [-2] above)
            ext = _ORDINAL_MAP.get(numstr[-1], 'th')
    if ext_only:
        return ext
    else:
        return numstr + ext


def cardinalize(unit_noun, count):
    """Conditionally pluralizes a singular word *unit_noun* if
    *count* is not one, preserving case when possible.

    >>> vowels = 'aeiou'
    >>> print(len(vowels), cardinalize('vowel', len(vowels)))
    5 vowels
    >>> print(3, cardinalize('Wish', 3))
    3 Wishes
    """
    if count == 1:
        return unit_noun
    return pluralize(unit_noun)


def singularize(word):
    """Semi-intelligently converts an English plural *word* to its
    singular form, preserving case pattern.

    >>> singularize('chances')
    'chance'
    >>> singularize('Activities')
    'Activity'
    >>> singularize('Glasses')
    'Glass'
    >>> singularize('FEET')
    'FOOT'

    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_S2P:
        return orig_word

    irr_singular = _IRR_P2S.get(word)
    if irr_singular:
        singular = irr_singular
    elif not word.endswith('s'):
        return orig_word
    elif len(word) == 2:
        singular = word[:-1]  # or just return word?
    elif word.endswith('ies') and word[-4:-3] not in 'aeiou':
        singular = word[:-3] + 'y'
    elif word.endswith('es') and word[-3] == 's':
        singular = word[:-2]
    else:
        singular = word[:-1]
    return _match_case(orig_word, singular)


def pluralize(word):
    """Semi-intelligently converts an English *word* from singular form to
    plural, preserving case pattern.

    >>> pluralize('friend')
    'friends'
    >>> pluralize('enemy')
    'enemies'
    >>> pluralize('Sheep')
    'Sheep'
    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_P2S:
        return orig_word
    irr_plural = _IRR_S2P.get(word)
    if irr_plural:
        plural = irr_plural
    elif word.endswith('y') and word[-2:-1] not in 'aeiou':
        plural = word[:-1] + 'ies'
    elif word[-1] == 's' or word.endswith('ch') or word.endswith('sh'):
        plural = word if word.endswith('es') else word + 'es'
    else:
        plural = word + 's'
    return _match_case(orig_word, plural)


def _match_case(master, disciple):
    if not master.strip():
        return disciple
    if master.lower() == master:
        return disciple.lower()
    elif master.upper() == master:
        return disciple.upper()
    elif master.title() == master:
        return disciple.title()
    return disciple


# Singular to plural map of irregular pluralizations
_IRR_S2P = {'addendum': 'addenda', 'alga': 'algae', 'alumna': 'alumnae',
            'alumnus': 'alumni', 'analysis': 'analyses', 'antenna': 'antennae',
            'appendix': 'appendices', 'axis': 'axes', 'bacillus': 'bacilli',
            'bacterium': 'bacteria', 'basis': 'bases', 'beau': 'beaux',
            'bison': 'bison', 'bureau': 'bureaus', 'cactus': 'cacti',
            'calf': 'calves', 'child': 'children', 'corps': 'corps',
            'corpus': 'corpora', 'crisis': 'crises', 'criterion': 'criteria',
            'curriculum': 'curricula', 'datum': 'data', 'deer': 'deer',
            'diagnosis': 'diagnoses', 'die': 'dice', 'dwarf': 'dwarves',
            'echo': 'echoes', 'elf': 'elves', 'ellipsis': 'ellipses',
            'embargo': 'embargoes', 'emphasis': 'emphases', 'erratum': 'errata',
            'fireman': 'firemen', 'fish': 'fish', 'focus': 'foci',
            'foot': 'feet', 'formula': 'formulae', 'formula': 'formulas',
            'fungus': 'fungi', 'genus': 'genera', 'goose': 'geese',
            'half': 'halves', 'hero': 'heroes', 'hippopotamus': 'hippopotami',
            'hoof': 'hooves', 'hypothesis': 'hypotheses', 'index': 'indices',
            'knife': 'knives', 'leaf': 'leaves', 'life': 'lives',
            'loaf': 'loaves', 'louse': 'lice', 'man': 'men',
            'matrix': 'matrices', 'means': 'means', 'medium': 'media',
            'memorandum': 'memoranda', 'millennium': 'milennia', 'moose': 'moose',
            'mosquito': 'mosquitoes', 'mouse': 'mice', 'nebula': 'nebulae',
            'neurosis': 'neuroses', 'nucleus': 'nuclei', 'oasis': 'oases',
            'octopus': 'octopi', 'offspring': 'offspring', 'ovum': 'ova',
            'ox': 'oxen', 'paralysis': 'paralyses', 'parenthesis': 'parentheses',
            'person': 'people', 'phenomenon': 'phenomena', 'potato': 'potatoes',
            'radius': 'radii', 'scarf': 'scarves', 'scissors': 'scissors',
            'self': 'selves', 'sense': 'senses', 'series': 'series', 'sheep':
            'sheep', 'shelf': 'shelves', 'species': 'species', 'stimulus':
            'stimuli', 'stratum': 'strata', 'syllabus': 'syllabi', 'symposium':
            'symposia', 'synopsis': 'synopses', 'synthesis': 'syntheses',
            'tableau': 'tableaux', 'that': 'those', 'thesis': 'theses',
            'thief': 'thieves', 'this': 'these', 'tomato': 'tomatoes', 'tooth':
            'teeth', 'torpedo': 'torpedoes', 'vertebra': 'vertebrae', 'veto':
            'vetoes', 'vita': 'vitae', 'watch': 'watches', 'wife': 'wives',
            'wolf': 'wolves', 'woman': 'women'}


# Reverse index of the above
_IRR_P2S = {v: k for k, v in _IRR_S2P.items()}

HASHTAG_RE = re.compile(r"(?:^|\s)[＃#]{1}(\w+)", re.UNICODE)


def find_hashtags(string):
    """Finds and returns all hashtags in a string, with the hashmark
    removed. Supports full-width hashmarks for Asian languages and
    does not false-positive on URL anchors.

    >>> find_hashtags('#atag http://asite/#ananchor')
    ['atag']

    ``find_hashtags`` also works with unicode hashtags.
    """

    # the following works, doctest just struggles with it
    # >>> find_hashtags(u"can't get enough of that dignity chicken #肯德基 woo")
    # [u'\u80af\u5fb7\u57fa']
    return HASHTAG_RE.findall(string)


def a10n(string):
    """That thing where "internationalization" becomes "i18n", what's it
    called? Abbreviation? Oh wait, no: ``a10n``. (It's actually a form
    of `numeronym`_.)

    >>> a10n('abbreviation')
    'a10n'
    >>> a10n('internationalization')
    'i18n'
    >>> a10n('')
    ''

    .. _numeronym: http://en.wikipedia.org/wiki/Numeronym
    """
    if len(string) < 3:
        return string
    return f'{string[0]}{len(string[1:-1])}{string[-1]}'


# Based on https://en.wikipedia.org/wiki/ANSI_escape_code#Escape_sequences
ANSI_SEQUENCES = re.compile(r'''
    \x1B            # Sequence starts with ESC, i.e. hex 0x1B
    (?:
        [@-Z\\-_]   # Second byte:
                    #   all 0x40–0x5F range but CSI char, i.e ASCII @A–Z\]^_
    |               # Or
        \[          # CSI sequences, starting with [
        [0-?]*      # Parameter bytes:
                    #   range 0x30–0x3F, ASCII 0–9:;<=>?
        [ -/]*      # Intermediate bytes:
                    #   range 0x20–0x2F, ASCII space and !"#$%&'()*+,-./
        [@-~]       # Final byte
                    #   range 0x40–0x7E, ASCII @A–Z[\]^_`a–z{|}~
    )
''', re.VERBOSE)


def strip_ansi(text):
    """Strips ANSI escape codes from *text*. Useful for the occasional
    time when a log or redirected output accidentally captures console
    color codes and the like.

    >>> strip_ansi('\x1b[0m\x1b[1;36mart\x1b[46;34m')
    'art'

    Supports str, bytes and bytearray content as input. Returns the
    same type as the input.

    There's a lot of ANSI art available for testing on `sixteencolors.net`_.
    This function does not interpret or render ANSI art, but you can do so with
    `ansi2img`_ or `escapes.js`_.

    .. _sixteencolors.net: http://sixteencolors.net
    .. _ansi2img: http://www.bedroomlan.org/projects/ansi2img
    .. _escapes.js: https://github.com/atdt/escapes.js
    """
    # TODO: move to cliutils.py

    # Transform any ASCII-like content to unicode to allow regex to match, and
    # save input type for later.
    target_type = None
    # Unicode type aliased to str is code-smell for Boltons in Python 3 env.
    if isinstance(text, (bytes, bytearray)):
        target_type = type(text)
        text = text.decode('utf-8')

    cleaned = ANSI_SEQUENCES.sub('', text)

    # Transform back the result to the same bytearray type provided by the user.
    if target_type and target_type != type(cleaned):
        cleaned = target_type(cleaned, 'utf-8')

    return cleaned


def asciify(text, ignore=False):
    """Converts a unicode or bytestring, *text*, into a bytestring with
    just ascii characters. Performs basic deaccenting for all you
    Europhiles out there.

    Also, a gentle reminder that this is a **utility**, primarily meant
    for slugification. Whenever possible, make your application work
    **with** unicode, not against it.

    Args:
        text (str): The string to be asciified.
        ignore (bool): Configures final encoding to ignore remaining
            unasciified string instead of replacing it.

    >>> asciify('Beyoncé') == b'Beyonce'
    True
    """
    try:
        try:
            return text.encode('ascii')
        except UnicodeDecodeError:
            # this usually means you passed in a non-unicode string
            text = text.decode('utf-8')
            return text.encode('ascii')
    except UnicodeEncodeError:
        mode = 'replace'
        if ignore:
            mode = 'ignore'
        transd = unicodedata.normalize('NFKD', text.translate(DEACCENT_MAP))
        ret = transd.encode('ascii', mode)
        return ret


def is_ascii(text):
    """Check if a string or bytestring, *text*, is composed of ascii
    characters only. Raises :exc:`ValueError` if argument is not text.

    Args:
        text (str): The string to be checked.

    >>> is_ascii('Beyoncé')
    False
    >>> is_ascii('Beyonce')
    True
    """
    if isinstance(text, str):
        try:
            text.encode('ascii')
        except UnicodeEncodeError:
            return False
    elif isinstance(text, bytes):
        try:
            text.decode('ascii')
        except UnicodeDecodeError:
            return False
    else:
        raise ValueError('expected text or bytes, not %r' % type(text))
    return True


class DeaccenterDict(dict):
    "A small caching dictionary for deaccenting."
    def __missing__(self, key):
        ch = self.get(key)
        if ch is not None:
            return ch
        try:
            de = unicodedata.decomposition(chr(key))
            p1, _, p2 = de.rpartition(' ')
            if int(p2, 16) == 0x308:
                ch = self.get(key)
            else:
                ch = int(p1, 16)
        except (IndexError, ValueError):
            ch = self.get(key, key)
        self[key] = ch
        return ch


# http://chmullig.com/2009/12/python-unicode-ascii-ifier/
# For something more complete, investigate the unidecode
# or isounidecode packages, which are capable of performing
# crude transliteration.
_BASE_DEACCENT_MAP = {
    0xc6: "AE", # Æ LATIN CAPITAL LETTER AE
    0xd0: "D",  # Ð LATIN CAPITAL LETTER ETH
    0xd8: "OE", # Ø LATIN CAPITAL LETTER O WITH STROKE
    0xde: "Th", # Þ LATIN CAPITAL LETTER THORN
    0xc4: 'Ae', # Ä LATIN CAPITAL LETTER A WITH DIAERESIS
    0xd6: 'Oe', # Ö LATIN CAPITAL LETTER O WITH DIAERESIS
    0xdc: 'Ue', # Ü LATIN CAPITAL LETTER U WITH DIAERESIS
    0xc0: "A",  # À LATIN CAPITAL LETTER A WITH GRAVE
    0xc1: "A",  # Á LATIN CAPITAL LETTER A WITH ACUTE
    0xc3: "A",  # Ã LATIN CAPITAL LETTER A WITH TILDE
    0xc7: "C",  # Ç LATIN CAPITAL LETTER C WITH CEDILLA
    0xc8: "E",  # È LATIN CAPITAL LETTER E WITH GRAVE
    0xc9: "E",  # É LATIN CAPITAL LETTER E WITH ACUTE
    0xca: "E",  # Ê LATIN CAPITAL LETTER E WITH CIRCUMFLEX
    0xcc: "I",  # Ì LATIN CAPITAL LETTER I WITH GRAVE
    0xcd: "I",  # Í LATIN CAPITAL LETTER I WITH ACUTE
    0xd2: "O",  # Ò LATIN CAPITAL LETTER O WITH GRAVE
    0xd3: "O",  # Ó LATIN CAPITAL LETTER O WITH ACUTE
    0xd5: "O",  # Õ LATIN CAPITAL LETTER O WITH TILDE
    0xd9: "U",  # Ù LATIN CAPITAL LETTER U WITH GRAVE
    0xda: "U",  # Ú LATIN CAPITAL LETTER U WITH ACUTE
    0xdf: "ss", # ß LATIN SMALL LETTER SHARP S
    0xe6: "ae", # æ LATIN SMALL LETTER AE
    0xf0: "d",  # ð LATIN SMALL LETTER ETH
    0xf8: "oe", # ø LATIN SMALL LETTER O WITH STROKE
    0xfe: "th", # þ LATIN SMALL LETTER THORN,
    0xe4: 'ae', # ä LATIN SMALL LETTER A WITH DIAERESIS
    0xf6: 'oe', # ö LATIN SMALL LETTER O WITH DIAERESIS
    0xfc: 'ue', # ü LATIN SMALL LETTER U WITH DIAERESIS
    0xe0: "a",  # à LATIN SMALL LETTER A WITH GRAVE
    0xe1: "a",  # á LATIN SMALL LETTER A WITH ACUTE
    0xe3: "a",  # ã LATIN SMALL LETTER A WITH TILDE
    0xe7: "c",  # ç LATIN SMALL LETTER C WITH CEDILLA
    0xe8: "e",  # è LATIN SMALL LETTER E WITH GRAVE
    0xe9: "e",  # é LATIN SMALL LETTER E WITH ACUTE
    0xea: "e",  # ê LATIN SMALL LETTER E WITH CIRCUMFLEX
    0xec: "i",  # ì LATIN SMALL LETTER I WITH GRAVE
    0xed: "i",  # í LATIN SMALL LETTER I WITH ACUTE
    0xf2: "o",  # ò LATIN SMALL LETTER O WITH GRAVE
    0xf3: "o",  # ó LATIN SMALL LETTER O WITH ACUTE
    0xf5: "o",  # õ LATIN SMALL LETTER O WITH TILDE
    0xf9: "u",  # ù LATIN SMALL LETTER U WITH GRAVE
    0xfa: "u",  # ú LATIN SMALL LETTER U WITH ACUTE
    0x2018: "'",  # ‘ LEFT SINGLE QUOTATION MARK
    0x2019: "'",  # ’ RIGHT SINGLE QUOTATION MARK
    0x201c: '"',  # “ LEFT DOUBLE QUOTATION MARK
    0x201d: '"',  # ” RIGHT DOUBLE QUOTATION MARK
    }


DEACCENT_MAP = DeaccenterDict(_BASE_DEACCENT_MAP)


_SIZE_SYMBOLS = ('B', 'K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
_SIZE_BOUNDS = [(1024 ** i, sym) for i, sym in enumerate(_SIZE_SYMBOLS)]
_SIZE_RANGES = list(zip(_SIZE_BOUNDS, _SIZE_BOUNDS[1:]))


def bytes2human(nbytes, ndigits=0):
    """Turns an integer value of *nbytes* into a human readable format. Set
    *ndigits* to control how many digits after the decimal point
    should be shown (default ``0``).

    >>> bytes2human(128991)
    '126K'
    >>> bytes2human(100001221)
    '95M'
    >>> bytes2human(0, 2)
    '0.00B'
    """
    abs_bytes = abs(nbytes)
    for (size, symbol), (next_size, next_symbol) in _SIZE_RANGES:
        if abs_bytes <= next_size:
            break
    hnbytes = float(nbytes) / size
    return '{hnbytes:.{ndigits}f}{symbol}'.format(hnbytes=hnbytes,
                                                  ndigits=ndigits,
                                                  symbol=symbol)


class HTMLTextExtractor(HTMLParser):
    def __init__(self):
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.result = []

    def handle_data(self, d):
        self.result.append(d)

    def handle_charref(self, number):
        if number[0] == 'x' or number[0] == 'X':
            codepoint = int(number[1:], 16)
        else:
            codepoint = int(number)
        self.result.append(chr(codepoint))

    def handle_entityref(self, name):
        try:
            codepoint = htmlentitydefs.name2codepoint[name]
        except KeyError:
            self.result.append('&' + name + ';')
        else:
            self.result.append(chr(codepoint))

    def get_text(self):
        return ''.join(self.result)


def html2text(html):
    """Strips tags from HTML text, returning markup-free text. Also, does
    a best effort replacement of entities like "&nbsp;"

    >>> r = html2text(u'<a href="#">Test &amp;<em>(\u0394&#x03b7;&#956;&#x03CE;)</em></a>')
    >>> r == u'Test &(\u0394\u03b7\u03bc\u03ce)'
    True
    """
    # based on answers to http://stackoverflow.com/questions/753052/
    s = HTMLTextExtractor()
    s.feed(html)
    return s.get_text()


_EMPTY_GZIP_BYTES = b'\x1f\x8b\x08\x089\xf3\xb9U\x00\x03empty\x00\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00'
_NON_EMPTY_GZIP_BYTES = b'\x1f\x8b\x08\x08\xbc\xf7\xb9U\x00\x03not_empty\x00K\xaa,I-N\xcc\xc8\xafT\xe4\x02\x00\xf3nb\xbf\x0b\x00\x00\x00'


def gunzip_bytes(bytestring):
    """The :mod:`gzip` module is great if you have a file or file-like
    object, but what if you just have bytes. StringIO is one
    possibility, but it's often faster, easier, and simpler to just
    use this one-liner. Use this tried-and-true utility function to
    decompress gzip from bytes.

    >>> gunzip_bytes(_EMPTY_GZIP_BYTES) == b''
    True
    >>> gunzip_bytes(_NON_EMPTY_GZIP_BYTES).rstrip() == b'bytesahoy!'
    True
    """
    return zlib.decompress(bytestring, 16 + zlib.MAX_WBITS)


def gzip_bytes(bytestring, level=6):
    """Turn some bytes into some compressed bytes.

    >>> len(gzip_bytes(b'a' * 10000))
    46

    Args:
        bytestring (bytes): Bytes to be compressed
        level (int): An integer, 1-9, controlling the
          speed/compression. 1 is fastest, least compressed, 9 is
          slowest, but most compressed.

    Note that all levels of gzip are pretty fast these days, though
    it's not really a competitor in compression, at any level.
    """
    out = StringIO()
    f = GzipFile(fileobj=out, mode='wb', compresslevel=level)
    f.write(bytestring)
    f.close()
    return out.getvalue()



_line_ending_re = re.compile(r'(\r\n|\n|\x0b|\f|\r|\x85|\x2028|\x2029)',
                             re.UNICODE)


def iter_splitlines(text):
    r"""Like :meth:`str.splitlines`, but returns an iterator of lines
    instead of a list. Also similar to :meth:`file.next`, as that also
    lazily reads and yields lines from a file.

    This function works with a variety of line endings, but as always,
    be careful when mixing line endings within a file.

    >>> list(iter_splitlines('\nhi\nbye\n'))
    ['', 'hi', 'bye', '']
    >>> list(iter_splitlines('\r\nhi\rbye\r\n'))
    ['', 'hi', 'bye', '']
    >>> list(iter_splitlines(''))
    []
    """
    prev_end, len_text = 0, len(text)
    # print('last: %r' % last_idx)
    # start, end = None, None
    for match in _line_ending_re.finditer(text):
        start, end = match.start(1), match.end(1)
        # print(start, end)
        if prev_end <= start:
            yield text[prev_end:start]
        if end == len_text:
            yield ''
        prev_end = end
    tail = text[prev_end:]
    if tail:
        yield tail
    return


def indent(text, margin, newline='\n', key=bool):
    """The missing counterpart to the built-in :func:`textwrap.dedent`.

    Args:
        text (str): The text to indent.
        margin (str): The string to prepend to each line.
        newline (str): The newline used to rejoin the lines (default: ``\\n``)
        key (callable): Called on each line to determine whether to
          indent it. Default: :class:`bool`, to ensure that empty lines do
          not get whitespace added.
    """
    indented_lines = [(margin + line if key(line) else line)
                      for line in iter_splitlines(text)]
    return newline.join(indented_lines)


def is_uuid(obj, version=4):
    """Check the argument is either a valid UUID object or string.

    Args:
        obj (object): The test target. Strings and UUID objects supported.
        version (int): The target UUID version, set to 0 to skip version check.

    >>> is_uuid('e682ccca-5a4c-4ef2-9711-73f9ad1e15ea')
    True
    >>> is_uuid('0221f0d9-d4b9-11e5-a478-10ddb1c2feb9')
    False
    >>> is_uuid('0221f0d9-d4b9-11e5-a478-10ddb1c2feb9', version=1)
    True
    """
    if not isinstance(obj, uuid.UUID):
        try:
            obj = uuid.UUID(obj)
        except (TypeError, ValueError, AttributeError):
            return False
    if version and obj.version != int(version):
        return False
    return True


def escape_shell_args(args, sep=' ', style=None):
    """Returns an escaped version of each string in *args*, according to
    *style*.

    Args:
        args (list): A list of arguments to escape and join together
        sep (str): The separator used to join the escaped arguments.
        style (str): The style of escaping to use. Can be one of
          ``cmd`` or ``sh``, geared toward Windows and Linux/BSD/etc.,
          respectively. If *style* is ``None``, then it is picked
          according to the system platform.

    See :func:`args2cmd` and :func:`args2sh` for details and example
    output for each style.
    """
    if not style:
        style = 'cmd' if sys.platform == 'win32' else 'sh'

    if style == 'sh':
        return args2sh(args, sep=sep)
    elif style == 'cmd':
        return args2cmd(args, sep=sep)

    raise ValueError("style expected one of 'cmd' or 'sh', not %r" % style)


_find_sh_unsafe = re.compile(r'[^a-zA-Z0-9_@%+=:,./-]').search


def args2sh(args, sep=' '):
    """Return a shell-escaped string version of *args*, separated by
    *sep*, based on the rules of sh, bash, and other shells in the
    Linux/BSD/MacOS ecosystem.

    >>> print(args2sh(['aa', '[bb]', "cc'cc", 'dd"dd']))
    aa '[bb]' 'cc'"'"'cc' 'dd"dd'

    As you can see, arguments with no special characters are not
    escaped, arguments with special characters are quoted with single
    quotes, and single quotes themselves are quoted with double
    quotes. Double quotes are handled like any other special
    character.

    Based on code from the :mod:`pipes`/:mod:`shlex` modules. Also
    note that :mod:`shlex` and :mod:`argparse` have functions to split
    and parse strings escaped in this manner.
    """
    ret_list = []

    for arg in args:
        if not arg:
            ret_list.append("''")
            continue
        if _find_sh_unsafe(arg) is None:
            ret_list.append(arg)
            continue
        # use single quotes, and put single quotes into double quotes
        # the string $'b is then quoted as '$'"'"'b'
        ret_list.append("'" + arg.replace("'", "'\"'\"'") + "'")

    return ' '.join(ret_list)


def args2cmd(args, sep=' '):
    r"""Return a shell-escaped string version of *args*, separated by
    *sep*, using the same rules as the Microsoft C runtime.

    >>> print(args2cmd(['aa', '[bb]', "cc'cc", 'dd"dd']))
    aa [bb] cc'cc dd\"dd

    As you can see, escaping is through backslashing and not quoting,
    and double quotes are the only special character. See the comment
    in the code for more details. Based on internal code from the
    :mod:`subprocess` module.

    """
    # technique description from subprocess below
    """
    1) Arguments are delimited by white space, which is either a
       space or a tab.

    2) A string surrounded by double quotation marks is
       interpreted as a single argument, regardless of white space
       contained within.  A quoted string can be embedded in an
       argument.

    3) A double quotation mark preceded by a backslash is
       interpreted as a literal double quotation mark.

    4) Backslashes are interpreted literally, unless they
       immediately precede a double quotation mark.

    5) If backslashes immediately precede a double quotation mark,
       every pair of backslashes is interpreted as a literal
       backslash.  If the number of backslashes is odd, the last
       backslash escapes the next double quotation mark as
       described in rule 3.

    See http://msdn.microsoft.com/en-us/library/17w5ykft.aspx
    or search http://msdn.microsoft.com for
    "Parsing C++ Command-Line Arguments"
    """
    result = []
    needquote = False
    for arg in args:
        bs_buf = []

        # Add a space to separate this argument from the others
        if result:
            result.append(' ')

        needquote = (" " in arg) or ("\t" in arg) or not arg
        if needquote:
            result.append('"')

        for c in arg:
            if c == '\\':
                # Don't know if we need to double yet.
                bs_buf.append(c)
            elif c == '"':
                # Double backslashes.
                result.append('\\' * len(bs_buf)*2)
                bs_buf = []
                result.append('\\"')
            else:
                # Normal char
                if bs_buf:
                    result.extend(bs_buf)
                    bs_buf = []
                result.append(c)

        # Add remaining backslashes, if any.
        if bs_buf:
            result.extend(bs_buf)

        if needquote:
            result.extend(bs_buf)
            result.append('"')

    return ''.join(result)


def parse_int_list(range_string, delim=',', range_delim='-'):
    """Returns a sorted list of positive integers based on
    *range_string*. Reverse of :func:`format_int_list`.

    Args:
        range_string (str): String of comma separated positive
            integers or ranges (e.g. '1,2,4-6,8'). Typical of a custom
            page range string used in printer dialogs.
        delim (char): Defaults to ','. Separates integers and
            contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
            range of integers.

    >>> parse_int_list('1,3,5-8,10-11,15')
    [1, 3, 5, 6, 7, 8, 10, 11, 15]

    """
    output = []

    for x in range_string.strip().split(delim):

        # Range
        if range_delim in x:
            range_limits = list(map(int, x.split(range_delim)))
            output += list(range(min(range_limits), max(range_limits)+1))

        # Empty String
        elif not x:
            continue

        # Integer
        else:
            output.append(int(x))

    return sorted(output)


def format_int_list(int_list, delim=',', range_delim='-', delim_space=False):
    """Returns a sorted range string from a list of positive integers
    (*int_list*). Contiguous ranges of integers are collapsed to min
    and max values. Reverse of :func:`parse_int_list`.

    Args:
        int_list (list): List of positive integers to be converted
           into a range string (e.g. [1,2,4,5,6,8]).
        delim (char): Defaults to ','. Separates integers and
           contiguous ranges of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous
           range of integers.
        delim_space (bool): Defaults to ``False``. If ``True``, adds a
           space after all *delim* characters.

    >>> format_int_list([1,3,5,6,7,8,10,11,15])
    '1,3,5-8,10-11,15'

    """
    output = []
    contig_range = collections.deque()

    for x in sorted(int_list):

        # Handle current (and first) value.
        if len(contig_range) < 1:
            contig_range.append(x)

        # Handle current value, given multiple previous values are contiguous.
        elif len(contig_range) > 1:
            delta = x - contig_range[-1]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                      range_delim,
                                                      max(contig_range))
                output.append(range_substr)
                contig_range.clear()
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

        # Handle current value, given no previous contiguous integers
        else:
            delta = x - contig_range[0]

            # Current value is contiguous.
            if delta == 1:
                contig_range.append(x)

            # Current value is non-contiguous.
            elif delta > 1:
                output.append(f'{contig_range.popleft():d}')
                contig_range.append(x)

            # Current value repeated.
            else:
                continue

    # Handle the last value.
    else:

        # Last value is non-contiguous.
        if len(contig_range) == 1:
            output.append(f'{contig_range.popleft():d}')
            contig_range.clear()

        # Last value is part of contiguous range.
        elif len(contig_range) > 1:
            range_substr = '{:d}{}{:d}'.format(min(contig_range),
                                                  range_delim,
                                                  max(contig_range))
            output.append(range_substr)
            contig_range.clear()

    if delim_space:
        output_str = (delim+' ').join(output)
    else:
        output_str = delim.join(output)

    return output_str


def complement_int_list(
        range_string, range_start=0, range_end=None,
        delim=',', range_delim='-'):
    """ Returns range string that is the complement of the one provided as
    *range_string* parameter.

    These range strings are of the kind produce by :func:`format_int_list`, and
    parseable by :func:`parse_int_list`.

    Args:
        range_string (str): String of comma separated positive integers or
           ranges (e.g. '1,2,4-6,8'). Typical of a custom page range string
           used in printer dialogs.
        range_start (int): A positive integer from which to start the resulting
           range. Value is inclusive. Defaults to ``0``.
        range_end (int): A positive integer from which the produced range is
           stopped. Value is exclusive. Defaults to the maximum value found in
           the provided ``range_string``.
        delim (char): Defaults to ','. Separates integers and contiguous ranges
           of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous range of
           integers.

    >>> complement_int_list('1,3,5-8,10-11,15')
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=0)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=1)
    '2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=2)
    '2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=3)
    '4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=15)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=14)
    '0,2,4,9,12-13'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=13)
    '0,2,4,9,12'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=20)
    '0,2,4,9,12-14,16-19'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=0)
    ''

    >>> complement_int_list('1,3,5-8,10-11,15', range_start=-1)
    '0,2,4,9,12-14'

    >>> complement_int_list('1,3,5-8,10-11,15', range_end=-1)
    ''

    >>> complement_int_list('1,3,5-8', range_start=1, range_end=1)
    ''

    >>> complement_int_list('1,3,5-8', range_start=2, range_end=2)
    ''

    >>> complement_int_list('1,3,5-8', range_start=2, range_end=3)
    '2'

    >>> complement_int_list('1,3,5-8', range_start=-10, range_end=-5)
    ''

    >>> complement_int_list('1,3,5-8', range_start=20, range_end=10)
    ''

    >>> complement_int_list('')
    ''
    """
    int_list = set(parse_int_list(range_string, delim, range_delim))
    if range_end is None:
        if int_list:
            range_end = max(int_list) + 1
        else:
            range_end = range_start
    complement_values = set(
        range(range_end)) - int_list - set(range(range_start))
    return format_int_list(complement_values, delim, range_delim)


def int_ranges_from_int_list(range_string, delim=',', range_delim='-'):
    """ Transform a string of ranges (*range_string*) into a tuple of tuples.

    Args:
        range_string (str): String of comma separated positive integers or
           ranges (e.g. '1,2,4-6,8'). Typical of a custom page range string
           used in printer dialogs.
        delim (char): Defaults to ','. Separates integers and contiguous ranges
           of integers.
        range_delim (char): Defaults to '-'. Indicates a contiguous range of
           integers.

    >>> int_ranges_from_int_list('1,3,5-8,10-11,15')
    ((1, 1), (3, 3), (5, 8), (10, 11), (15, 15))

    >>> int_ranges_from_int_list('1')
    ((1, 1),)

    >>> int_ranges_from_int_list('')
    ()
    """
    int_tuples = []
    # Normalize the range string to our internal format for processing.
    range_string = format_int_list(
        parse_int_list(range_string, delim, range_delim))
    if range_string:
        for bounds in range_string.split(','):
            if '-' in bounds:
                start, end = bounds.split('-')
            else:
                start, end = bounds, bounds
            int_tuples.append((int(start), int(end)))
    return tuple(int_tuples)


class MultiReplace:
    """
    MultiReplace is a tool for doing multiple find/replace actions in one pass.

    Given a mapping of values to be replaced it allows for all of the matching
    values to be replaced in a single pass which can save a lot of performance
    on very large strings. In addition to simple replace, it also allows for
    replacing based on regular expressions.

    Keyword Arguments:

    :type regex: bool
    :param regex: Treat search keys as regular expressions [Default: False]
    :type flags: int
    :param flags: flags to pass to the regex engine during compile

    Dictionary Usage::

        from boltons import strutils
        s = strutils.MultiReplace({
            'foo': 'zoo',
            'cat': 'hat',
            'bat': 'kraken'
        })
        new = s.sub('The foo bar cat ate a bat')
        new == 'The zoo bar hat ate a kraken'

    Iterable Usage::

        from boltons import strutils
        s = strutils.MultiReplace([
            ('foo', 'zoo'),
            ('cat', 'hat'),
            ('bat', 'kraken)'
        ])
        new = s.sub('The foo bar cat ate a bat')
        new == 'The zoo bar hat ate a kraken'


    The constructor can be passed a dictionary or other mapping as well as
    an iterable of tuples. If given an iterable, the substitution will be run
    in the order the replacement values are specified in the iterable. This is
    also true if it is given an OrderedDict. If given a dictionary then the
    order will be non-deterministic::

        >>> 'foo bar baz'.replace('foo', 'baz').replace('baz', 'bar')
        'bar bar bar'
        >>> m = MultiReplace({'foo': 'baz', 'baz': 'bar'})
        >>> m.sub('foo bar baz')
        'baz bar bar'

    This is because the order of replacement can matter if you're inserting
    something that might be replaced by a later substitution. Pay attention and
    if you need to rely on order then consider using a list of tuples instead
    of a dictionary.
    """

    def __init__(self, sub_map, **kwargs):
        """Compile any regular expressions that have been passed."""
        options = {
            'regex': False,
            'flags': 0,
        }
        options.update(kwargs)
        self.group_map = {}
        regex_values = []

        if isinstance(sub_map, Mapping):
            sub_map = sub_map.items()

        for idx, vals in enumerate(sub_map):
            group_name = f'group{idx}'
            if isinstance(vals[0], str):
                # If we're not treating input strings like a regex, escape it
                if not options['regex']:
                    exp = re.escape(vals[0])
                else:
                    exp = vals[0]
            else:
                exp = vals[0].pattern

            regex_values.append(f'(?P<{group_name}>{exp})')
            self.group_map[group_name] = vals[1]

        self.combined_pattern = re.compile(
            '|'.join(regex_values),
            flags=options['flags']
        )

    def _get_value(self, match):
        """Given a match object find replacement value."""
        group_dict = match.groupdict()
        key = [x for x in group_dict if group_dict[x]][0]
        return self.group_map[key]

    def sub(self, text):
        """
        Run substitutions on the input text.

        Given an input string, run all substitutions given in the
        constructor.
        """
        return self.combined_pattern.sub(self._get_value, text)


def multi_replace(text, sub_map, **kwargs):
    """
    Shortcut function to invoke MultiReplace in a single call.

    Example Usage::

        from boltons.strutils import multi_replace
        new = multi_replace(
            'The foo bar cat ate a bat',
            {'foo': 'zoo', 'cat': 'hat', 'bat': 'kraken'}
        )
        new == 'The zoo bar hat ate a kraken'
    """
    m = MultiReplace(sub_map, **kwargs)
    return m.sub(text)


def unwrap_text(text, ending='\n\n'):
    r"""
    Unwrap text, the natural complement to :func:`textwrap.wrap`.

    >>> text = "Short \n lines  \nwrapped\nsmall.\n\nAnother\nparagraph."
    >>> unwrap_text(text)
    'Short lines wrapped small.\n\nAnother paragraph.'

    Args:
       text: A string to unwrap.
       ending (str): The string to join all unwrapped paragraphs
          by. Pass ``None`` to get the list. Defaults to '\n\n' for
          compatibility with Markdown and RST.

    """
    all_grafs = []
    cur_graf = []
    for line in text.splitlines():
        line = line.strip()
        if line:
            cur_graf.append(line)
        else:
            all_grafs.append(' '.join(cur_graf))
            cur_graf = []
    if cur_graf:
        all_grafs.append(' '.join(cur_graf))
    if ending is None:
        return all_grafs
    return ending.join(all_grafs)

def removeprefix(text: str, prefix: str) -> str:
    r"""
    Remove `prefix` from start of `text` if present.

    Backport of `str.removeprefix` for Python versions less than 3.9.

    Args:
        text: A string to remove the prefix from.
        prefix: The string to remove from the beginning of `text`.
    """
    if text.startswith(prefix):
        return text[len(prefix):]
    return text
