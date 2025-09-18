"""MockAPI Destination Connector for Airbyte"""

__version__ = "0.1.0"

from .client import MockAPIClient
from .config import MockAPIConfig

# Import destination separately to avoid circular imports
try:
    from .destination import DestinationMockapi
    __all__ = ["DestinationMockapi", "MockAPIClient", "MockAPIConfig"]
except ImportError:
    # If airbyte_cdk is not available, skip destination import
    __all__ = ["MockAPIClient", "MockAPIConfig"]