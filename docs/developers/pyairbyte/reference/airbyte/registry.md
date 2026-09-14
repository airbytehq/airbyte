---
id: airbyte-registry
title: airbyte.registry
---

Module airbyte.registry
=======================
Connectivity to the connector catalog registry.

Functions
---------

`get_available_connectors(install_type: InstallType | str | None = InstallType.INSTALLABLE) ‑> list[str]`
:   Return a list of all available connectors.
    
    Connectors will be returned in alphabetical order, with the standard prefix "source-".
    
    Args:
        install_type: The type of installation for the connector.
            Defaults to `InstallType.INSTALLABLE`.

`get_connector_api_docs_urls(connector_name: str) ‑> list[airbyte.registry.ApiDocsUrl]`
:   Get API documentation URLs for a connector.
    
    This function retrieves documentation URLs for a connector's upstream API from multiple sources:
    - Registry metadata (documentationUrl, externalDocumentationUrls)
    - Connector manifest.yaml file (data.externalDocumentationUrls)
    
    Args:
        connector_name: The canonical connector name (e.g., "source-facebook-marketing")
    
    Returns:
        List of ApiDocsUrl objects with documentation URLs, deduplicated by URL.
    
    Raises:
        AirbyteConnectorNotRegisteredError: If the connector is not found in the registry.

`get_connector_metadata(name: str) ‑> airbyte.registry.ConnectorMetadata | None`
:   Check the cache for the connector.
    
    If the cache is empty, populate by calling update_cache.

`get_connector_version_history(connector_name: str, *, num_versions_to_validate: int = 5, timeout: int = 30) ‑> list[airbyte.registry.ConnectorVersionInfo]`
:   Get version history for a connector.
    
    This function retrieves the version history for a connector by:
    1. Scraping the changelog HTML from docs.airbyte.com
    2. Parsing version information including PR URLs and titles
    3. Overriding release dates for the most recent N versions with accurate
       registry data
    
    Args:
        connector_name: Name of the connector (e.g., 'source-faker', 'destination-postgres')
        num_versions_to_validate: Number of most recent versions to override with
            registry release dates for accuracy. Defaults to 5.
        timeout: Timeout in seconds for the changelog fetch. Defaults to 30.
    
    Returns:
        List of ConnectorVersionInfo objects, sorted by most recent first.
    
    Raises:
        AirbyteConnectorNotRegisteredError: If the connector is not found in the registry.
    
    Example:
        >>> versions = get_connector_version_history("source-faker", num_versions_to_validate=3)
        >>> for v in versions[:5]:
        ...     print(f"\{v.version\}: \{v.release_date\}")

Classes
-------

`ApiDocsUrl(**data: Any)`
:   API documentation URL information.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `doc_type: str`
    :

    `model_config`
    :

    `requires_login: bool`
    :

    `source: str`
    :

    `title: str`
    :

    `url: str`
    :

    ### Static methods

    `from_manifest_dict(manifest_data: dict[str, Any]) ‑> list[typing.Self]`
    :   Extract documentation URLs from parsed manifest data.
        
        Args:
            manifest_data: The parsed manifest.yaml data as a dictionary
        
        Returns:
            List of ApiDocsUrl objects extracted from the manifest

`ConnectorMetadata(**data: Any)`
:   Metadata for a connector.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `install_types: set[airbyte.registry.InstallType]`
    :   The supported install types for the connector.

    `language: airbyte.registry.Language | None`
    :   The language of the connector.

    `latest_available_version: str | None`
    :   The latest available version of the connector.

    `model_config`
    :

    `name: str`
    :   Connector name. For example, "source-google-sheets".

    `pypi_package_name: str | None`
    :   The name of the PyPI package for the connector, if it exists.

    `suggested_streams: list[str] | None`
    :   A list of suggested streams for the connector, if available.

    ### Instance variables

    `default_install_type: InstallType`
    :   Return the default install type for the connector.

`ConnectorVersionInfo(**data: Any)`
:   Information about a specific connector version.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `changelog_url: str`
    :

    `docker_image_url: str`
    :

    `model_config`
    :

    `parsing_errors: list[str]`
    :

    `pr_title: str | None`
    :

    `pr_url: str | None`
    :

    `release_date: str | None`
    :

    `version: str`
    :

`InstallType(*args, **kwds)`
:   The type of installation for a connector.

    ### Ancestors (in MRO)

    * builtins.str
    * enum.Enum

    ### Class variables

    `ANY`
    :   All connectors in the registry (environment-independent).

    `DOCKER`
    :   Docker-based connectors (returns all connectors for backward compatibility).

    `INSTALLABLE`
    :   Connectors installable in the current environment (environment-sensitive).
        
        Returns all connectors if Docker is installed, otherwise only Python and YAML.

    `JAVA`
    :   Java-based connectors.

    `PYTHON`
    :   Python-based connectors available via PyPI.

    `YAML`
    :   Manifest-only connectors that can be run without Docker.

`Language(*args, **kwds)`
:   The language of a connector.

    ### Ancestors (in MRO)

    * builtins.str
    * enum.Enum

    ### Class variables

    `JAVA`
    :

    `MANIFEST_ONLY`
    :

    `PYTHON`
    :