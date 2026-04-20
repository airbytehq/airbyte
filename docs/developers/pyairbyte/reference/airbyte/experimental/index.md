---
id: airbyte-experimental-index
title: airbyte.experimental.index
---

Module airbyte.experimental
===========================
Experimental features which may change.

> **NOTE:**
> The following "experimental" features are now "stable" and can be accessed directly from the
`airbyte.get_source()` method:
> - Docker sources, using the `docker_image` argument.
> - Yaml sources, using the `source_manifest` argument.

## About Experimental Features

Experimental features may change without notice between minor versions of PyAirbyte. Although rare,
they may also be entirely removed or refactored in future versions of PyAirbyte. Experimental
features may also be less stable than other features, and may not be as well-tested.

You can help improve this product by reporting issues and providing feedback for improvements in our
[GitHub issue tracker](https://github.com/airbytehq/pyairbyte/issues).

Functions
---------

`get_source(name: str, config: dict[str, Any] | None = None, *, config_change_callback: ConfigChangeCallback | None = None, streams: str | list[str] | None = None, version: str | None = None, use_python: bool | Path | str | None = None, pip_url: str | None = None, local_executable: Path | str | None = None, docker_image: bool | str | None = None, use_host_network: bool = False, source_manifest: bool | dict | Path | str | None = None, install_if_missing: bool = True, install_root: Path | None = None, no_executor: bool = False) ‑> Source`
:   Get a connector by name and version.
    
    If an explicit install or execution method is requested (e.g. `local_executable`,
    `docker_image`, `pip_url`, `source_manifest`), the connector will be executed using this method.
    
    Otherwise, an appropriate method will be selected based on the available connector metadata:
    1. If the connector is registered and has a YAML source manifest is available, the YAML manifest
       will be downloaded and used to to execute the connector.
    2. Else, if the connector is registered and has a PyPI package, it will be installed via pip.
    3. Else, if the connector is registered and has a Docker image, and if Docker is available, it
       will be executed using Docker.
    
    Args:
        name: connector name
        config: connector config - if not provided, you need to set it later via the set_config
            method.
        config_change_callback: callback function to be called when the connector config changes.
        streams: list of stream names to select for reading. If set to "*", all streams will be
            selected. If not provided, you can set it later via the `select_streams()` or
            `select_all_streams()` method.
        version: connector version - if not provided, the currently installed version will be used.
            If no version is installed, the latest available version will be used. The version can
            also be set to "latest" to force the use of the latest available version.
        use_python: (Optional.) Python interpreter specification:
            - True: Use current Python interpreter. (Inferred if `pip_url` is set.)
            - False: Use Docker instead.
            - Path: Use interpreter at this path.
            - str: Use specific Python version. E.g. "3.11" or "3.11.10". If the version is not yet
                installed, it will be installed by uv. (This generally adds less than 3 seconds
                to install times.)
        pip_url: connector pip URL - if not provided, the pip url will be inferred from the
            connector name.
        local_executable: If set, the connector will be assumed to already be installed and will be
            executed using this path or executable name. Otherwise, the connector will be installed
            automatically in a virtual environment.
        docker_image: If set, the connector will be executed using Docker. You can specify `True`
            to use the default image for the connector, or you can specify a custom image name.
            If `version` is specified and your image name does not already contain a tag
            (e.g. `my-image:latest`), the version will be appended as a tag (e.g. `my-image:0.1.0`).
        use_host_network: If set, along with docker_image, the connector will be executed using
            the host network. This is useful for connectors that need to access resources on
            the host machine, such as a local database. This parameter is ignored when
            `docker_image` is not set.
        source_manifest: If set, the connector will be executed based on a declarative YAML
            source definition. This input can be `True` to attempt to auto-download a YAML spec,
            `dict` to accept a Python dictionary as the manifest, `Path` to pull a manifest from
            the local file system, or `str` to pull the definition from a web URL.
        install_if_missing: Whether to install the connector if it is not available locally. This
            parameter is ignored when `local_executable` or `source_manifest` are set.
        install_root: (Optional.) The root directory where the virtual environment will be
            created. If not provided, the current working directory will be used.
        no_executor: If True, use NoOpExecutor which fetches specs from the registry without
            local installation. This is useful for scenarios where you need to validate
            configurations but don't need to run the connector locally (e.g., deploying to Cloud).