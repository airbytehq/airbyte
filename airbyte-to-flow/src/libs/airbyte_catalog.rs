use std::collections::HashMap;

use schemars::JsonSchema;
use serde::ser::{SerializeStruct, Serializer};
use serde::{Deserialize, Serialize};
use serde_json::value::RawValue;
use validator::{Validate, ValidationError};

#[derive(Debug, Serialize, Deserialize, Clone, PartialEq, JsonSchema)]
#[serde(rename_all = "snake_case")]
pub enum SyncMode {
    Incremental,
    FullRefresh,
}

#[derive(Debug, Serialize, Deserialize, Clone, Validate)]
#[serde(rename_all = "snake_case")]
pub struct Stream {
    pub name: String,
    pub json_schema: Box<RawValue>,
    // supported_sync_modes is planned to be made required soon
    // see https://is.gd/RqAhTO
    #[validate(length(min = 1))]
    pub supported_sync_modes: Option<Vec<SyncMode>>,
    pub source_defined_cursor: Option<bool>,
    pub default_cursor_field: Option<Vec<String>>,
    pub source_defined_primary_key: Option<Vec<Vec<String>>>,
    pub namespace: Option<String>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
#[serde(rename_all = "snake_case")]
pub enum DestinationSyncMode {
    Append,
    Overwrite,
    AppendDedup,
}

#[derive(Debug, Serialize, Deserialize, Clone, Validate)]
#[serde(rename_all = "snake_case")]
#[validate(schema(function = "Self::validate_configured_stream"))]
pub struct ConfiguredStream {
    #[validate]
    pub stream: Stream,
    pub sync_mode: SyncMode,
    pub destination_sync_mode: DestinationSyncMode,
    pub cursor_field: Option<Vec<String>>,
    pub primary_key: Option<Vec<Vec<String>>>,

    #[serde(alias = "estuary.dev/projections")]
    pub projections: HashMap<String, String>,
}
impl ConfiguredStream {
    fn validate_configured_stream(&self) -> Result<(), ValidationError> {
        if self
            .stream
            .supported_sync_modes
            .as_ref()
            .map(|modes| modes.contains(&self.sync_mode))
            .unwrap_or(false)
        {
            Ok(())
        } else {
            Err(ValidationError::new(
                "sync_mode is not in the supported list.",
            ))
        }
    }
}

#[derive(Debug, Serialize, Deserialize, Clone, Validate)]
pub struct Catalog {
    #[serde(rename = "streams")]
    #[validate]
    pub streams: Vec<Stream>,
}

#[derive(Debug, Deserialize, Clone, Validate, PartialEq)]
#[validate(schema(function = "Self::validate_range"))]
pub struct Range {
    pub begin: u32,
    pub end: u32,
}

impl Range {
    fn validate_range(&self) -> Result<(), ValidationError> {
        if self.begin <= self.end {
            Ok(())
        } else {
            Err(ValidationError::new("expected Begin <= End"))
        }
    }
}

impl Serialize for Range {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: Serializer,
    {
        let mut state = serializer.serialize_struct("Range", 2)?;
        state.serialize_field("begin", &format!("{:08x}", self.begin))?;
        state.serialize_field("end", &format!("{:08x}", self.end))?;
        state.end()
    }
}

#[derive(Debug, Serialize, Deserialize, Clone, Validate)]
#[serde(rename_all = "snake_case")]
pub struct ConfiguredCatalog {
    #[serde(rename = "streams")]
    #[validate(length(min = 1))]
    #[validate]
    pub streams: Vec<ConfiguredStream>,

    #[serde(rename = "estuary.dev/tail")]
    pub tail: bool,

    #[serde(rename = "estuary.dev/range")]
    #[validate]
    pub range: Range,
}

#[derive(Debug, Serialize, Deserialize, Clone, PartialEq)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum Status {
    Succeeded,
    Failed,
}

#[derive(Debug, Serialize, Deserialize, Clone, PartialEq)]
#[serde(rename_all = "snake_case")]
pub struct ConnectionStatus {
    pub status: Status,
    pub message: Option<String>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
#[serde(rename_all = "snake_case")]
pub struct Record {
    pub stream: String,
    pub data: serde_json::Value,
    pub emitted_at: i64,
    pub namespace: Option<String>,
}

#[derive(Debug, Serialize, Deserialize, Clone, PartialEq)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum LogLevel {
    Trace,
    Debug,
    Info,
    Warn,
    Error,
    Fatal,
}

#[derive(Debug, Serialize, Deserialize, Clone, PartialEq)]
#[serde(rename_all = "camelCase")]
pub struct Log {
    pub level: LogLevel,
    pub message: String,
}
impl Log {
    pub fn log(&self) {
        match self.level {
            LogLevel::Trace => tracing::trace!("{}", self.message),
            LogLevel::Debug => tracing::debug!("{}", self.message),
            LogLevel::Info => tracing::info!("{}", self.message),
            LogLevel::Warn => tracing::warn!("{}", self.message),
            LogLevel::Error | LogLevel::Fatal => tracing::error!("{}", self.message),
        }
    }
}

#[derive(Debug, Serialize, Deserialize, Clone)]
#[serde(rename_all = "snake_case")]
pub struct State {
    // Data is the actual state associated with the ingestion. This must be a JSON _Object_ in order
    // to comply with the airbyte specification.
    pub data: Box<RawValue>,

    // Merge indicates that Data is an RFC 7396 JSON Merge Patch, and should
    // be be reduced into the previous state accordingly.
    #[serde(alias = "estuary.dev/merge")]
    pub merge: Option<bool>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
#[serde(rename_all = "camelCase")]
pub struct Spec {
    pub documentation_url: Option<String>,
    pub changelog_url: Option<String>,
    pub connection_specification: Box<RawValue>,
    pub supports_incremental: Option<bool>,

    // SupportedDestinationSyncModes is ignored by Flow
    pub supported_destination_sync_modes: Option<Vec<DestinationSyncMode>>,
    // SupportsNormalization is not currently used or supported by Flow or estuary-developed
    // connectors
    pub supports_normalization: Option<bool>,
    // SupportsDBT is not currently used or supported by Flow or estuary-developed connectors
    #[serde(rename = "supportsDBT")]
    pub supports_dbt: Option<bool>,

    // AuthSpecification is not currently used or supported by Flow or estuary-developed
    // connectors, and it is deprecated in the airbyte spec.
    pub auth_specification: Option<Box<RawValue>>,
    // AdvancedAuth is not currently used or supported by Flow or estuary-developed
    // connectors.
    pub advanced_auth: Option<Box<RawValue>>,
}

#[derive(Debug, Serialize, Deserialize, Clone, PartialEq)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum MessageType {
    Record,
    State,
    Log,
    Spec,
    ConnectionStatus,
    Catalog,
}

#[derive(Debug, Serialize, Deserialize, Clone, Validate)]
#[serde(rename_all = "camelCase")]
pub struct Message {
    #[serde(rename = "type")]
    pub message_type: MessageType,

    pub log: Option<Log>,
    pub state: Option<State>,
    pub record: Option<Record>,
    pub connection_status: Option<ConnectionStatus>,
    pub spec: Option<Spec>,
    #[validate]
    pub catalog: Option<Catalog>,
}

#[derive(Debug, Serialize, Deserialize, JsonSchema, Clone)]
#[serde(rename_all = "camelCase")]
// ResourceSpec is the configuration for Airbyte source streams.
pub struct ResourceSpec {
    pub stream: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub namespace: Option<String>,
    pub sync_mode: SyncMode,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub cursor_field: Option<Vec<String>>,
}
