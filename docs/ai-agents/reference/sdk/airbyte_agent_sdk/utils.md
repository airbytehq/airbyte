---
id: airbyte_agent_sdk-utils
title: airbyte_agent_sdk.utils
---

Module airbyte_agent_sdk.utils
==============================
Utility functions for working with connectors.

Functions
---------

<a id="find_matching_auth_options"></a>

`find_matching_auth_options(provided_keys: set[str], auth_options: list[AuthOption]) ‑> list[AuthOption]`
:   Find auth options that match the provided credential keys.
    
    This is the single source of truth for auth scheme inference logic,
    used by both the executor (at runtime) and validation (for cassettes).
    
    Matching logic:
    - An option matches if all its required fields are present in provided_keys
    - Options with no required fields match any credentials
    
    Args:
        provided_keys: Set of credential/auth_config keys
        auth_options: List of AuthOption from the connector model
    
    Returns:
        List of AuthOption that match the provided keys

<a id="infer_auth_scheme_name"></a>

`infer_auth_scheme_name(provided_keys: set[str], auth_options: list[AuthOption]) ‑> str | None`
:   Infer the auth scheme name from provided credential keys.
    
    Uses find_matching_auth_options to find matches, then returns
    the scheme name only if exactly one option matches.
    
    Args:
        provided_keys: Set of credential/auth_config keys
        auth_options: List of AuthOption from the connector model
    
    Returns:
        The scheme_name if exactly one match, None otherwise

<a id="save_download"></a>

`save_download(download_iterator: AsyncIterator[bytes], path: str | Path, *, overwrite: bool = False) ‑> pathlib._local.Path`
:   Save a download iterator to a file.
    
    Args:
        download_iterator: AsyncIterator[bytes] from a download operation
        path: File path where content should be saved
        overwrite: Whether to overwrite existing file (default: False)
    
    Returns:
        Absolute Path to the saved file
    
    Raises:
        FileExistsError: If file exists and overwrite=False
        OSError: If file cannot be written
    
    Example:
        >>> from airbyte_agent_sdk.utils import save_download
        >>>
        >>> # Download and save a file
        >>> result = await connector.download_article_attachment(id="123")
        >>> file_path = await save_download(result, "./downloads/attachment.pdf")
        >>> print(f"Downloaded to \{file_path\}")
        Downloaded to /absolute/path/to/downloads/attachment.pdf
        >>>
        >>> # Overwrite existing file
        >>> file_path = await save_download(result, "./downloads/attachment.pdf", overwrite=True)