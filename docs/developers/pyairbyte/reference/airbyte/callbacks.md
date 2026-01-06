---
id: airbyte-callbacks
title: airbyte.callbacks
---

Module airbyte.callbacks
========================
Callbacks for working with PyAirbyte.

Variables
---------

`ConfigChangeCallback`
:   Callback for when the configuration changes while the connector is running.
    
    This callback can be passed to supporting functions like `airbyte.get_source()` and
    `airbyte.get_destination()` to take action whenever configuration changes.
    The callback will be called with the new configuration as the only argument.
    
    The most common use case for this callback is for connectors with OAuth APIs to pass updated
    refresh tokens when the previous token is about to expire.
    
    Note that the dictionary passed will contain the entire configuration, not just the changed fields.
    
    Example Usage:
    
    ```python
    import airbyte as ab
    import yaml
    from pathlib import Path
    
    config_file = Path("path/to/my/config.yaml")
    config_dict = yaml.safe_load(config_file.read_text())
    
    # Define the callback function:
    def config_callback(new_config: dict[str, Any]) -> None:
        # Write new config back to config file
        config_file.write_text(yaml.safe_dump(new_config))
    
    # Pass in the callback function when creating the source:
    source = get_source(
        "source-faker",
        config=config_dict,
        config_change_callback=config_callback,
    )
    # Now read as usual. If config changes during sync, the callback will be called.
    source.read()
    ```
    
    For more information on the underlying Airbyte protocol, please see documentation on the
    [`CONNECTOR_CONFIG`](https://docs.airbyte.com/understanding-airbyte/airbyte-protocol#airbytecontrolconnectorconfigmessage)
    control messages.