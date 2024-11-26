"""
Metadata about semver.

Contains information about semver's version, the implemented version
of the semver specifictation, author, maintainers, and description.

.. autodata:: __author__

.. autodata:: __description__

.. autodata:: __maintainer__

.. autodata:: __version__

.. autodata:: SEMVER_SPEC_VERSION
"""

#: Semver version
__version__ = "3.0.2"

#: Original semver author
__author__ = "Kostiantyn Rybnikov"

#: Author's email address
__author_email__ = "k-bx@k-bx.com"

#: Current maintainer
__maintainer__ = ["Sebastien Celles", "Tom Schraitle"]

#: Maintainer's email address
__maintainer_email__ = "s.celles@gmail.com"

#: Short description about semver
__description__ = "Python helper for Semantic Versioning (https://semver.org)"

#: Supported semver specification
SEMVER_SPEC_VERSION = "2.0.0"
