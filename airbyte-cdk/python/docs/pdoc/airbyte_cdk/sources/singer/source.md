Module airbyte_cdk.sources.singer.source
========================================

Classes
-------

`BaseSingerSource()`
:   Helper class that provides a standard way to create an ABC using
    inheritance.

    ### Ancestors (in MRO)

    * airbyte_cdk.sources.singer.source.SingerSource
    * airbyte_cdk.sources.source.BaseSource
    * airbyte_cdk.connector.BaseConnector
    * abc.ABC
    * typing.Generic

    ### Class variables

    `check_config_against_spec: bool`
    :

    `force_full_refresh`
    :

    ### Instance variables

    `api_error: Type[Exception]`
    :   Class/Base class of the exception that will be thrown if the tap is misconfigured or service unavailable

    `tap_cmd: str`
    :   Tap command

    `tap_name: str`
    :   Tap name

    ### Methods

    `try_connect(self, logger: logging.Logger, config: Mapping[str, Any])`
    :   Test provided credentials, raises self.api_error if something goes wrong

`ConfigContainer(config, config_path)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = {}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict
    * typing.Generic

    ### Class variables

    `config_path: str`
    :

`SingerSource()`
:   Helper class that provides a standard way to create an ABC using
    inheritance.

    ### Ancestors (in MRO)

    * airbyte_cdk.sources.source.BaseSource
    * airbyte_cdk.connector.BaseConnector
    * abc.ABC
    * typing.Generic

    ### Descendants

    * airbyte_cdk.sources.singer.source.BaseSingerSource

    ### Class variables

    `check_config_against_spec: bool`
    :

    ### Methods

    `check(self, logger: logging.Logger, config: airbyte_cdk.sources.singer.source.ConfigContainer) ‑> airbyte_cdk.models.airbyte_protocol.AirbyteConnectionStatus`
    :   Tests if the input configuration can be used to successfully connect to the integration

    `check_config(self, logger: logging.Logger, config_path: str, config: airbyte_cdk.sources.singer.source.ConfigContainer) ‑> airbyte_cdk.models.airbyte_protocol.AirbyteConnectionStatus`
    :   Some Singer source may perform check using config_path or config to
        tests if the input configuration can be used to successfully connect to the integration

    `configure(self, config: Mapping[str, Any], temp_dir: str) ‑> airbyte_cdk.sources.singer.source.ConfigContainer`
    :   Persist raw_config in temporary directory to run the Source job
        This can be overridden if extra temporary files need to be persisted in the temp dir

    `discover(self, logger: logging.Logger, config: airbyte_cdk.sources.singer.source.ConfigContainer) ‑> airbyte_cdk.models.airbyte_protocol.AirbyteCatalog`
    :   Implements the parent class discover method.

    `discover_cmd(self, logger: logging.Logger, config_path: str) ‑> str`
    :   Returns the command used to run discovery in the singer tap. For example, if the bash command used to invoke the singer tap is `tap-postgres`,
        and the config JSON lived in "/path/config.json", this method would return "tap-postgres --config /path/config.json"

    `get_excluded_streams(self) ‑> List[str]`
    :   This method provide ability to exclude some streams from catalog
        
        :return: A list of excluded stream names

    `get_primary_key_overrides(self) ‑> Dict[str, List[str]]`
    :   Similar to get_sync_mode_overrides but for primary keys.
        
        :return: A dict from stream name to the list of primary key fields for the stream.

    `get_sync_mode_overrides(self) ‑> Dict[str, airbyte_cdk.sources.singer.singer_helpers.SyncModeInfo]`
    :   The Singer Spec outlines a way for taps to declare in their catalog that their streams support incremental sync (valid-replication-keys,
        forced-replication-method, and others). However, many taps which are incremental don't actually declare that via the catalog, and just
        use their input state to perform an incremental sync without giving any hints to the user. An Airbyte Connector built on top of such a
        Singer Tap cannot automatically detect which streams are full refresh or incremental or what their cursors are. In those cases the developer
        needs to manually specify information about the sync modes.
        
        This method provides a way of doing that: the dict of stream names to SyncModeInfo returned from this method will be used to override each
        stream's sync mode information in the Airbyte Catalog output from the discover method. Only set fields provided in the SyncModeInfo are used.
        If a SyncModeInfo field is not set, it will not be overridden in the output catalog.
        
        :return: A dict from stream name to the sync modes that should be applied to this stream.

    `read(self, logger: logging.Logger, config: airbyte_cdk.sources.singer.source.ConfigContainer, catalog_path: str, state_path: str = None) ‑> Iterable[airbyte_cdk.models.airbyte_protocol.AirbyteMessage]`
    :   Implements the parent class read method.

    `read_catalog(self, catalog_path: str) ‑> str`
    :   Since singer source don't need actual catalog object, we override this to return path only

    `read_cmd(self, logger: logging.Logger, config_path: str, catalog_path: str, state_path: str = None) ‑> str`
    :   Returns the command used to read data from the singer tap. For example, if the bash command used to invoke the singer tap is `tap-postgres`,
        and the config JSON lived in "/path/config.json", and the catalog was in "/path/catalog.json",
        this method would return "tap-postgres --config /path/config.json --catalog /path/catalog.json"

    `read_state(self, state_path: str) ‑> str`
    :   Since singer source don't need actual state object, we override this to return path only

    `transform_config(self, config: Mapping[str, Any]) ‑> Mapping[str, Any]`
    :   Singer source may need to adapt the Config object for the singer tap specifics