#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype metadata.**

This submodule exports global constants synopsizing this package -- including
versioning and dependencies.

Python Version
--------------
For uniformity between this codebase and the ``setup.py`` setuptools script
importing this module, this module also validates the version of the active
Python 3 interpreter. An exception is raised if this version is insufficient.

As a tradeoff between backward compatibility, security, and maintainability,
this package strongly attempts to preserve compatibility with the first stable
release of the oldest version of CPython still under active development. Hence,
obsolete and insecure versions of CPython that have reached their official End
of Life (EoL) (e.g., Python 3.5) are explicitly unsupported.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# CAUTION: To avoid accidental importation of optional runtime dependencies
# (e.g., "typing-extensions") at installation time *BEFORE* the current package
# manager has installed those dependencies, this module may *NOT* import from
# any submodules of the current package. This includes *ALL* "beartype._util"
# submodules, most of which import from "beartype.typing", which conditionally
# imports optional runtime dependencies under certain contexts.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# CAUTION: To avoid race conditions during setuptools-based installation, this
# module may import *ONLY* from modules guaranteed to exist at the start of
# installation. This includes all standard Python and package modules but
# *NOT* third-party dependencies, which if currently uninstalled will only be
# installed at some later time in the installation.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# CAUTION: To avoid polluting the public module namespace, external attributes
# should be locally imported at module scope *ONLY* under alternate private
# names (e.g., "from argparse import ArgumentParser as _ArgumentParser" rather
# than merely "from argparse import ArgumentParser").
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

import sys as _sys
# from beartype.typing import Tuple as _Tuple

# ....................{ METADATA                           }....................
NAME = 'beartype'
'''
Human-readable package name.
'''


LICENSE = 'MIT'
'''
Human-readable name of the license this package is licensed under.
'''

# ....................{ METADATA ~ package                 }....................
PACKAGE_NAME = NAME.lower()
'''
Fully-qualified name of the top-level Python package containing this submodule.
'''


PACKAGE_TEST_NAME = f'{PACKAGE_NAME}_test'
'''
Fully-qualified name of the top-level Python package exercising this project.
'''

# ....................{ PYTHON ~ version                   }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: Changes to this section *MUST* be synchronized with:
# * Signs declared by the private
#   "beartype._data.hint.pep.datapepsign" submodule, which *MUST*
#   be synchronized against the "__all__" dunder list global of the "typing"
#   module bundled with the most recent CPython release.
# * Continuous integration test matrices, including:
#   * The top-level "tox.ini" file.
#   * The "jobs/tests/strategy/matrix/{tox-env,include/python-version}"
#     settings of the GitHub Actions-specific
#     ".github/workflows/python_test.yml" file.
# * Front-facing documentation (e.g., "README.rst", "doc/md/INSTALL.md").
#
# On bumping the minimum required version of Python, consider also documenting
# the justification for doing so in the "Python Version" section of this
# submodule's docstring above.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

PYTHON_VERSION_MIN = '3.8.0'
'''
Human-readable minimum version of Python required by this package as a
``.``-delimited string.

See Also
--------
"Python Version" section of this submodule's docstring for a detailed
justification of this constant's current value.
'''


PYTHON_VERSION_MINOR_MAX = 13
'''
Maximum minor stable version of this major version of Python currently released
(e.g., ``5`` if Python 3.5 is the most recent stable version of Python 3.x).
'''


def _convert_version_str_to_tuple(version_str: str):  # -> _Tuple[int, ...]:
    '''
    Convert the passed human-readable ``.``-delimited version string into a
    machine-readable version tuple of corresponding integers.
    '''
    assert isinstance(version_str, str), f'"{version_str}" not version string.'

    return tuple(int(version_part) for version_part in version_str.split('.'))


PYTHON_VERSION_MIN_PARTS = _convert_version_str_to_tuple(PYTHON_VERSION_MIN)
'''
Machine-readable minimum version of Python required by this package as a
tuple of integers.
'''


_PYTHON_VERSION_PARTS = _sys.version_info[:3]
'''
Machine-readable current version of the active Python interpreter as a
tuple of integers.
'''


# Validate the version of the active Python interpreter *BEFORE* subsequent
# code possibly depending on this version. Since this version should be
# validated both at setuptools-based install time and post-install runtime
# *AND* since this module is imported sufficiently early by both, stash this
# validation here to avoid duplication of this logic and hence the hardcoded
# Python version.
#
# The "sys" module exposes three version-related constants for this purpose:
# * "hexversion", an integer intended to be specified in an obscure (albeit
#   both efficient and dependable) hexadecimal format: e.g.,
#    >>> sys.hexversion
#    33883376
#    >>> '%x' % sys.hexversion
#    '20504f0'
# * "version", a human-readable string: e.g.,
#    >>> sys.version
#    2.5.2 (r252:60911, Jul 31 2008, 17:28:52)
#    [GCC 4.2.3 (Ubuntu 4.2.3-2ubuntu7)]
# * "version_info", a tuple of three or more integers *OR* strings: e.g.,
#    >>> sys.version_info
#    (2, 5, 2, 'final', 0)
#
# For sanity, this package will *NEVER* conditionally depend upon the
# string-formatted release type of the current Python version exposed via the
# fourth element of the "version_info" tuple. Since the first three elements of
# that tuple are guaranteed to be integers *AND* since a comparable 3-tuple of
# integers is declared above, comparing the former and latter yield the
# simplest and most reliable Python version test.
#
# Note that the nearly decade-old and officially accepted PEP 345 proposed a
# new field "requires_python" configured via a key-value pair passed to the
# call to setup() in "setup.py" (e.g., "requires_python = ['>=2.2.1'],"), that
# field has yet to be integrated into either disutils or setuputils. Hence,
# that field is validated manually in the typical way.
if _PYTHON_VERSION_PARTS < PYTHON_VERSION_MIN_PARTS:
    # Human-readable current version of Python. Ideally, "sys.version" would be
    # leveraged here instead; sadly, that string embeds significantly more than
    # merely a version and hence is inapplicable for real-world usage: e.g.,
    #
    #     >>> import sys
    #     >>> sys.version
    #     '3.6.5 (default, Oct 28 2018, 19:51:39) \n[GCC 7.3.0]'
    _PYTHON_VERSION = '.'.join(
        str(version_part) for version_part in _sys.version_info[:3])

    # Die ignominiously.
    raise RuntimeError(
        f'{NAME} requires at least Python {PYTHON_VERSION_MIN}, but '
        f'the active interpreter only targets Python {_PYTHON_VERSION}. '
        f'We feel unbearable sadness for you.'
    )

# ....................{ METADATA ~ version                 }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: When modifying the current version of this package below,
# consider adhering to the Semantic Versioning schema. Specifically, the
# version should consist of three "."-delimited integers
# "{major}.{minor}.{patch}", where:
#
# * "{major}" specifies the major version, incremented only when either:
#   * Breaking backward compatibility in this package's public API.
#   * Implementing headline-worthy functionality (e.g., a GUI). Technically,
#     this condition breaks the Semantic Versioning schema, which stipulates
#     that *ONLY* changes breaking backward compatibility warrant major bumps.
#     But this is the real world. In the real world, significant improvements
#     are rewarded with significant version changes.
#   In either case, the minor and patch versions both reset to 0.
# * "{minor}" specifies the minor version, incremented only when implementing
#   customary functionality in a manner preserving such compatibility. In this
#   case, the patch version resets to 0.
# * "{patch}" specifies the patch version, incremented only when correcting
#   outstanding issues in a manner preserving such compatibility.
#
# When in doubt, increment only the minor version and reset the patch version.
# For further details, see http://semver.org.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

VERSION = '0.16.4'
'''
Human-readable package version as a ``.``-delimited string.
'''


VERSION_PARTS = _convert_version_str_to_tuple(VERSION)
'''
Machine-readable package version as a tuple of integers.
'''

# ....................{ METADATA ~ synopsis                }....................
SYNOPSIS = 'Unbearably fast runtime type checking in pure Python.'
'''
Human-readable single-line synopsis of this package.

By PyPI design, this string must *not* span multiple lines or paragraphs.
'''

# ....................{ METADATA ~ authors                 }....................
AUTHOR_EMAIL = 'leycec@gmail.com'
'''
Email address of the principal corresponding author (i.e., the principal author
responding to public correspondence).
'''


AUTHORS = 'Cecil Curry, et al.'
'''
Human-readable list of all principal authors of this package as a
comma-delimited string.

For brevity, this string *only* lists authors explicitly assigned copyrights.
For the list of all contributors regardless of copyright assignment or
attribution, see the `contributors graph`_ for this project.

.. _contributors graph:
   https://github.com/beartype/beartype/graphs/contributors
'''


COPYRIGHT = '2014-2023 Beartype authors'
'''
Legally binding copyright line excluding the license-specific prefix (e.g.,
``"Copyright (c)"``).

For brevity, this string *only* lists authors explicitly assigned copyrights.
For the list of all contributors regardless of copyright assignment or
attribution, see the `contributors graph`_ for this project.

.. _contributors graph:
   https://github.com/beartype/beartype/graphs/contributors
'''

# ....................{ METADATA ~ urls                    }....................
URL_CONDA = f'https://anaconda.org/conda-forge/{PACKAGE_NAME}'
'''
URL of this project's entry on **Anaconda** (i.e., alternate third-party Python
package repository utilized by the Anaconda Python distribution).
'''


URL_LIBRARIES = f'https://libraries.io/pypi/{PACKAGE_NAME}'
'''
URL of this project's entry on **Libraries.io** (i.e., third-party open-source
package registrar associated with the Tidelift open-source funding agency).
'''


URL_PYPI = f'https://pypi.org/project/{PACKAGE_NAME}'
'''
URL of this project's entry on **PyPI** (i.e., official Python package
repository, also colloquially known as the "cheeseshop").
'''


URL_RTD = f'https://readthedocs.org/projects/{PACKAGE_NAME}'
'''
URL of this project's entry on **ReadTheDocs (RTD)** (i.e., popular Python
documentation host, shockingly hosting this project's documentation).
'''

# ....................{ METADATA ~ urls : docs             }....................
URL_HOMEPAGE = f'https://{PACKAGE_NAME}.readthedocs.io'
'''
URL of this project's homepage.
'''


URL_PEP585_DEPRECATIONS = (
    f'{URL_HOMEPAGE}/en/latest/api_roar/#pep-585-deprecations')
'''
URL documenting :pep:`585` deprecations of :pep:`484` type hints.
'''

# ....................{ METADATA ~ urls : repo             }....................
URL_REPO_ORG_NAME = PACKAGE_NAME
'''
Name of the **organization** (i.e., parent group or user principally responsible
for maintaining this project, indicated as the second-to-last trailing
subdirectory component) of the URL of this project's git repository.
'''


URL_REPO_BASENAME = PACKAGE_NAME
'''
**Basename** (i.e., trailing subdirectory component) of the URL of this
project's git repository.
'''


URL_REPO = f'https://github.com/{URL_REPO_ORG_NAME}/{URL_REPO_BASENAME}'
'''
URL of this project's git repository.
'''


URL_DOWNLOAD = f'{URL_REPO}/archive/{VERSION}.tar.gz'
'''
URL of the source tarball for the current version of this project.

This URL assumes a tag whose name is ``v{VERSION}`` where ``{VERSION}`` is the
human-readable current version of this project (e.g., ``v0.4.0``) to exist.
Typically, no such tag exists for live versions of this project -- which
have yet to be stabilized and hence tagged. Hence, this URL is typically valid
*only* for previously released (rather than live) versions of this project.
'''


URL_FORUMS = f'{URL_REPO}/discussions'
'''
URL of this project's user forums.
'''


URL_ISSUES = f'{URL_REPO}/issues'
'''
URL of this project's issue tracker.
'''


URL_RELEASES = f'{URL_REPO}/releases'
'''
URL of this project's release list.
'''

# ....................{ METADATA ~ libs : runtime          }....................
_LIB_RUNTIME_OPTIONAL_VERSION_MINIMUM_NUMPY = '1.21.0'
'''
Minimum optional version of NumPy recommended for use with this project.

NumPy >= 1.21.0 first introduced the third-party PEP-noncompliant
:attr:`numpy.typing.NDArray` type hint supported by the
:func:`beartype.beartype` decorator.
'''


_LIB_RUNTIME_OPTIONAL_VERSION_MINIMUM_TYPING_EXTENSIONS = '3.10.0.0'
'''
Minimum optional version of the third-party :mod:`typing_extensions` package
recommended for use with this project.

:mod:`typing_extensions` >= 3.10.0.0 backports all :mod:`typing` attributes
unavailable under older Python interpreters supported by the
:func:`beartype.beartype` decorator.
'''


# Note that we intentionally omit NumPy here, because:
# * If you want it, you're already using it.
# * If you do *NOT* want it, you're *NOT* already using it.
LIBS_RUNTIME_OPTIONAL = (
    (
        f'typing-extensions >='
        f'{_LIB_RUNTIME_OPTIONAL_VERSION_MINIMUM_TYPING_EXTENSIONS}'
    ),
)
'''
Optional runtime package dependencies as a tuple of :mod:`setuptools`-specific
requirements strings of the format ``{project_name}
{comparison1}{version1},...,{comparisonN}{versionN}``, where:

* ``{project_name}`` is a :mod:`setuptools`-specific project name (e.g.,
  ``"numpy"``, ``"scipy"``).
* ``{comparison1}`` and ``{comparisonN}`` are :mod:`setuptools`-specific
  version comparison operators. As well as standard mathematical comparison
  operators (e.g., ``==``, ``>=``, ``<``), :mod:`setuptools` also supports the
  PEP 440-compliant "compatible release" operator ``~=`` more commonly denoted
  by ``^`` in modern package managers (e.g., poetry, npm); this operator
  enables forward compatibility with all future versions of this dependency
  known *not* to break backward compatibility, but should only be applied to
  dependencies strictly following the semantic versioning contract.
* ``{version1}`` and ``{version1}`` are arbitrary version strings (e.g.,
  ``2020.2.16``, ``0.75a2``).
'''

# ....................{ METADATA ~ libs : test : optional  }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# CAUTION: Avoid constraining optional test-time dependencies to version
# ranges, which commonly fail for edge-case test environments -- including:
# * The oldest Python version still supported by @beartype, which typically is
#   *NOT* supported by newer versions of these dependencies.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

LIBS_TESTTIME_OPTIONAL = (
    # Require a reasonably recent version of mypy known to behave well. Less
    # recent versions are significantly deficient with respect to error
    # reporting and *MUST* thus be blacklisted.
    #
    # Note that PyPy currently fails to support mypy. See also this official
    # documentation discussing this regrettable incompatibility:
    #     https://mypy.readthedocs.io/en/stable/faq.html#does-it-run-on-pypy
    'mypy >=0.800; platform_python_implementation != "PyPy"',

    #FIXME: Let's avoid attempting to remotely compile with nuitka under GitHub
    #Actions-hosted continuous integration (CI) for the moment. Doing so is
    #non-trivial enough under local testing workflows. *sigh*
    # Require a reasonably recent version of nuitka if the current platform is a
    # Linux distribution *AND* the active Python interpreter targets Python >=
    # 3.8. For questionable reasons best ignored, nuitka fails to compile
    # beartype under Python <= 3.7.
    # 'nuitka >=1.2.6; sys_platform == "linux" and python_version >= "3.8.0"',

    #FIXME: Consider dropping the 'and platform_python_implementation != "PyPy"'
    #clause now that "tox.ini" installs NumPy wheels from a third-party vendor
    #explicitly supporting PyPy.
    # Require NumPy. NumPy has become *EXTREMELY* non-trivial to install under
    # macOS with "pip", due to the conjunction of multiple issues. These
    # include:
    # * NumPy > 1.18.0, whose initial importation now implicitly detects
    #   whether the BLAS implementation NumPy was linked against is sane and
    #   raises a "RuntimeError" exception if that implementation is insane:
    #       RuntimeError: Polyfit sanity test emitted a warning, most
    #       likely due to using a buggy Accelerate backend. If you
    #       compiled yourself, more information is available at
    #       https://numpy.org/doc/stable/user/building.html#accelerated-blas-lapack-libraries
    #       Otherwise report this to the vendor that provided NumPy.
    #       RankWarning: Polyfit may be poorly conditioned
    # * Apple's blatantly broken multithreaded implementation of their
    #   "Accelerate" BLAS replacement, which neither NumPy nor "pip" have *ANY*
    #   semblance of control over.
    # * "pip" under PyPy, which for unknown reasons fails to properly install
    #   NumPy even when the "--force-reinstall" option is explicitly passed to
    #   "pip". Oddly, passing that option to "pip" under CPython resolves this
    #   issue -- which is why we only selectively disable NumPy installation
    #   under macOS + PyPy.
    #
    # See also this upstream NumPy issue:
    #     https://github.com/numpy/numpy/issues/15947
    (
        'numpy; '
        'sys_platform != "darwin" and '
        'platform_python_implementation != "PyPy"'
    ),

    # Required by optional Pandera-specific integration tests.
    'pandera',

    # Required by optional Sphinx-specific integration tests.
    #
    # Note that Sphinx currently provokes unrelated test failures under Python
    # 3.7 with  obscure deprecation warnings. Since *ALL* of this only applies
    # to Python 3.7, we crudely circumvent this nonsense by simply avoiding
    # installing Sphinx under Python 3.7. The exception resembles:
    #     FAILED
    #     ../../../beartype_test/a00_unit/a20_util/test_utilobject.py::test_is_object_hashable
    #     - beartype.roar.BeartypeModuleUnimportableWarning: Ignoring module
    #     "pkg_resources.__init__" importation exception DeprecationWarning:
    #     Deprecated call to `pkg_resources.declare_namespace('sphinxcontrib')`.
    'sphinx; python_version >= "3.8.0"',

    # Required to exercise third-party backports of type hint factories
    # published by the standard "typing" module under newer versions of Python.
    (
        f'typing-extensions >='
        f'{_LIB_RUNTIME_OPTIONAL_VERSION_MINIMUM_TYPING_EXTENSIONS}'
    ),
)
'''
**Optional developer test-time package dependencies** (i.e., dependencies
recommended to test this package with :mod:`tox` as a developer at the command
line) as a tuple of :mod:`setuptools`-specific requirements strings of the
format ``{project_name} {comparison1}{version1},...,{comparisonN}{versionN}``.

See Also
----------
:data:`LIBS_RUNTIME_OPTIONAL`
    Further details.
'''

# ....................{ METADATA ~ libs : test : mandatory }....................
LIBS_TESTTIME_MANDATORY_COVERAGE = (
    'coverage >=5.5',
)
'''
**Mandatory test-time coverage package dependencies** (i.e., dependencies
required to measure test coverage for this package) as a tuple of
:mod:`setuptools`-specific requirements strings of the format ``{project_name}
{comparison1}{version1},...,{comparisonN}{versionN}``.

See Also
----------
:data:`LIBS_RUNTIME_OPTIONAL`
    Further details.
'''


# For completeness, install *ALL* optional test-time dependencies into *ALL*
# isolated virtual environments managed by "tox". Failure to list *ALL*
# optional test-time dependencies here commonly results in errors from mypy,
# which raises false positives on parsing "import" statements for currently
# uninstalled third-party packages (e.g., "import numpy as np").
LIBS_TESTTIME_MANDATORY_TOX = LIBS_TESTTIME_OPTIONAL + (
    'pytest >=4.0.0',
)
'''
**Mandatory tox test-time package dependencies** (i.e., dependencies required
to test this package under :mod:`tox`) as a tuple of :mod:`setuptools`-specific
requirements strings of the format ``{project_name}
{comparison1}{version1},...,{comparisonN}{versionN}``.

See Also
----------
:data:`LIBS_RUNTIME_OPTIONAL`
    Further details.
'''


LIBS_TESTTIME_MANDATORY = (
    LIBS_TESTTIME_MANDATORY_COVERAGE +
    LIBS_TESTTIME_MANDATORY_TOX + (
        # A relatively modern version of tox is required.
        'tox >=3.20.1',
    )
)
'''
**Mandatory developer test-time package dependencies** (i.e., dependencies
required to test this package with :mod:`tox` as a developer at the command
line) as a tuple of :mod:`setuptools`-specific requirements strings of the
format ``{project_name} {comparison1}{version1},...,{comparisonN}{versionN}``.

See Also
----------
:data:`LIBS_RUNTIME_OPTIONAL`
    Further details.
'''

# ....................{ METADATA ~ libs : doc : sphinx     }....................
_SPHINX_VERSION_MINIMUM = '4.2.0'
'''
Machine-readable minimum (inclusive) version as a ``.``-delimited string of
:mod:`sphinx` required to build package documentation.

Specifically, this project requires:

* :mod:sphinx` >= 4.2.0, which resolved a `severe compatibility issue`_ with
  Python >= 3.10.

.. _severe compatibility issue:
   https://github.com/sphinx-doc/sphinx/issues/9816
'''


#FIXME: Once "pydata-sphinx-theme" 0.13.0 is released:
#* Relax this restriction (e.g., by simply commenting this global out both here
#  and below).
#* Bump "_SPHINX_THEME_VERSION_MAXIMUM >= '0.13.0'" below.
_SPHINX_VERSION_MAXIMUM_EXCLUSIVE = '6.0.0'
'''
Machine-readable maximum (exclusive) version as a ``.``-delimited string of
:mod:`sphinx` required to build package documentation.

Specifically, this project requires:

* :mod:sphinx` < 6.0.0, as more recent versions `currently conflict with our
  Sphinx theme <theme conflict_>`__.

.. _theme conflict:
   https://github.com/sphinx-doc/sphinx/issues/9816
'''

# ....................{ METADATA ~ libs : doc : theme      }....................
#FIXME: Switch! So, "pydata-sphinx-theme" is ostensibly *MOSTLY* great. However,
#there are numerous obvious eccentricities in "pydata-sphinx-theme" that we
#strongly disagree with -- especially that theme's oddball division in TOC
#heading levels between the top and left sidebars.
#
#Enter "sphinx-book-theme", stage left. "sphinx-book-theme" is based on
#"pydata-sphinx-theme", but entirely dispenses with all of the obvious
#eccentricities that hamper usage of "pydata-sphinx-theme". We no longer have
#adequate time to maintain custom documentation CSS against the moving target
#that is "pydata-sphinx-theme". Ergo, we should instead let "sphinx-book-theme"
#do all of that heavy lifting for us. Doing so will enable us to:
#* Lift the horrifying constraint above on a maximum Sphinx version. *gulp*
#* Substantially simplify our Sphinx configuration. Notably, the entire fragile
#  "doc/src/_templates/" subdirectory should be *ENTIRELY* excised away.
#
#Please transition to "sphinx-book-theme" as time permits.
SPHINX_THEME_NAME = 'pydata-sphinx-theme'
'''
Name of the third-party Sphinx extension providing the custom HTML theme
preferred by this documentation.

Note that we selected this theme according to mostly objective (albeit
ultimately subjective) heuristic criteria. In descending order of importance, we
selected the theme with:

#. The most frequent git commit history.
#. The open issues and pull requests (PRs).
#. The most GitHub stars as a crude proxy for aggregate rating.
#. **IS NOT STRONGLY OPINIONATED** (i.e., is configurable with standard Sphinx
   settings and directives).

Furo
----------
Furo_ handily bested all other themes across the first three criteria. Furo is
very well-maintained, frequently closes out open issues and merges open PRs, and
sports the highest quantity of GitHub stars by an overwhelming margin. Sadly,
Furo handily loses against literally unmaintained themes across the final
criteria. Furo is absurdly strongly opinionated to an authoritarian degree we
rarely find in open-source software. Why? Because it's principal maintainer is.
Like maintainer, like software. Furo routinely ignores standard Sphinx settings
and directives due to subjective opinions held by its maintainer, including:

* Most user-defined ``:toctree:`` settings used to configure both global and
  local tables of contents (TOCs) and thus the leftmost navigation sidebar,
  effectively preventing users from using that sidebar to navigate to anything.
  We are *not* kidding. ``:toctree:`` settings ignored by Furo include:

  * ``:maxdepth:``. Internally, Furo forces the ``:titlesonly:`` setting by
    passing ``titles_only=True`` to Sphinx's ``toctree()`` function at runtime.
    Doing so effectively coerces ``:maxdepth: 1``, thus intentionally hiding
    *all* document structure from the navigation sidebar -- where (usually)
    *all* document structure is displayed. Users thus have no means of directly
    jumping from the root landing page to child leaf documents, significantly
    obstructing user experience (UX) and usability. See also this `feature
    request <Furo discussion_>`__ to relax these constraints, to which the Furo
    maintainer caustically replies:

        No, there isn't any (supported) way to do this.

        Separating the page content hierarchy and site structure was an explicit
        design goal.

We fundamentally disagree with those goals and have thus permanently switched
away from Furo. Unjustified opinions are the little death of sanity.

PyData
======
Furo and PyData are neck-and-neck with respect to git commit history; both are
extremely well-maintained. Furo leaps ahead with respect to both issue and PR
resolution, however; PyData has an extreme number of open issues and PRs, where
Furo enjoys none. Moreover, Furo also enjoys dramatically more GitHub stars.

Nonetheless, PyData is *not* strongly opinionated; Furo is. PyData does *not*
silently ignore standard Sphinx settings and directives for largely indefensible
reasons. Consequently, PyData wins by default. In fact, *any* other theme
(including even unmaintained dead themes) wins by default; *no* other theme (to
my limited knowledge) forcefully ignores standard Sphinx settings and directives
to the extent that Furo does.

PyData wins by *literally* doing nothing. Laziness prevails. All hail La-Z-Boy.

.. _Furo:
   https://github.com/pradyunsg/furo
.. _Furo discussion:
   https://github.com/pradyunsg/furo/discussions/146
'''


_SPHINX_THEME_VERSION_MAXIMUM = '0.7.2'
# _SPHINX_THEME_VERSION_MAXIMUM = '0.12.0'
'''
Machine-readable maximum (inclusive) version as a ``.``-delimited string of the
above Sphinx theme optionally leveraged when building package documentation.

This theme is a rapidly moving target that frequently breaks backward
compatibility. Although understandable, the fragility of this theme leaves us
little alternatives but to pin to a **maximum** rather than **minimum** version
of this theme. Specifically, this project requires:

* :mod:pydata_sphinx_theme` <= 0.7.2, as our circumvention of both
  pydata/pydata-sphinx-theme#90 and pydata/pydata-sphinx-theme#221 assumes a
  reasonably older version of this theme. See also this currently `open issue`_.

.. _open issue:
   https://github.com/pydata/pydata-sphinx-theme/issues/1181
'''

# ....................{ METADATA ~ libs : doc              }....................
LIBS_DOCTIME_MANDATORY = (
    # Sphinx itself.
    (
        f'sphinx '
        f'>={_SPHINX_VERSION_MINIMUM}, '
        f'<{_SPHINX_VERSION_MAXIMUM_EXCLUSIVE}'
    ),

    # Third-party Sphinx theme.
    f'{SPHINX_THEME_NAME} <={_SPHINX_THEME_VERSION_MAXIMUM}',

    # Third-party Sphinx extensions.
    'autoapi >=0.9.0',
    'sphinxext-opengraph >= 0.7.5',
)
'''
**Mandatory developer documentation build-time package dependencies** (i.e.,
dependencies required to manually build documentation for this package as a
developer at the command line) as a tuple of :mod:`setuptools`-specific
requirements strings of the format ``{project_name}
{comparison1}{version1},...,{comparisonN}{versionN}``.

For flexibility, these dependencies are loosely relaxed to enable developers to
build with *any* versions satisfying at least the bare minimum. For the same
reason, optional documentation build-time package dependencies are omitted.
Since our documentation build system emits a non-fatal warning for each missing
optional dependency, omitting these optional dependencies here imposes no undue
hardships while improving usability.

See Also
----------
:data:`LIBS_RUNTIME_OPTIONAL`
    Further details.
'''


#FIXME: For future use, we still preserve an RTD-specific list of requirements.
#It's unclear whether we actually require this, however. Consider excising. The
#prior approach of pinning exact Sphinx versions failed painfully by
#accidentally constraining us to obsolete Sphinx versions known to be broken.
LIBS_DOCTIME_MANDATORY_RTD = LIBS_DOCTIME_MANDATORY
# LIBS_DOCTIME_MANDATORY_RTD = (
#     f'sphinx =={_SPHINX_VERSION_MINIMUM}',
#     f'{SPHINX_THEME_NAME} =={_SPHINX_THEME_VERSION_MAXIMUM}',
# )
'''
**Mandatory Read The Docs (RTD) documentation build-time package dependencies**
(i.e., dependencies required to automatically build documentation for this
package from the third-party RTD hosting service) as a tuple of
:mod:`setuptools`-specific requirements strings of the format ``{project_name}
{comparison1}{version1},...,{comparisonN}{versionN}``.

For consistency, these dependencies are strictly constrained to force RTD to
build against a single well-tested configuration known to work reliably.

See Also
----------
:data:`LIBS_RUNTIME_OPTIONAL`
    Further details.
'''

# ....................{ METADATA ~ libs : dev              }....................
LIBS_DEVELOPER_MANDATORY = LIBS_TESTTIME_MANDATORY + LIBS_DOCTIME_MANDATORY
'''
**Mandatory developer package dependencies** (i.e., dependencies required to
develop and meaningfully contribute pull requests for this package) as a tuple
of :mod:`setuptools`-specific requirements strings of the format
``{project_name} {comparison1}{version1},...,{comparisonN}{versionN}``.

This tuple includes all mandatory test- and documentation build-time package
dependencies and is thus a convenient shorthand for those lower-level tuples.

See Also
----------
:data:`LIBS_RUNTIME_OPTIONAL`
    Further details.
'''
