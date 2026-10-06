---
id: airbyte-destinations-util
title: airbyte.destinations.util
---

Module airbyte.destinations.util
================================
Destination utilities.

For usage examples, see the `airbyte.destinations` module documentation.

Functions
---------

`get_destination(name: str, config: dict[str, Any] | None = None, *, config_change_callback: ConfigChangeCallback | None = None, version: str | None = None, use_python: bool | Path | str | None = None, pip_url: str | None = None, local_executable: Path | str | None = None, docker_image: str | bool | None = None, use_host_network: bool = False, install_if_missing: bool = True, install_root: Path | None = None, no_executor: bool = False) ‑> Destination`
:   Get a connector by name and version.
    
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
        install_if_missing: Whether to install the connector if it is not available locally. This
            parameter is ignored when local_executable is set.
        install_root: (Optional.) The root directory where the virtual environment will be
            created. If not provided, the current working directory will be used.
        no_executor: If True, use NoOpExecutor which fetches specs from the registry without
            local installation. This is useful for scenarios where you need to validate
            configurations but don't need to run the connector locally (e.g., deploying to Cloud).

`get_noop_destination(*, install_if_missing: bool = True) ‑> airbyte.destinations.base.Destination`
:   Get a devnull (no-op) destination.
    
    This is useful for performance benchmarking of sources, without
    adding the overhead of writing data to a real destination.