"""Utility functions for connector naming conventions."""


def extract_root_name(connector_name: str) -> str:
    """
    Extract root name from full connector name.

    Strips the 'source-' or 'destination-' prefix to get the root name
    used for 1Password item naming.

    Examples:
        source-stripe -> stripe
        destination-mysql -> mysql
        source-google-ads -> google-ads
        stripe -> stripe (already a root name)

    Args:
        connector_name: Full connector name (e.g., "source-stripe")

    Returns:
        Root name for 1Password item (e.g., "stripe")
    """
    for prefix in ['source-', 'destination-']:
        if connector_name.startswith(prefix):
            return connector_name[len(prefix):]
    return connector_name  # Already a root name
