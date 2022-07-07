Module airbyte_cdk.models.airbyte_protocol
==========================================

Classes
-------

`AdvancedAuth(**data: Any)`
:   Create a new model by parsing and validating input data from keyword arguments.
    
    Raises ValidationError if the input data cannot be parsed to form a valid model.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel
    * pydantic.utils.Representation

    ### Class variables

    `auth_flow_type: Optional[airbyte_cdk.models.airbyte_protocol.AuthFlowType]`
    :

    `oauth_config_specification: Optional[airbyte_cdk.models.airbyte_protocol.OAuthConfigSpecification]`
    :

    `predicate_key: Optional[List[str]]`
    :

    `predicate_value: Optional[str]`
    :

`AirbyteCatalog(**data: Any)`
:   Create a new model by parsing and validating input data from keyword arguments.
    
    Raises ValidationError if the input data cannot be parsed to form a valid model.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel
    * pydantic.utils.Representation

    ### Class variables

    `Config`
    :

    `streams: List[airbyte_cdk.models.airbyte_protocol.AirbyteStream]`
    :

`AirbyteConnectionStatus(**data: Any)`
:   Create a new model by parsing and validating input data from keyword arguments.
    
    Raises ValidationError if the input data cannot be parsed to form a valid model.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel
    * pydantic.utils.Representation

    ### Class variables

    `Config`
    :

    `message: Optional[str]`
    :

    `status: airbyte_cdk.models.airbyte_protocol.Status`
    :

`AirbyteErrorTraceMessage(**data: Any)`
:   Create a new model by parsing and validating input data from keyword arguments.
    
    Raises ValidationError if the input data cannot be parsed to form a valid model.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel
    * pydantic.utils.Representation

    ### Class variables

    `Config`
    :

    `failure_type: Optional[airbyte_cdk.models.airbyte_protocol.FailureType]`
    :

    `internal_message: Optional[str]`
    :

    `message: str`
    :

    `stack_trace: Optional[str]`
    :

`AirbyteGlobalState(**data: Any)`
:   Create a new model by parsing and validating input data from keyword arguments.
    
    Raises ValidationError if the input data cannot be parsed to form a valid model.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel
    * pydantic.utils.Representation

    ### Class variables

    `Config`
    :

    `shared_state: Optional[airbyte_cdk.models.airbyte_protocol.AirbyteStateBlob]`
    :

    `stream_states: List[airbyte_cdk.models.airbyte_protocol.AirbyteStreamState]`
    :

`AirbyteLogMessage(**data: Any)`
:   Create a new model by parsing and validating input data from keyword arguments.
    
    Raises ValidationError if the input data cannot be parsed to form a valid model.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel
    * pydantic.utils.Representation

    ### Class variables

    `Config`
    :

    `level: airbyte_cdk.models.airbyte_protocol.Level`
    :

    `message: str`
    :

`AirbyteMessage(**data: Any)`
:   Create a new model by parsing and validating input data from keyword arguments.
    
    Raises ValidationError if the input data cannot be parsed to form a valid model.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel
    * pydantic.utils.Representation

    ### Class variables

    `Config`
    :

    `catalog: Optional[airbyte_cdk.models.airbyte_protocol.AirbyteCatalog]`
    :

    `connectionStatus: Optional[airbyte_cdk.models.airbyte_protocol.AirbyteConnectionStatus]`
    :

    `log: Optional[airbyte_cdk.models.airbyte_protocol.AirbyteLogMessage]`
    :

    `record: Optional[airbyte_cdk.models.airbyte_protocol.AirbyteRecordMessage]`
    :

    `spec: Optional[airbyte_cdk.models.airbyte_protocol.ConnectorSpecification]`
    :

    `state: Optional[airbyte_cdk.models.airbyte_protocol.AirbyteStateMessage]`
    :

    `trace: Optional[airbyte_cdk.models.airbyte_protocol.AirbyteTraceMessage]`
    :

    `type: airbyte_cdk.models.airbyte_protocol.Type`
    :

`AirbyteProtocol(**data: Any)`
:   Create a new model by parsing and validating input data from keyword arguments.
    
    Raises ValidationError if the input data cannot be parsed to form a valid model.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel
    * pydantic.utils.Representation

    ### Class variables

    `airbyte_message: Optional[airbyte_cdk.models.airbyte_protocol.AirbyteMessage]`
    :

    `configured_airbyte_catalog: Optional[airbyte_cdk.models.airbyte_protocol.ConfiguredAirbyteCatalog]`
    :

`AirbyteRecordMessage(**data: Any)`
:   Create a new model by parsing and validating input data from keyword arguments.
    
    Raises ValidationError if the input data cannot be parsed to form a valid model.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel
    * pydantic.utils.Representation

    ### Class variables

    `Config`
    :

    `data: Dict[str, Any]`
    :

    `emitted_at: int`
    :

    `namespace: Optional[str]`
    :

    `stream: str`
    :

`AirbyteStateBlob(**data: Any)`
:   Create a new model by parsing and validating input data from keyword arguments.
    
    Raises ValidationError if the input data cannot be parsed to form a valid model.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel
    * pydantic.utils.Representation

    ### Class variables

    `Config`
    :

`AirbyteStateMessage(**data: Any)`
:   Create a new model by parsing and validating input data from keyword arguments.
    
    Raises ValidationError if the input data cannot be parsed to form a valid model.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel
    * pydantic.utils.Representation

    ### Class variables

    `Config`
    :

    `data: Optional[Dict[str, Any]]`
    :

    `global_: Optional[airbyte_cdk.models.airbyte_protocol.AirbyteGlobalState]`
    :

    `stream: Optional[airbyte_cdk.models.airbyte_protocol.AirbyteStreamState]`
    :

    `type: Optional[airbyte_cdk.models.airbyte_protocol.AirbyteStateType]`
    :

`AirbyteStateType(value, names=None, *, module=None, qualname=None, type=None, start=1)`
:   An enumeration.

    ### Ancestors (in MRO)

    * enum.Enum

    ### Class variables

    `GLOBAL`
    :

    `LEGACY`
    :

    `STREAM`
    :

`AirbyteStream(**data: Any)`
:   Create a new model by parsing and validating input data from keyword arguments.
    
    Raises ValidationError if the input data cannot be parsed to form a valid model.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel
    * pydantic.utils.Representation

    ### Class variables

    `Config`
    :

    `default_cursor_field: Optional[List[str]]`
    :

    `json_schema: Dict[str, Any]`
    :

    `name: str`
    :

    `namespace: Optional[str]`
    :

    `source_defined_cursor: Optional[bool]`
    :

    `source_defined_primary_key: Optional[List[List[str]]]`
    :

    `supported_sync_modes: Optional[List[airbyte_cdk.models.airbyte_protocol.SyncMode]]`
    :

`AirbyteStreamState(**data: Any)`
:   Create a new model by parsing and validating input data from keyword arguments.
    
    Raises ValidationError if the input data cannot be parsed to form a valid model.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel
    * pydantic.utils.Representation

    ### Class variables

    `Config`
    :

    `stream_descriptor: airbyte_cdk.models.airbyte_protocol.StreamDescriptor`
    :

    `stream_state: Optional[airbyte_cdk.models.airbyte_protocol.AirbyteStateBlob]`
    :

`AirbyteTraceMessage(**data: Any)`
:   Create a new model by parsing and validating input data from keyword arguments.
    
    Raises ValidationError if the input data cannot be parsed to form a valid model.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel
    * pydantic.utils.Representation

    ### Class variables

    `Config`
    :

    `emitted_at: float`
    :

    `error: Optional[airbyte_cdk.models.airbyte_protocol.AirbyteErrorTraceMessage]`
    :

    `type: airbyte_cdk.models.airbyte_protocol.TraceType`
    :

`AuthFlowType(value, names=None, *, module=None, qualname=None, type=None, start=1)`
:   An enumeration.

    ### Ancestors (in MRO)

    * enum.Enum

    ### Class variables

    `oauth1_0`
    :

    `oauth2_0`
    :

`AuthSpecification(**data: Any)`
:   Create a new model by parsing and validating input data from keyword arguments.
    
    Raises ValidationError if the input data cannot be parsed to form a valid model.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel
    * pydantic.utils.Representation

    ### Class variables

    `auth_type: Optional[airbyte_cdk.models.airbyte_protocol.AuthType]`
    :

    `oauth2Specification: Optional[airbyte_cdk.models.airbyte_protocol.OAuth2Specification]`
    :

`AuthType(value, names=None, *, module=None, qualname=None, type=None, start=1)`
:   An enumeration.

    ### Ancestors (in MRO)

    * enum.Enum

    ### Class variables

    `oauth2_0`
    :

`ConfiguredAirbyteCatalog(**data: Any)`
:   Create a new model by parsing and validating input data from keyword arguments.
    
    Raises ValidationError if the input data cannot be parsed to form a valid model.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel
    * pydantic.utils.Representation

    ### Class variables

    `Config`
    :

    `streams: List[airbyte_cdk.models.airbyte_protocol.ConfiguredAirbyteStream]`
    :

`ConfiguredAirbyteStream(**data: Any)`
:   Create a new model by parsing and validating input data from keyword arguments.
    
    Raises ValidationError if the input data cannot be parsed to form a valid model.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel
    * pydantic.utils.Representation

    ### Class variables

    `Config`
    :

    `cursor_field: Optional[List[str]]`
    :

    `destination_sync_mode: airbyte_cdk.models.airbyte_protocol.DestinationSyncMode`
    :

    `primary_key: Optional[List[List[str]]]`
    :

    `stream: airbyte_cdk.models.airbyte_protocol.AirbyteStream`
    :

    `sync_mode: airbyte_cdk.models.airbyte_protocol.SyncMode`
    :

`ConnectorSpecification(**data: Any)`
:   Create a new model by parsing and validating input data from keyword arguments.
    
    Raises ValidationError if the input data cannot be parsed to form a valid model.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel
    * pydantic.utils.Representation

    ### Class variables

    `Config`
    :

    `advanced_auth: Optional[airbyte_cdk.models.airbyte_protocol.AdvancedAuth]`
    :

    `authSpecification: Optional[airbyte_cdk.models.airbyte_protocol.AuthSpecification]`
    :

    `changelogUrl: Optional[pydantic.networks.AnyUrl]`
    :

    `connectionSpecification: Dict[str, Any]`
    :

    `documentationUrl: Optional[pydantic.networks.AnyUrl]`
    :

    `supported_destination_sync_modes: Optional[List[airbyte_cdk.models.airbyte_protocol.DestinationSyncMode]]`
    :

    `supportsDBT: Optional[bool]`
    :

    `supportsIncremental: Optional[bool]`
    :

    `supportsNormalization: Optional[bool]`
    :

`DestinationSyncMode(value, names=None, *, module=None, qualname=None, type=None, start=1)`
:   An enumeration.

    ### Ancestors (in MRO)

    * enum.Enum

    ### Class variables

    `append`
    :

    `append_dedup`
    :

    `overwrite`
    :

`FailureType(value, names=None, *, module=None, qualname=None, type=None, start=1)`
:   An enumeration.

    ### Ancestors (in MRO)

    * enum.Enum

    ### Class variables

    `config_error`
    :

    `system_error`
    :

`Level(value, names=None, *, module=None, qualname=None, type=None, start=1)`
:   An enumeration.

    ### Ancestors (in MRO)

    * enum.Enum

    ### Class variables

    `DEBUG`
    :

    `ERROR`
    :

    `FATAL`
    :

    `INFO`
    :

    `TRACE`
    :

    `WARN`
    :

`OAuth2Specification(**data: Any)`
:   Create a new model by parsing and validating input data from keyword arguments.
    
    Raises ValidationError if the input data cannot be parsed to form a valid model.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel
    * pydantic.utils.Representation

    ### Class variables

    `Config`
    :

    `oauthFlowInitParameters: Optional[List[List[str]]]`
    :

    `oauthFlowOutputParameters: Optional[List[List[str]]]`
    :

    `rootObject: Optional[List[Union[str, int]]]`
    :

`OAuthConfigSpecification(**data: Any)`
:   Create a new model by parsing and validating input data from keyword arguments.
    
    Raises ValidationError if the input data cannot be parsed to form a valid model.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel
    * pydantic.utils.Representation

    ### Class variables

    `complete_oauth_output_specification: Optional[Dict[str, Any]]`
    :

    `complete_oauth_server_input_specification: Optional[Dict[str, Any]]`
    :

    `complete_oauth_server_output_specification: Optional[Dict[str, Any]]`
    :

    `oauth_user_input_from_connector_config_specification: Optional[Dict[str, Any]]`
    :

`Status(value, names=None, *, module=None, qualname=None, type=None, start=1)`
:   An enumeration.

    ### Ancestors (in MRO)

    * enum.Enum

    ### Class variables

    `FAILED`
    :

    `SUCCEEDED`
    :

`StreamDescriptor(**data: Any)`
:   Create a new model by parsing and validating input data from keyword arguments.
    
    Raises ValidationError if the input data cannot be parsed to form a valid model.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel
    * pydantic.utils.Representation

    ### Class variables

    `Config`
    :

    `name: str`
    :

    `namespace: Optional[str]`
    :

`SyncMode(value, names=None, *, module=None, qualname=None, type=None, start=1)`
:   An enumeration.

    ### Ancestors (in MRO)

    * enum.Enum

    ### Class variables

    `full_refresh`
    :

    `incremental`
    :

`TraceType(value, names=None, *, module=None, qualname=None, type=None, start=1)`
:   An enumeration.

    ### Ancestors (in MRO)

    * enum.Enum

    ### Class variables

    `ERROR`
    :

`Type(value, names=None, *, module=None, qualname=None, type=None, start=1)`
:   An enumeration.

    ### Ancestors (in MRO)

    * enum.Enum

    ### Class variables

    `CATALOG`
    :

    `CONNECTION_STATUS`
    :

    `LOG`
    :

    `RECORD`
    :

    `SPEC`
    :

    `STATE`
    :

    `TRACE`
    :