"""URL normalize main module.

Copyright (c) 2020 Nikolay Panov
This module is part of url-normalize package and is released under the MIT License:
https://opensource.org/licenses/MIT

"""

from __future__ import annotations

from .generic_url_cleanup import generic_url_cleanup
from .normalize_fragment import normalize_fragment
from .normalize_host import DEFAULT_CHARSET, normalize_host
from .normalize_path import normalize_path
from .normalize_port import normalize_port
from .normalize_query import normalize_query
from .normalize_scheme import DEFAULT_SCHEME, normalize_scheme
from .normalize_userinfo import normalize_userinfo
from .provide_url_domain import provide_url_domain
from .provide_url_scheme import provide_url_scheme
from .tools import deconstruct_url, reconstruct_url


def url_normalize(  # noqa: PLR0913
    url: str | None,
    *,  # Force keyword-only arguments
    charset: str = DEFAULT_CHARSET,
    default_scheme: str = DEFAULT_SCHEME,
    default_domain: str | None = None,
    filter_params: bool = False,
    param_allowlist: dict | list | None = None,
) -> str | None:
    """URI normalization routine.

    Sometimes you get an URL by a user that just isn't a real
    URL because it contains unsafe characters like ' ' and so on.
    This function can fix some of the problems in a similar way
    browsers handle data entered by the user:

    >>> url_normalize('http://de.wikipedia.org/wiki/Elf (Begriffsklärung)')
    'http://de.wikipedia.org/wiki/Elf%20%28Begriffskl%C3%A4rung%29'

    Params:
        url : str | None : URL to normalize
        charset : str : optional
            The target charset for the URL if the url was given as unicode string
        default_scheme : str : default scheme to use if none present
        default_domain : str | None : optional
            Default domain to use for absolute paths (starting with '/')
        filter_params : bool : optional
            Whether to filter non-allowlisted parameters (False by default)
        param_allowlist : dict | list | None : optional
            Override for the parameter allowlist

    Returns:
        str | None : a normalized url

    """
    if not url:
        return url
    url = provide_url_domain(url, default_domain)
    url = provide_url_scheme(url, default_scheme)
    url = generic_url_cleanup(url)
    url_elements = deconstruct_url(url)
    url_elements = url_elements._replace(
        scheme=normalize_scheme(url_elements.scheme),
        userinfo=normalize_userinfo(url_elements.userinfo),
        host=normalize_host(url_elements.host, charset),
        query=normalize_query(
            url_elements.query,
            host=url_elements.host,
            filter_params=filter_params,
            param_allowlist=param_allowlist,
        ),
        fragment=normalize_fragment(url_elements.fragment),
    )
    url_elements = url_elements._replace(
        port=normalize_port(url_elements.port, url_elements.scheme),
        path=normalize_path(url_elements.path, url_elements.scheme),
    )
    return reconstruct_url(url_elements)
