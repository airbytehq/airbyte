use schemars::schema::RootSchema;
use serde::{Deserialize, Serialize};
use serde_json::Value;
use thiserror::Error;
use url::Url;

#[derive(Serialize, Deserialize, Clone, Debug, Default)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum MessageType {
    Record,
    State,
    Log,
    Spec,
    ConnectionStatus,
    Catalog,
    #[default]
    Trace,
}

#[derive(Clone, Debug)]
pub enum Message {
    Spec(ConnectorSpecification),
    Record(AirbyteRecordMessage),
    Log(AirbyteLogMessage),
    ConnectionStatus(AirbyteConnectionStatus),
}

impl Message {
    pub fn airbyte_message(self) -> AirbyteMessage {
        self.into()
    }
}

impl From<Message> for AirbyteMessage {
    fn from(message: Message) -> Self {
        match message {
            Message::Spec(item) => Self {
                r#type: MessageType::Spec,
                spec: Some(item),
                ..Default::default()
            },
            Message::Record(item) => Self {
                r#type: MessageType::Record,
                record: Some(item),
                ..Default::default()
            },
            Message::Log(item) => Self {
                r#type: MessageType::Log,
                log: Some(item),
                ..Default::default()
            },
            Message::ConnectionStatus(item) => Self {
                r#type: MessageType::ConnectionStatus,
                connection_status: Some(item),
                ..Default::default()
            },
        }
    }
}

#[derive(Error, Debug)]
pub enum ParseAirbyteMessageError {
    #[error("missing data")]
    MissingData,
}

impl TryFrom<AirbyteMessage> for Message {
    type Error = ParseAirbyteMessageError;

    fn try_from(message: AirbyteMessage) -> Result<Self, Self::Error> {
        use MessageType::*;
        use ParseAirbyteMessageError::MissingData;
        let result = match message.r#type {
            Spec => Message::Spec(message.spec.ok_or(MissingData)?),
            Record => Message::Record(message.record.ok_or(MissingData)?),
            Log => Message::Log(message.log.ok_or(MissingData)?),
            ConnectionStatus => {
                Message::ConnectionStatus(message.connection_status.ok_or(MissingData)?)
            }
            _ => todo!(),
        };
        Ok(result)
    }
}

#[derive(Serialize, Deserialize, Clone, Debug, Default)]
#[serde(rename_all = "camelCase")]
pub struct AirbyteMessage {
    pub r#type: MessageType,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub spec: Option<ConnectorSpecification>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub record: Option<AirbyteRecordMessage>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub log: Option<AirbyteLogMessage>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub connection_status: Option<AirbyteConnectionStatus>,
}

impl AirbyteMessage {
    pub fn send(&self) {
        println!("{}", serde_json::to_string(&self).unwrap());
    }
}

#[derive(Serialize, Deserialize, Clone, Debug, Default)]
#[serde(rename_all = "lowercase")]
pub enum DestinationSyncMode {
    #[default]
    Overwrite,
    Append,
}

#[derive(Serialize, Deserialize, Clone, Debug, Default)]
#[serde(rename_all = "snake_case")]
pub enum SyncMode {
    #[default]
    FullRefresh,
    Incremental,
}

#[derive(Serialize, Deserialize, Clone, Debug, Default)]
#[serde(rename_all = "camelCase")]
pub struct ConnectorSpecification {
    /// Airbyte Protocol version supported by the connector.
    #[serde(rename = "protocol_version")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub protocol_version: Option<String>,
    pub connection_specification: RootSchema,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub documentation_url: Option<Url>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub changelog_url: Option<Url>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub supports_normalization: Option<bool>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub supports_incremental: Option<bool>,
    #[serde(skip_serializing_if = "Option::is_none")]
    #[serde(rename = "supportsDBT")]
    pub supports_dbt: Option<bool>,
    #[serde(
        skip_serializing_if = "Option::is_none",
        rename = "supported_destination_sync_modes"
    )]
    pub supported_destination_sync_modes: Option<Vec<DestinationSyncMode>>,
}

#[derive(Serialize, Deserialize, Clone, Debug, Default)]
pub struct AirbyteCatalog {
    pub streams: Vec<ConfiguredAirbyteStream>,
}

#[derive(Serialize, Deserialize, Clone, Debug, Default)]
pub struct ConfiguredAirbyteStream {
    pub stream: AirbyteStream,
    pub sync_mode: SyncMode,
    pub cursor_field: Vec<String>,
    pub destination_sync_mode: DestinationSyncMode,
    pub primary_key: Value,
}

#[derive(Serialize, Deserialize, Clone, Debug, Default)]
pub struct AirbyteStream {
    pub name: String,
    pub json_schema: RootSchema,
}

#[derive(Serialize, Deserialize, Clone, Debug, Default)]
pub struct AirbyteRecordMessage {
    #[serde(default)]
    pub namespace: Option<String>,
    pub stream: String,
    pub data: Value,
    pub emitted_at: u64,
}

#[derive(Serialize, Deserialize, Clone, Debug, Default)]
pub struct AirbyteStateMessage {
    pub state: Value,
}

#[derive(Serialize, Deserialize, Clone, Debug, Default)]
#[serde(rename_all = "UPPERCASE")]
pub enum LogLevel {
    Fatal,
    Error,
    Warn,
    #[default]
    Info,
    Debug,
    Trace,
}

#[derive(Serialize, Deserialize, Clone, Debug, Default)]
pub struct AirbyteLogMessage {
    pub level: LogLevel,
    pub message: String,
    #[serde(default)]
    pub stack_trace: Option<String>,
}

#[derive(Serialize, Deserialize, Clone, Debug, Default)]
#[serde(rename_all = "UPPERCASE")]
pub enum Status {
    #[default]
    Succeeded,
    Failed,
}

#[derive(Serialize, Deserialize, Clone, Debug, Default)]
pub struct AirbyteConnectionStatus {
    pub status: Status,
    #[serde(skip_serializing_if = "Option::is_none", default)]
    pub message: Option<String>,
}

#[test]
fn test_deserialize_destination_catalog() {
    serde_json::from_str::<AirbyteCatalog>(include_str!("../test_data/destination_catalog.json"))
        .unwrap();
}
