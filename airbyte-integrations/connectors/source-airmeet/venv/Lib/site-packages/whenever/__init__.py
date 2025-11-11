from __future__ import annotations

from ._core import *
from ._core import (  # The unpickle functions must be findable at module-level
    _EXTENSION_LOADED,
    _unpkl_date,
    _unpkl_ddelta,
    _unpkl_dtdelta,
    _unpkl_inst,
    _unpkl_local,
    _unpkl_md,
    _unpkl_offset,
    _unpkl_system,
    _unpkl_tdelta,
    _unpkl_time,
    _unpkl_utc,
    _unpkl_ym,
    _unpkl_zoned,
)
from ._utils import *

# These imports are only needed for the doc generation, which only
# runs in pure Python mode.
if not _EXTENSION_LOADED:  # pragma: no cover
    from ._pywhenever import (
        __all__,
        _BasicConversions,
        _ExactAndLocalTime,
        _ExactTime,
        _LocalTime,
    )


__version__ = "0.8.10"

reset_tzpath()  # populate the tzpath once at startup


# Handle deprecated names
def __getattr__(name: str) -> object:
    import warnings

    # This ensures we get the most up-to-date TZPATH.
    if name == "TZPATH":
        from ._utils import TZPATH

        return TZPATH
    elif name in ("NaiveDateTime", "LocalDateTime"):
        warnings.warn(
            f"whenever.{name} has been renamed to PlainDateTime.",
            DeprecationWarning,
        )
        return PlainDateTime

    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
