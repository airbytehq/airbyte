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

""":mod:`urlutils` is a module dedicated to one of software's most
versatile, well-aged, and beloved data structures: the URL, also known
as the `Uniform Resource Locator`_.

Among other things, this module is a full reimplementation of URLs,
without any reliance on the :mod:`urlparse` or :mod:`urllib` standard
library modules. The centerpiece and top-level interface of urlutils
is the :class:`URL` type. Also featured is the :func:`find_all_links`
convenience function. Some low-level functions and constants are also
below.

The implementations in this module are based heavily on `RFC 3986`_ and
`RFC 3987`_, and incorporates details from several other RFCs and `W3C
documents`_.

.. _Uniform Resource Locator: https://en.wikipedia.org/wiki/Uniform_Resource_Locator
.. _RFC 3986: https://tools.ietf.org/html/rfc3986
.. _RFC 3987: https://tools.ietf.org/html/rfc3987
.. _W3C documents: https://www.w3.org/TR/uri-clarification/

"""

import re
import socket
import string
from unicodedata import normalize

# The unreserved URI characters (per RFC 3986 Section 2.3)
_UNRESERVED_CHARS = frozenset('~-._0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                              'abcdefghijklmnopqrstuvwxyz')

# URL parsing regex (based on RFC 3986 Appendix B, with modifications)
_URL_RE = re.compile(r'^((?P<scheme>[^:/?#]+):)?'
                     r'((?P<_netloc_sep>//)(?P<authority>[^/?#]*))?'
                     r'(?P<path>[^?#]*)'
                     r'(\?(?P<query>[^#]*))?'
                     r'(#(?P<fragment>.*))?')


_HEX_CHAR_MAP = {(a + b).encode('ascii'):
                 chr(int(a + b, 16)).encode('charmap')
                 for a in string.hexdigits for b in string.hexdigits}
_ASCII_RE = re.compile('([\x00-\x7f]+)')


# This port list painstakingly curated by hand searching through
# https://www.iana.org/assignments/uri-schemes/uri-schemes.xhtml
# and
# https://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.xhtml
SCHEME_PORT_MAP = {'acap': 674, 'afp': 548, 'dict': 2628, 'dns': 53,
                   'file': None, 'ftp': 21, 'git': 9418, 'gopher': 70,
                   'http': 80, 'https': 443, 'imap': 143, 'ipp': 631,
                   'ipps': 631, 'irc': 194, 'ircs': 6697, 'ldap': 389,
                   'ldaps': 636, 'mms': 1755, 'msrp': 2855, 'msrps': None,
                   'mtqp': 1038, 'nfs': 111, 'nntp': 119, 'nntps': 563,
                   'pop': 110, 'prospero': 1525, 'redis': 6379, 'rsync': 873,
                   'rtsp': 554, 'rtsps': 322, 'rtspu': 5005, 'sftp': 22,
                   'smb': 445, 'snmp': 161, 'ssh': 22, 'steam': None,
                   'svn': 3690, 'telnet': 23, 'ventrilo': 3784, 'vnc': 5900,
                   'wais': 210, 'ws': 80, 'wss': 443, 'xmpp': None}

# This list of schemes that don't use authorities is also from the link above.
NO_NETLOC_SCHEMES = {'urn', 'about', 'bitcoin', 'blob', 'data', 'geo',
                         'magnet', 'mailto', 'news', 'pkcs11',
                         'sip', 'sips', 'tel'}
# As of Mar 11, 2017, there were 44 netloc schemes, and 13 non-netloc

# RFC 3986 section 2.2, Reserved Characters
_GEN_DELIMS = frozenset(':/?#[]@')
_SUB_DELIMS = frozenset("!$&'()*+,;=")
_ALL_DELIMS = _GEN_DELIMS | _SUB_DELIMS

_USERINFO_SAFE = _UNRESERVED_CHARS | _SUB_DELIMS
_USERINFO_DELIMS = _ALL_DELIMS - _USERINFO_SAFE
_PATH_SAFE = _UNRESERVED_CHARS | _SUB_DELIMS | set(':@')
_PATH_DELIMS = _ALL_DELIMS - _PATH_SAFE
_FRAGMENT_SAFE = _UNRESERVED_CHARS | _PATH_SAFE | set('/?')
_FRAGMENT_DELIMS = _ALL_DELIMS - _FRAGMENT_SAFE
_QUERY_SAFE = _UNRESERVED_CHARS | _FRAGMENT_SAFE - set('&=+')
_QUERY_DELIMS = _ALL_DELIMS - _QUERY_SAFE


class URLParseError(ValueError):
    """Exception inheriting from :exc:`ValueError`, raised when failing to
    parse a URL. Mostly raised on invalid ports and IPv6 addresses.
    """
    pass


DEFAULT_ENCODING = 'utf8'


def to_unicode(obj):
    try:
        return str(obj)
    except UnicodeDecodeError:
        return str(obj, encoding=DEFAULT_ENCODING)


# regex from gruber via tornado
# doesn't support ipv6
# doesn't support mailto (netloc-less schemes)
_FIND_ALL_URL_RE = re.compile(r"""\b((?:([\w-]+):(/{1,3})|www[.])(?:(?:(?:[^\s&()<>]|&amp;|&quot;)*(?:[^!"#$%'()*+,.:;<=>?@\[\]^`{|}~\s]))|(?:\((?:[^\s&()]|&amp;|&quot;)*\)))+)""")


def find_all_links(text, with_text=False, default_scheme='https', schemes=()):
    """This function uses heuristics to searches plain text for strings
    that look like URLs, returning a :class:`list` of :class:`URL`
    objects. It supports limiting the accepted schemes, and returning
    interleaved text as well.

    >>> find_all_links('Visit https://boltons.rtfd.org!')
    [URL(u'https://boltons.rtfd.org')]
    >>> find_all_links('Visit https://boltons.rtfd.org!', with_text=True)
    [u'Visit ', URL(u'https://boltons.rtfd.org'), u'!']

    Args:
       text (str): The text to search.

       with_text (bool): Whether or not to interleave plaintext blocks
          with the returned URL objects. Having all tokens can be
          useful for transforming the text, e.g., replacing links with
          HTML equivalents. Defaults to ``False``.

       default_scheme (str): Many URLs are written without the scheme
          component. This function can match a reasonable subset of
          those, provided *default_scheme* is set to a string. Set to
          ``False`` to disable matching scheme-less URLs. Defaults to
          ``'https'``.

       schemes (list): A list of strings that a URL's scheme must
          match in order to be included in the results. Defaults to
          empty, which matches all schemes.

    .. note:: Currently this function does not support finding IPv6
      addresses or URLs with netloc-less schemes, like mailto.

    """
    text = to_unicode(text)
    prev_end, start, end = 0, None, None
    ret = []
    _add = ret.append

    def _add_text(t):
        if ret and isinstance(ret[-1], str):
            ret[-1] += t
        else:
            _add(t)

    for match in _FIND_ALL_URL_RE.finditer(text):
        start, end = match.start(1), match.end(1)
        if prev_end < start and with_text:
            _add(text[prev_end:start])
        prev_end = end
        try:
            cur_url_text = match.group(0)
            cur_url = URL(cur_url_text)
            if not cur_url.scheme:
                if default_scheme:
                    cur_url = URL(default_scheme + '://' + cur_url_text)
                else:
                    _add_text(text[start:end])
                    continue
            if schemes and cur_url.scheme not in schemes:
                _add_text(text[start:end])
            else:
                _add(cur_url)
        except URLParseError:
            # currently this should only be hit with broken port
            # strings. the regex above doesn't support ipv6 addresses
            if with_text:
                _add_text(text[start:end])

    if with_text:
        tail = text[prev_end:]
        if tail:
            _add_text(tail)

    return ret


def _make_quote_map(safe_chars):
    ret = {}
    # v is included in the dict for py3 mostly, because bytestrings
    # are iterables of ints, of course!
    for i, v in zip(range(256), range(256)):
        c = chr(v)
        if c in safe_chars:
            ret[c] = ret[v] = c
        else:
            ret[c] = ret[v] = f'%{i:02X}'
    return ret


_USERINFO_PART_QUOTE_MAP = _make_quote_map(_USERINFO_SAFE)
_PATH_PART_QUOTE_MAP = _make_quote_map(_PATH_SAFE)
_QUERY_PART_QUOTE_MAP = _make_quote_map(_QUERY_SAFE)
_FRAGMENT_QUOTE_MAP = _make_quote_map(_FRAGMENT_SAFE)


def quote_path_part(text, full_quote=True):
    """
    Percent-encode a single segment of a URL path.
    """
    if full_quote:
        bytestr = normalize('NFC', to_unicode(text)).encode('utf8')
        return ''.join([_PATH_PART_QUOTE_MAP[b] for b in bytestr])
    return ''.join([_PATH_PART_QUOTE_MAP[t] if t in _PATH_DELIMS else t
                     for t in text])


def quote_query_part(text, full_quote=True):
    """
    Percent-encode a single query string key or value.
    """
    if full_quote:
        bytestr = normalize('NFC', to_unicode(text)).encode('utf8')
        return ''.join([_QUERY_PART_QUOTE_MAP[b] for b in bytestr])
    return ''.join([_QUERY_PART_QUOTE_MAP[t] if t in _QUERY_DELIMS else t
                     for t in text])


def quote_fragment_part(text, full_quote=True):
    """Quote the fragment part of the URL. Fragments don't have
    subdelimiters, so the whole URL fragment can be passed.
    """
    if full_quote:
        bytestr = normalize('NFC', to_unicode(text)).encode('utf8')
        return ''.join([_FRAGMENT_QUOTE_MAP[b] for b in bytestr])
    return ''.join([_FRAGMENT_QUOTE_MAP[t] if t in _FRAGMENT_DELIMS else t
                     for t in text])


def quote_userinfo_part(text, full_quote=True):
    """Quote special characters in either the username or password
    section of the URL. Note that userinfo in URLs is considered
    deprecated in many circles (especially browsers), and support for
    percent-encoded userinfo can be spotty.
    """
    if full_quote:
        bytestr = normalize('NFC', to_unicode(text)).encode('utf8')
        return ''.join([_USERINFO_PART_QUOTE_MAP[b] for b in bytestr])
    return ''.join([_USERINFO_PART_QUOTE_MAP[t] if t in _USERINFO_DELIMS
                     else t for t in text])


def unquote(string, encoding='utf-8', errors='replace'):
    """Percent-decode a string, by replacing %xx escapes with their
    single-character equivalent. The optional *encoding* and *errors*
    parameters specify how to decode percent-encoded sequences into
    Unicode characters, as accepted by the :meth:`bytes.decode()` method.  By
    default, percent-encoded sequences are decoded with UTF-8, and
    invalid sequences are replaced by a placeholder character.

    >>> unquote(u'abc%20def')
    u'abc def'
    """
    if '%' not in string:
        string.split
        return string
    if encoding is None:
        encoding = 'utf-8'
    if errors is None:
        errors = 'replace'
    bits = _ASCII_RE.split(string)
    res = [bits[0]]
    append = res.append
    for i in range(1, len(bits), 2):
        append(unquote_to_bytes(bits[i]).decode(encoding, errors))
        append(bits[i + 1])
    return ''.join(res)


def unquote_to_bytes(string):
    """unquote_to_bytes('abc%20def') -> b'abc def'."""
    # Note: strings are encoded as UTF-8. This is only an issue if it contains
    # unescaped non-ASCII characters, which URIs should not.
    if not string:
        # Is it a string-like object?
        string.split
        return b''
    if isinstance(string, str):
        string = string.encode('utf-8')
    bits = string.split(b'%')
    if len(bits) == 1:
        return string
    # import pdb;pdb.set_trace()
    res = [bits[0]]
    append = res.append

    for item in bits[1:]:
        try:
            append(_HEX_CHAR_MAP[item[:2]])
            append(item[2:])
        except KeyError:
            append(b'%')
            append(item)
    return b''.join(res)


def register_scheme(text, uses_netloc=None, default_port=None):
    """Registers new scheme information, resulting in correct port and
    slash behavior from the URL object. There are dozens of standard
    schemes preregistered, so this function is mostly meant for
    proprietary internal customizations or stopgaps on missing
    standards information. If a scheme seems to be missing, please
    `file an issue`_!

    Args:
        text (str): Text representing the scheme.
           (the 'http' in 'http://hatnote.com')
        uses_netloc (bool): Does the scheme support specifying a
           network host? For instance, "http" does, "mailto" does not.
        default_port (int): The default port, if any, for netloc-using
           schemes.

    .. _file an issue: https://github.com/mahmoud/boltons/issues
    """
    text = text.lower()
    if default_port is not None:
        try:
            default_port = int(default_port)
        except ValueError:
            raise ValueError('default_port expected integer or None, not %r'
                             % (default_port,))

    if uses_netloc is True:
        SCHEME_PORT_MAP[text] = default_port
    elif uses_netloc is False:
        if default_port is not None:
            raise ValueError('unexpected default port while specifying'
                             ' non-netloc scheme: %r' % default_port)
        NO_NETLOC_SCHEMES.add(text)
    elif uses_netloc is not None:
        raise ValueError('uses_netloc expected True, False, or None')

    return


def resolve_path_parts(path_parts):
    """Normalize the URL path by resolving segments of '.' and '..',
    resulting in a dot-free path.  See RFC 3986 section 5.2.4, Remove
    Dot Segments.
    """
    # TODO: what to do with multiple slashes
    ret = []

    for part in path_parts:
        if part == '.':
            pass
        elif part == '..':
            if ret and (len(ret) > 1 or ret[0]):  # prevent unrooting
                ret.pop()
        else:
            ret.append(part)

    if list(path_parts[-1:]) in (['.'], ['..']):
        ret.append('')

    return ret


class cachedproperty:
    """The ``cachedproperty`` is used similar to :class:`property`, except
    that the wrapped method is only called once. This is commonly used
    to implement lazy attributes.

    After the property has been accessed, the value is stored on the
    instance itself, using the same name as the cachedproperty. This
    allows the cache to be cleared with :func:`delattr`, or through
    manipulating the object's ``__dict__``.
    """
    def __init__(self, func):
        self.__doc__ = getattr(func, '__doc__')
        self.func = func

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        value = obj.__dict__[self.func.__name__] = self.func(obj)
        return value

    def __repr__(self):
        cn = self.__class__.__name__
        return f'<{cn} func={self.func}>'


class URL:
    r"""The URL is one of the most ubiquitous data structures in the
    virtual and physical landscape. From blogs to billboards, URLs are
    so common, that it's easy to overlook their complexity and
    power.

    There are 8 parts of a URL, each with its own semantics and
    special characters:

      * :attr:`~URL.scheme`
      * :attr:`~URL.username`
      * :attr:`~URL.password`
      * :attr:`~URL.host`
      * :attr:`~URL.port`
      * :attr:`~URL.path`
      * :attr:`~URL.query_params` (query string parameters)
      * :attr:`~URL.fragment`

    Each is exposed as an attribute on the URL object. RFC 3986 offers
    this brief structural summary of the main URL components::

        foo://user:pass@example.com:8042/over/there?name=ferret#nose
        \_/   \_______/ \_________/ \__/\_________/ \_________/ \__/
         |        |          |        |      |           |        |
       scheme  userinfo     host     port   path       query   fragment

    And here's how that example can be manipulated with the URL type:

    >>> url = URL('foo://example.com:8042/over/there?name=ferret#nose')
    >>> print(url.host)
    example.com
    >>> print(url.get_authority())
    example.com:8042
    >>> print(url.qp['name'])  # qp is a synonym for query_params
    ferret

    URL's approach to encoding is that inputs are decoded as much as
    possible, and data remains in this decoded state until re-encoded
    using the :meth:`~URL.to_text()` method. In this way, it's similar
    to Python's current approach of encouraging immediate decoding of
    bytes to text.

    Note that URL instances are mutable objects. If an immutable
    representation of the URL is desired, the string from
    :meth:`~URL.to_text()` may be used. For an immutable, but
    almost-as-featureful, URL object, check out the `hyperlink
    package`_.

    .. _hyperlink package: https://github.com/mahmoud/hyperlink

    """

    # public attributes (for comparison, see __eq__):
    _cmp_attrs = ('scheme', 'uses_netloc', 'username', 'password',
                  'family', 'host', 'port', 'path', 'query_params', 'fragment')

    def __init__(self, url=''):
        # TODO: encoding param. The encoding that underlies the
        # percent-encoding is always utf8 for IRIs, but can be Latin-1
        # for other usage schemes.
        ud = DEFAULT_PARSED_URL
        if url:
            if isinstance(url, URL):
                url = url.to_text()  # better way to copy URLs?
            elif isinstance(url, bytes):
                try:
                    url = url.decode(DEFAULT_ENCODING)
                except UnicodeDecodeError as ude:
                    raise URLParseError('expected text or %s-encoded bytes.'
                                        ' try decoding the url bytes and'
                                        ' passing the result. (got: %s)'
                                        % (DEFAULT_ENCODING, ude))
            ud = parse_url(url)

        _e = ''
        self.scheme = ud['scheme'] or _e
        self._netloc_sep = ud['_netloc_sep'] or _e
        self.username = (unquote(ud['username'])
                         if '%' in (ud['username'] or _e) else ud['username'] or _e)
        self.password = (unquote(ud['password'])
                         if '%' in (ud['password'] or _e) else ud['password'] or _e)
        self.family = ud['family']

        if not ud['host']:
            self.host = _e
        else:
            try:
                self.host = ud['host'].encode("ascii")
            except UnicodeEncodeError:
                self.host = ud['host']  # already non-ascii text
            else:
                self.host = self.host.decode("idna")

        self.port = ud['port']
        self.path_parts = tuple([unquote(p) if '%' in p else p for p
                                 in (ud['path'] or _e).split('/')])
        self._query = ud['query'] or _e
        self.fragment = (unquote(ud['fragment'])
                         if '%' in (ud['fragment'] or _e) else ud['fragment'] or _e)
        # TODO: possibly use None as marker for empty vs missing
        return

    @classmethod
    def from_parts(cls, scheme=None, host=None, path_parts=(), query_params=(),
                   fragment='', port=None, username=None, password=None):
        """Build a new URL from parts. Note that the respective arguments are
        not in the order they would appear in a URL:

        Args:
           scheme (str): The scheme of a URL, e.g., 'http'
           host (str): The host string, e.g., 'hatnote.com'
           path_parts (tuple): The individual text segments of the
             path, e.g., ('post', '123')
           query_params (dict): An OMD, dict, or list of (key, value)
             pairs representing the keys and values of the URL's query
             parameters.
           fragment (str): The fragment of the URL, e.g., 'anchor1'
           port (int): The integer port of URL, automatic defaults are
             available for registered schemes.
           username (str): The username for the userinfo part of the URL.
           password (str): The password for the userinfo part of the URL.

        Note that this method does relatively little
        validation. :meth:`URL.to_text()` should be used to check if
        any errors are produced while composing the final textual URL.
        """
        ret = cls()

        ret.scheme = scheme
        ret.host = host
        ret.path_parts = tuple(path_parts) or ('',)
        ret.query_params.update(query_params)
        ret.fragment = fragment
        ret.port = port
        ret.username = username
        ret.password = password

        return ret

    @cachedproperty
    def query_params(self):
        """The parsed form of the query string of the URL, represented as a
        :class:`~dictutils.OrderedMultiDict`. Also available as the
        handy alias ``qp``.

        >>> url = URL('http://boltons.readthedocs.io/?utm_source=doctest&python=great')
        >>> url.qp.keys()
        [u'utm_source', u'python']
        """
        return QueryParamDict.from_text(self._query)

    qp = query_params

    @property
    def path(self):
        "The URL's path, in text form."
        return '/'.join([quote_path_part(p, full_quote=False)
                          for p in self.path_parts])

    @path.setter
    def path(self, path_text):
        self.path_parts = tuple([unquote(p) if '%' in p else p
                                 for p in to_unicode(path_text).split('/')])
        return

    @property
    def uses_netloc(self):
        """Whether or not a URL uses :code:`:` or :code:`://` to separate the
        scheme from the rest of the URL depends on the scheme's own
        standard definition. There is no way to infer this behavior
        from other parts of the URL. A scheme either supports network
        locations or it does not.

        The URL type's approach to this is to check for explicitly
        registered schemes, with common schemes like HTTP
        preregistered. This is the same approach taken by
        :mod:`urlparse`.

        URL adds two additional heuristics if the scheme as a whole is
        not registered. First, it attempts to check the subpart of the
        scheme after the last ``+`` character. This adds intuitive
        behavior for schemes like ``git+ssh``. Second, if a URL with
        an unrecognized scheme is loaded, it will maintain the
        separator it sees.

        >>> print(URL('fakescheme://test.com').to_text())
        fakescheme://test.com
        >>> print(URL('mockscheme:hello:world').to_text())
        mockscheme:hello:world

        """
        default = self._netloc_sep
        if self.scheme in SCHEME_PORT_MAP:
            return True
        if self.scheme in NO_NETLOC_SCHEMES:
            return False
        if self.scheme.split('+')[-1] in SCHEME_PORT_MAP:
            return True
        return default

    @property
    def default_port(self):
        """Return the default port for the currently-set scheme. Returns
        ``None`` if the scheme is unrecognized. See
        :func:`register_scheme` above. If :attr:`~URL.port` matches
        this value, no port is emitted in the output of
        :meth:`~URL.to_text()`.

        Applies the same '+' heuristic detailed in :meth:`URL.uses_netloc`.
        """
        try:
            return SCHEME_PORT_MAP[self.scheme]
        except KeyError:
            return SCHEME_PORT_MAP.get(self.scheme.split('+')[-1])

    def normalize(self, with_case=True):
        """Resolve any "." and ".." references in the path, as well as
        normalize scheme and host casing. To turn off case
        normalization, pass ``with_case=False``.

        More information can be found in `Section 6.2.2 of RFC 3986`_.

        .. _Section 6.2.2 of RFC 3986: https://tools.ietf.org/html/rfc3986#section-6.2.2
        """
        self.path_parts = resolve_path_parts(self.path_parts)

        if with_case:
            self.scheme = self.scheme.lower()
            self.host = self.host.lower()
        return

    def navigate(self, dest):
        """Factory method that returns a _new_ :class:`URL` based on a given
        destination, *dest*. Useful for navigating those relative
        links with ease.

        The newly created :class:`URL` is normalized before being returned.

        >>> url = URL('http://boltons.readthedocs.io')
        >>> url.navigate('en/latest/')
        URL(u'http://boltons.readthedocs.io/en/latest/')

        Args:
           dest (str): A string or URL object representing the destination

        More information can be found in `Section 5 of RFC 3986`_.

        .. _Section 5 of RFC 3986: https://tools.ietf.org/html/rfc3986#section-5
        """
        orig_dest = None
        if not isinstance(dest, URL):
            dest, orig_dest = URL(dest), dest
        if dest.scheme and dest.host:
            # absolute URLs replace everything, but don't make an
            # extra copy if we don't have to
            return URL(dest) if orig_dest is None else dest
        query_params = dest.query_params

        if dest.path:
            if dest.path.startswith('/'):   # absolute path
                new_path_parts = list(dest.path_parts)
            else:  # relative path
                new_path_parts = list(self.path_parts[:-1]) \
                               + list(dest.path_parts)
        else:
            new_path_parts = list(self.path_parts)
            if not query_params:
                query_params = self.query_params

        ret = self.from_parts(scheme=dest.scheme or self.scheme,
                              host=dest.host or self.host,
                              port=dest.port or self.port,
                              path_parts=new_path_parts,
                              query_params=query_params,
                              fragment=dest.fragment,
                              username=dest.username or self.username,
                              password=dest.password or self.password)
        ret.normalize()
        return ret

    def get_authority(self, full_quote=False, with_userinfo=False):
        """Used by URL schemes that have a network location,
        :meth:`~URL.get_authority` combines :attr:`username`,
        :attr:`password`, :attr:`host`, and :attr:`port` into one
        string, the *authority*, that is used for
        connecting to a network-accessible resource.

        Used internally by :meth:`~URL.to_text()` and can be useful
        for labeling connections.

        >>> url = URL('ftp://user@ftp.debian.org:2121/debian/README')
        >>> print(url.get_authority())
        ftp.debian.org:2121
        >>> print(url.get_authority(with_userinfo=True))
        user@ftp.debian.org:2121

        Args:
           full_quote (bool): Whether or not to apply IDNA encoding.
              Defaults to ``False``.
           with_userinfo (bool): Whether or not to include username
              and password, technically part of the
              authority. Defaults to ``False``.

        """
        parts = []
        _add = parts.append
        if self.username and with_userinfo:
            _add(quote_userinfo_part(self.username))
            if self.password:
                _add(':')
                _add(quote_userinfo_part(self.password))
            _add('@')
        if self.host:
            if self.family == socket.AF_INET6:
                _add('[')
                _add(self.host)
                _add(']')
            elif full_quote:
                _add(self.host.encode('idna').decode('ascii'))
            else:
                _add(self.host)
            # TODO: 0 port?
            if self.port and self.port != self.default_port:
                _add(':')
                _add(str(self.port))
        return ''.join(parts)

    def to_text(self, full_quote=False):
        """Render a string representing the current state of the URL
        object.

        >>> url = URL('http://listen.hatnote.com')
        >>> url.fragment = 'en'
        >>> print(url.to_text())
        http://listen.hatnote.com#en

        By setting the *full_quote* flag, the URL can either be fully
        quoted or minimally quoted. The most common characteristic of
        an encoded-URL is the presence of percent-encoded text (e.g.,
        %60).  Unquoted URLs are more readable and suitable
        for display, whereas fully-quoted URLs are more conservative
        and generally necessary for sending over the network.
        """
        scheme = self.scheme
        path = '/'.join([quote_path_part(p, full_quote=full_quote)
                          for p in self.path_parts])
        authority = self.get_authority(full_quote=full_quote,
                                       with_userinfo=True)
        query_string = self.query_params.to_text(full_quote=full_quote)
        fragment = quote_fragment_part(self.fragment, full_quote=full_quote)

        parts = []
        _add = parts.append
        if scheme:
            _add(scheme)
            _add(':')
        if authority:
            _add('//')
            _add(authority)
        elif (scheme and path[:2] != '//' and self.uses_netloc):
            _add('//')
        if path:
            if scheme and authority and path[:1] != '/':
                _add('/')
                # TODO: i think this is here because relative paths
                # with absolute authorities = undefined
            _add(path)
        if query_string:
            _add('?')
            _add(query_string)
        if fragment:
            _add('#')
            _add(fragment)
        return ''.join(parts)

    def __repr__(self):
        cn = self.__class__.__name__
        return f'{cn}({self.to_text()!r})'

    def __str__(self):
        return self.to_text()

    def __unicode__(self):
        return self.to_text()

    def __eq__(self, other):
        for attr in self._cmp_attrs:
            if not getattr(self, attr) == getattr(other, attr, None):
                return False
        return True

    def __ne__(self, other):
        return not self == other


try:
    from socket import inet_pton
except ImportError:
    # from https://gist.github.com/nnemkin/4966028
    import ctypes

    class _sockaddr(ctypes.Structure):
        _fields_ = [("sa_family", ctypes.c_short),
                    ("__pad1", ctypes.c_ushort),
                    ("ipv4_addr", ctypes.c_byte * 4),
                    ("ipv6_addr", ctypes.c_byte * 16),
                    ("__pad2", ctypes.c_ulong)]

    WSAStringToAddressA = ctypes.windll.ws2_32.WSAStringToAddressA
    WSAAddressToStringA = ctypes.windll.ws2_32.WSAAddressToStringA

    def inet_pton(address_family, ip_string):
        addr = _sockaddr()
        ip_string = ip_string.encode('ascii')
        addr.sa_family = address_family
        addr_size = ctypes.c_int(ctypes.sizeof(addr))

        if WSAStringToAddressA(ip_string, address_family, None, ctypes.byref(addr), ctypes.byref(addr_size)) != 0:
            raise OSError(ctypes.FormatError())

        if address_family == socket.AF_INET:
            return ctypes.string_at(addr.ipv4_addr, 4)
        if address_family == socket.AF_INET6:
            return ctypes.string_at(addr.ipv6_addr, 16)
        raise OSError('unknown address family')


def parse_host(host):
    """\
    Low-level function used to parse the host portion of a URL.

    Returns a tuple of (family, host) where *family* is a
    :mod:`socket` module constant or ``None``, and host is a string.

    >>> parse_host('googlewebsite.com') == (None, 'googlewebsite.com')
    True
    >>> parse_host('[::1]') == (socket.AF_INET6, '::1')
    True
    >>> parse_host('192.168.1.1') == (socket.AF_INET, '192.168.1.1')
    True

    Odd doctest formatting above due to py3's switch from int to enums
    for :mod:`socket` constants.

    """
    if not host:
        return None, ''
    if ':' in host and '[' == host[0] and ']' == host[-1]:
        host = host[1:-1]
        try:
            inet_pton(socket.AF_INET6, host)
        except OSError as se:
            raise URLParseError(f'invalid IPv6 host: {host!r} ({se!r})')
        except UnicodeEncodeError:
            pass  # TODO: this can't be a real host right?
        else:
            family = socket.AF_INET6
            return family, host
    try:
        inet_pton(socket.AF_INET, host)
    except (OSError, UnicodeEncodeError):
        family = None  # not an IP
    else:
        family = socket.AF_INET
    return family, host


def parse_url(url_text):
    """\
    Used to parse the text for a single URL into a dictionary, used
    internally by the :class:`URL` type.

    Note that "URL" has a very narrow, standards-based
    definition. While :func:`parse_url` may raise
    :class:`URLParseError` under a very limited number of conditions,
    such as non-integer port, a surprising number of strings are
    technically valid URLs. For instance, the text ``"url"`` is a
    valid URL, because it is a relative path.

    In short, do not expect this function to validate form inputs or
    other more colloquial usages of URLs.

    >>> res = parse_url('http://127.0.0.1:3000/?a=1')
    >>> sorted(res.keys())  # res is a basic dictionary
    ['_netloc_sep', 'authority', 'family', 'fragment', 'host', 'password', 'path', 'port', 'query', 'scheme', 'username']
    """
    url_text = str(url_text)
    # raise TypeError('parse_url expected text, not %r' % url_str)
    um = _URL_RE.match(url_text)
    try:
        gs = um.groupdict()
    except AttributeError:
        raise URLParseError('could not parse url: %r' % url_text)

    au_text = gs['authority']
    user, pw, hostinfo = None, None, au_text

    if au_text:
        userinfo, sep, hostinfo = au_text.rpartition('@')
        if sep:
            # TODO: empty userinfo error?
            user, _, pw = userinfo.partition(':')

    host, port = None, None
    if hostinfo:
        host, sep, port_str = hostinfo.partition(':')
        if sep:
            if host and host[0] == '[' and ']' in port_str:
                host_right, _, port_str = port_str.partition(']')
                host = host + ':' + host_right + ']'
                if port_str and port_str[0] == ':':
                    port_str = port_str[1:]

            try:
                port = int(port_str)
            except ValueError:
                if port_str:  # empty ports ok according to RFC 3986 6.2.3
                    raise URLParseError('expected integer for port, not %r'
                                        % port_str)
                port = None

    family, host = parse_host(host)

    gs['username'] = user
    gs['password'] = pw
    gs['family'] = family
    gs['host'] = host
    gs['port'] = port
    return gs


DEFAULT_PARSED_URL = parse_url('')


def parse_qsl(qs, keep_blank_values=True, encoding=DEFAULT_ENCODING):
    """
    Converts a query string into a list of (key, value) pairs.
    """
    pairs = [s2 for s1 in qs.split('&') for s2 in s1.split(';')]
    ret = []
    for pair in pairs:
        if not pair:
            continue
        key, _, value = pair.partition('=')
        if not value:
            if keep_blank_values:
                value = None
            else:
                continue
        key = unquote(key.replace('+', ' '))
        if value:
            value = unquote(value.replace('+', ' '))
        ret.append((key, value))
    return ret


"""
# What follows is the OrderedMultiDict from dictutils.py, circa
# 20161021, used for the QueryParamDict, toward the bottom.
"""

from collections.abc import KeysView, ValuesView, ItemsView
from itertools import zip_longest

try:
    from .typeutils import make_sentinel
    _MISSING = make_sentinel(var_name='_MISSING')
except ImportError:
    _MISSING = object()


PREV, NEXT, KEY, VALUE, SPREV, SNEXT = range(6)


class OrderedMultiDict(dict):
    """A MultiDict is a dictionary that can have multiple values per key
    and the OrderedMultiDict (OMD) is a MultiDict that retains
    original insertion order. Common use cases include:

      * handling query strings parsed from URLs
      * inverting a dictionary to create a reverse index (values to keys)
      * stacking data from multiple dictionaries in a non-destructive way

    The OrderedMultiDict constructor is identical to the built-in
    :class:`dict`, and overall the API constitutes an intuitive
    superset of the built-in type:

    >>> omd = OrderedMultiDict()
    >>> omd['a'] = 1
    >>> omd['b'] = 2
    >>> omd.add('a', 3)
    >>> omd.get('a')
    3
    >>> omd.getlist('a')
    [1, 3]

    Some non-:class:`dict`-like behaviors also make an appearance,
    such as support for :func:`reversed`:

    >>> list(reversed(omd))
    ['b', 'a']

    Note that unlike some other MultiDicts, this OMD gives precedence
    to the most recent value added. ``omd['a']`` refers to ``3``, not
    ``1``.

    >>> omd
    OrderedMultiDict([('a', 1), ('b', 2), ('a', 3)])
    >>> omd.poplast('a')
    3
    >>> omd
    OrderedMultiDict([('a', 1), ('b', 2)])
    >>> omd.pop('a')
    1
    >>> omd
    OrderedMultiDict([('b', 2)])

    If you want a safe-to-modify or flat dictionary, use
    :meth:`OrderedMultiDict.todict()`.

    >>> from pprint import pprint as pp  # preserve printed ordering
    >>> omd = OrderedMultiDict([('a', 1), ('b', 2), ('a', 3)])
    >>> pp(omd.todict())
    {'a': 3, 'b': 2}
    >>> pp(omd.todict(multi=True))
    {'a': [1, 3], 'b': [2]}

    With ``multi=False``, items appear with the keys in to original
    insertion order, alongside the most-recently inserted value for
    that key.

    >>> OrderedMultiDict([('a', 1), ('b', 2), ('a', 3)]).items(multi=False)
    [('a', 3), ('b', 2)]

    .. warning::

       ``dict(omd)`` changed behavior `in Python 3.7
       <https://bugs.python.org/issue34320>`_ due to changes made to
       support the transition from :class:`collections.OrderedDict` to
       the built-in dictionary being ordered. Before 3.7, the result
       would be a new dictionary, with values that were lists, similar
       to ``omd.todict(multi=True)`` (but only shallow-copy; the lists
       were direct references to OMD internal structures). From 3.7
       onward, the values became singular, like
       ``omd.todict(multi=False)``. For reliable cross-version
       behavior, just use :meth:`~OrderedMultiDict.todict()`.

    """
    def __new__(cls, *a, **kw):
        ret = super().__new__(cls)
        ret._clear_ll()
        return ret 
    
    def __init__(self, *args, **kwargs):
        if len(args) > 1:
            raise TypeError('%s expected at most 1 argument, got %s'
                            % (self.__class__.__name__, len(args)))
        super().__init__()

        if args:
            self.update_extend(args[0])
        if kwargs:
            self.update(kwargs)

    def __getstate__(self):
        return list(self.iteritems(multi=True))

    def __setstate__(self, state):
        self.clear()
        self.update_extend(state)

    def _clear_ll(self):
        try:
            _map = self._map
        except AttributeError:
            _map = self._map = {}
            self.root = []
        _map.clear()
        self.root[:] = [self.root, self.root, None]

    def _insert(self, k, v):
        root = self.root
        cells = self._map.setdefault(k, [])
        last = root[PREV]
        cell = [last, root, k, v]
        last[NEXT] = root[PREV] = cell
        cells.append(cell)

    def add(self, k, v):
        """Add a single value *v* under a key *k*. Existing values under *k*
        are preserved.
        """
        values = super().setdefault(k, [])
        self._insert(k, v)
        values.append(v)

    def addlist(self, k, v):
        """Add an iterable of values underneath a specific key, preserving
        any values already under that key.

        >>> omd = OrderedMultiDict([('a', -1)])
        >>> omd.addlist('a', range(3))
        >>> omd
        OrderedMultiDict([('a', -1), ('a', 0), ('a', 1), ('a', 2)])

        Called ``addlist`` for consistency with :meth:`getlist`, but
        tuples and other sequences and iterables work.
        """
        if not v:
            return
        self_insert = self._insert
        values = super().setdefault(k, [])
        for subv in v:
            self_insert(k, subv)
        values.extend(v)

    def get(self, k, default=None):
        """Return the value for key *k* if present in the dictionary, else
        *default*. If *default* is not given, ``None`` is returned.
        This method never raises a :exc:`KeyError`.

        To get all values under a key, use :meth:`OrderedMultiDict.getlist`.
        """
        return super().get(k, [default])[-1]

    def getlist(self, k, default=_MISSING):
        """Get all values for key *k* as a list, if *k* is in the
        dictionary, else *default*. The list returned is a copy and
        can be safely mutated. If *default* is not given, an empty
        :class:`list` is returned.
        """
        try:
            return super().__getitem__(k)[:]
        except KeyError:
            if default is _MISSING:
                return []
            return default

    def clear(self):
        "Empty the dictionary."
        super().clear()
        self._clear_ll()

    def setdefault(self, k, default=_MISSING):
        """If key *k* is in the dictionary, return its value. If not, insert
        *k* with a value of *default* and return *default*. *default*
        defaults to ``None``. See :meth:`dict.setdefault` for more
        information.
        """
        if not super().__contains__(k):
            self[k] = None if default is _MISSING else default
        return self[k]

    def copy(self):
        "Return a shallow copy of the dictionary."
        return self.__class__(self.iteritems(multi=True))

    @classmethod
    def fromkeys(cls, keys, default=None):
        """Create a dictionary from a list of keys, with all the values
        set to *default*, or ``None`` if *default* is not set.
        """
        return cls([(k, default) for k in keys])

    def update(self, E, **F):
        """Add items from a dictionary or iterable (and/or keyword arguments),
        overwriting values under an existing key. See
        :meth:`dict.update` for more details.
        """
        # E and F are throwback names to the dict() __doc__
        if E is self:
            return
        self_add = self.add
        if isinstance(E, OrderedMultiDict):
            for k in E:
                if k in self:
                    del self[k]
            for k, v in E.iteritems(multi=True):
                self_add(k, v)
        elif callable(getattr(E, 'keys', None)):
            for k in E.keys():
                self[k] = E[k]
        else:
            seen = set()
            seen_add = seen.add
            for k, v in E:
                if k not in seen and k in self:
                    del self[k]
                    seen_add(k)
                self_add(k, v)
        for k in F:
            self[k] = F[k]
        return

    def update_extend(self, E, **F):
        """Add items from a dictionary, iterable, and/or keyword
        arguments without overwriting existing items present in the
        dictionary. Like :meth:`update`, but adds to existing keys
        instead of overwriting them.
        """
        if E is self:
            iterator = iter(E.items())
        elif isinstance(E, OrderedMultiDict):
            iterator = E.iteritems(multi=True)
        elif hasattr(E, 'keys'):
            iterator = ((k, E[k]) for k in E.keys())
        else:
            iterator = E

        self_add = self.add
        for k, v in iterator:
            self_add(k, v)

    def __setitem__(self, k, v):
        if super().__contains__(k):
            self._remove_all(k)
        self._insert(k, v)
        super().__setitem__(k, [v])

    def __getitem__(self, k):
        return super().__getitem__(k)[-1]

    def __delitem__(self, k):
        super().__delitem__(k)
        self._remove_all(k)

    def __eq__(self, other):
        if self is other:
            return True
        try:
            if len(other) != len(self):
                return False
        except TypeError:
            return False
        if isinstance(other, OrderedMultiDict):
            selfi = self.iteritems(multi=True)
            otheri = other.iteritems(multi=True)
            zipped_items = zip_longest(selfi, otheri, fillvalue=(None, None))
            for (selfk, selfv), (otherk, otherv) in zipped_items:
                if selfk != otherk or selfv != otherv:
                    return False
            if not(next(selfi, _MISSING) is _MISSING
                   and next(otheri, _MISSING) is _MISSING):
                # leftovers  (TODO: watch for StopIteration?)
                return False
            return True
        elif hasattr(other, 'keys'):
            for selfk in self:
                try:
                    other[selfk] == self[selfk]
                except KeyError:
                    return False
            return True
        return False

    def __ne__(self, other):
        return not (self == other)

    def __ior__(self, other):
        self.update(other)
        return self

    def pop(self, k, default=_MISSING):
        """Remove all values under key *k*, returning the most-recently
        inserted value. Raises :exc:`KeyError` if the key is not
        present and no *default* is provided.
        """
        try:
            return self.popall(k)[-1]
        except KeyError:
            if default is _MISSING:
                raise KeyError(k)
        return default

    def popall(self, k, default=_MISSING):
        """Remove all values under key *k*, returning them in the form of
        a list. Raises :exc:`KeyError` if the key is not present and no
        *default* is provided.
        """
        super_self = super()
        if super_self.__contains__(k):
            self._remove_all(k)
        if default is _MISSING:
            return super_self.pop(k)
        return super_self.pop(k, default)

    def poplast(self, k=_MISSING, default=_MISSING):
        """Remove and return the most-recently inserted value under the key
        *k*, or the most-recently inserted key if *k* is not
        provided. If no values remain under *k*, it will be removed
        from the OMD.  Raises :exc:`KeyError` if *k* is not present in
        the dictionary, or the dictionary is empty.
        """
        if k is _MISSING:
            if self:
                k = self.root[PREV][KEY]
            else:
                if default is _MISSING:
                    raise KeyError('empty %r' % type(self))
                return default
        try:
            self._remove(k)
        except KeyError:
            if default is _MISSING:
                raise KeyError(k)
            return default
        values = super().__getitem__(k)
        v = values.pop()
        if not values:
            super().__delitem__(k)
        return v

    def _remove(self, k):
        values = self._map[k]
        cell = values.pop()
        cell[PREV][NEXT], cell[NEXT][PREV] = cell[NEXT], cell[PREV]
        if not values:
            del self._map[k]

    def _remove_all(self, k):
        values = self._map[k]
        while values:
            cell = values.pop()
            cell[PREV][NEXT], cell[NEXT][PREV] = cell[NEXT], cell[PREV]
        del self._map[k]

    def iteritems(self, multi=False):
        """Iterate over the OMD's items in insertion order. By default,
        yields only the most-recently inserted value for each key. Set
        *multi* to ``True`` to get all inserted items.
        """
        root = self.root
        curr = root[NEXT]
        if multi:
            while curr is not root:
                yield curr[KEY], curr[VALUE]
                curr = curr[NEXT]
        else:
            for key in self.iterkeys():
                yield key, self[key]

    def iterkeys(self, multi=False):
        """Iterate over the OMD's keys in insertion order. By default, yields
        each key once, according to the most recent insertion. Set
        *multi* to ``True`` to get all keys, including duplicates, in
        insertion order.
        """
        root = self.root
        curr = root[NEXT]
        if multi:
            while curr is not root:
                yield curr[KEY]
                curr = curr[NEXT]
        else:
            yielded = set()
            yielded_add = yielded.add
            while curr is not root:
                k = curr[KEY]
                if k not in yielded:
                    yielded_add(k)
                    yield k
                curr = curr[NEXT]

    def itervalues(self, multi=False):
        """Iterate over the OMD's values in insertion order. By default,
        yields the most-recently inserted value per unique key.  Set
        *multi* to ``True`` to get all values according to insertion
        order.
        """
        for k, v in self.iteritems(multi=multi):
            yield v

    def todict(self, multi=False):
        """Gets a basic :class:`dict` of the items in this dictionary. Keys
        are the same as the OMD, values are the most recently inserted
        values for each key.

        Setting the *multi* arg to ``True`` is yields the same
        result as calling :class:`dict` on the OMD, except that all the
        value lists are copies that can be safely mutated.
        """
        if multi:
            return {k: self.getlist(k) for k in self}
        return {k: self[k] for k in self}

    def sorted(self, key=None, reverse=False):
        """Similar to the built-in :func:`sorted`, except this method returns
        a new :class:`OrderedMultiDict` sorted by the provided key
        function, optionally reversed.

        Args:
            key (callable): A callable to determine the sort key of
              each element. The callable should expect an **item**
              (key-value pair tuple).
            reverse (bool): Set to ``True`` to reverse the ordering.

        >>> omd = OrderedMultiDict(zip(range(3), range(3)))
        >>> omd.sorted(reverse=True)
        OrderedMultiDict([(2, 2), (1, 1), (0, 0)])

        Note that the key function receives an **item** (key-value
        tuple), so the recommended signature looks like:

        >>> omd = OrderedMultiDict(zip('hello', 'world'))
        >>> omd.sorted(key=lambda i: i[1])  # i[0] is the key, i[1] is the val
        OrderedMultiDict([('o', 'd'), ('l', 'l'), ('e', 'o'), ('l', 'r'), ('h', 'w')])
        """
        cls = self.__class__
        return cls(sorted(self.iteritems(multi=True), key=key, reverse=reverse))

    def sortedvalues(self, key=None, reverse=False):
        """Returns a copy of the :class:`OrderedMultiDict` with the same keys
        in the same order as the original OMD, but the values within
        each keyspace have been sorted according to *key* and
        *reverse*.

        Args:
            key (callable): A single-argument callable to determine
              the sort key of each element. The callable should expect
              an **item** (key-value pair tuple).
            reverse (bool): Set to ``True`` to reverse the ordering.

        >>> omd = OrderedMultiDict()
        >>> omd.addlist('even', [6, 2])
        >>> omd.addlist('odd', [1, 5])
        >>> omd.add('even', 4)
        >>> omd.add('odd', 3)
        >>> somd = omd.sortedvalues()
        >>> somd.getlist('even')
        [2, 4, 6]
        >>> somd.keys(multi=True) == omd.keys(multi=True)
        True
        >>> omd == somd
        False
        >>> somd
        OrderedMultiDict([('even', 2), ('even', 4), ('odd', 1), ('odd', 3), ('even', 6), ('odd', 5)])

        As demonstrated above, contents and key order are
        retained. Only value order changes.
        """
        try:
            superself_iteritems = super().iteritems()
        except AttributeError:
            superself_iteritems = super().items()
        # (not reverse) because they pop off in reverse order for reinsertion
        sorted_val_map = {k: sorted(v, key=key, reverse=(not reverse))
                               for k, v in superself_iteritems}
        ret = self.__class__()
        for k in self.iterkeys(multi=True):
            ret.add(k, sorted_val_map[k].pop())
        return ret

    def inverted(self):
        """Returns a new :class:`OrderedMultiDict` with values and keys
        swapped, like creating dictionary transposition or reverse
        index.  Insertion order is retained and all keys and values
        are represented in the output.

        >>> omd = OMD([(0, 2), (1, 2)])
        >>> omd.inverted().getlist(2)
        [0, 1]

        Inverting twice yields a copy of the original:

        >>> omd.inverted().inverted()
        OrderedMultiDict([(0, 2), (1, 2)])
        """
        return self.__class__((v, k) for k, v in self.iteritems(multi=True))

    def counts(self):
        """Returns a mapping from key to number of values inserted under that
        key. Like :py:class:`collections.Counter`, but returns a new
        :class:`OrderedMultiDict`.
        """
        # Returns an OMD because Counter/OrderedDict may not be
        # available, and neither Counter nor dict maintain order.
        super_getitem = super().__getitem__
        return self.__class__((k, len(super_getitem(k))) for k in self)

    def keys(self, multi=False):
        """Returns a list containing the output of :meth:`iterkeys`.  See
        that method's docs for more details.
        """
        return list(self.iterkeys(multi=multi))

    def values(self, multi=False):
        """Returns a list containing the output of :meth:`itervalues`.  See
        that method's docs for more details.
        """
        return list(self.itervalues(multi=multi))

    def items(self, multi=False):
        """Returns a list containing the output of :meth:`iteritems`.  See
        that method's docs for more details.
        """
        return list(self.iteritems(multi=multi))

    def __iter__(self):
        return self.iterkeys()

    def __reversed__(self):
        root = self.root
        curr = root[PREV]
        lengths = {}
        lengths_sd = lengths.setdefault
        get_values = super().__getitem__
        while curr is not root:
            k = curr[KEY]
            vals = get_values(k)
            if lengths_sd(k, 1) == len(vals):
                yield k
            lengths[k] += 1
            curr = curr[PREV]

    def __repr__(self):
        cn = self.__class__.__name__
        kvs = ', '.join([repr((k, v)) for k, v in self.iteritems(multi=True)])
        return f'{cn}([{kvs}])'

    def viewkeys(self):
        "OMD.viewkeys() -> a set-like object providing a view on OMD's keys"
        return KeysView(self)

    def viewvalues(self):
        "OMD.viewvalues() -> an object providing a view on OMD's values"
        return ValuesView(self)

    def viewitems(self):
        "OMD.viewitems() -> a set-like object providing a view on OMD's items"
        return ItemsView(self)



try:
    # try to import the built-in one anyways
    from .dictutils import OrderedMultiDict
except ImportError:
    pass

OMD = OrderedMultiDict


class QueryParamDict(OrderedMultiDict):
    """A subclass of :class:`~dictutils.OrderedMultiDict` specialized for
    representing query string values. Everything is fully unquoted on
    load and all parsed keys and values are strings by default.

    As the name suggests, multiple values are supported and insertion
    order is preserved.

    >>> qp = QueryParamDict.from_text(u'key=val1&key=val2&utm_source=rtd')
    >>> qp.getlist('key')
    [u'val1', u'val2']
    >>> qp['key']
    u'val2'
    >>> qp.add('key', 'val3')
    >>> qp.to_text()
    'key=val1&key=val2&utm_source=rtd&key=val3'

    See :class:`~dictutils.OrderedMultiDict` for more API features.
    """

    @classmethod
    def from_text(cls, query_string):
        """
        Parse *query_string* and return a new :class:`QueryParamDict`.
        """
        pairs = parse_qsl(query_string, keep_blank_values=True)
        return cls(pairs)

    def to_text(self, full_quote=False):
        """
        Render and return a query string.

        Args:
           full_quote (bool): Whether or not to percent-quote special
              characters or leave them decoded for readability.
        """
        ret_list = []
        for k, v in self.iteritems(multi=True):
            key = quote_query_part(to_unicode(k), full_quote=full_quote)
            if v is None:
                ret_list.append(key)
            else:
                val = quote_query_part(to_unicode(v), full_quote=full_quote)
                ret_list.append('='.join((key, val)))
        return '&'.join(ret_list)

# end urlutils.py
