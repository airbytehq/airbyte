---
id: airbyte-sources-registry
title: airbyte.sources.registry
---

Module airbyte.sources.registry
===============================
Backwards compatibility shim for airbyte.sources.registry.

This module re-exports symbols from airbyte.registry for backwards compatibility.
New code should import from airbyte.registry directly.

Functions
---------

`get_available_connectors(install_type: InstallType | str | None = InstallType.INSTALLABLE) ‑> list[str]`
:   Return a list of all available connectors.
    
    Connectors will be returned in alphabetical order, with the standard prefix "source-".
    
    Args:
        install_type: The type of installation for the connector.
            Defaults to `InstallType.INSTALLABLE`.

`get_connector_metadata(name: str) ‑> airbyte.registry.ConnectorMetadata | None`
:   Check the cache for the connector.
    
    If the cache is empty, populate by calling update_cache.

Classes
-------

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