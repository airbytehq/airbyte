use crate::{command::*, types::*};
use anyhow::Result;
use async_trait::async_trait;
use bytes::BytesMut;
use futures::stream::{BoxStream, StreamExt, TryStreamExt};
use schemars::{schema::RootSchema, schema_for, JsonSchema};
use serde::de::DeserializeOwned;
use serde_json::from_str;
use std::path::Path;
use thiserror::Error;
use tokio::{
    fs::read_to_string,
    io::{stdin, Stdin},
};
use tokio_serde::{formats::SymmetricalJson as Json, SymmetricallyFramed as SerdeFramed};
use tokio_util::codec::{FramedRead, LinesCodec, LinesCodecError};

mod source;
mod target;

pub use source::SourceConnector;
pub use target::TargetConnector;

/// Error in the [`Message`] stream.
#[derive(Error, Debug)]
pub enum MessageStreamError {
    #[error("error in underlying message stream")]
    Underlying(#[from] LinesCodecError),
    #[error("error decoding message from JSON")]
    Decoding(#[from] serde_json::Error),
    #[error("error parsing AirbyteMessage")]
    Coverting(#[from] ParseAirbyteMessageError),
}

/// Airbyte Connector.
#[async_trait]
pub trait Connector: Sized {
    /// Configuration object for this connector.
    type Config: DeserializeOwned + JsonSchema + Send + Sync;

    /// Return JSON schema for configuration.
    fn config_schema(&self) -> RootSchema {
        schema_for!(Self::Config)
    }

    /// Read config from path.
    async fn config_read(&self, path: &Path) -> Result<Self::Config> {
        let catalog = read_to_string(&path).await?;
        Ok(from_str(&catalog)?)
    }

    /// Read catalog from path.
    async fn catalog_read(&self, path: &Path) -> Result<AirbyteCatalog> {
        let catalog = read_to_string(&path).await?;
        Ok(from_str(&catalog)?)
    }

    /// Return connector specification.
    fn connector_specification(&self) -> ConnectorSpecification {
        let schema = self.config_schema();
        ConnectorSpecification {
            connection_specification: schema,
            supported_destination_sync_modes: Some(vec![DestinationSyncMode::Overwrite]),
            documentation_url: Some("https://example.com".parse().unwrap()),
            supports_incremental: Some(true),
            supports_normalization: Some(false),
            supports_dbt: Some(false),
            ..Default::default()
        }
    }

    /// Message stream.
    ///
    /// Read decoded messages from standard input.
    async fn message_stream(&self) -> BoxStream<'static, Result<Message, MessageStreamError>> {
        // start with standard input stream
        let stdin = stdin();
        // decode newline-separated messages
        let messages = FramedRead::new(stdin, LinesCodec::new())
            .map_ok(|r| BytesMut::from(r.as_bytes()))
            .map_err(MessageStreamError::from);
        // decode messages as AirbyteMessage JSON and turn into Message enum
        let messages = SerdeFramed::new(messages, Json::<AirbyteMessage>::default())
            .map(|m| m.and_then(|m| Ok(Message::try_from(m)?)));
        // box for type erasure
        Box::pin(messages)
    }

    /// Send a message.
    async fn message_send(&self, message: &Message) -> Result<()> {
        Ok(())
    }

    /// Handle spec command.
    ///
    /// This command returns the specification for this connector.
    async fn spec_command(&self, command: &SpecCommand) -> Result<()> {
        Message::Spec(self.connector_specification())
            .airbyte_message()
            .send();
        Ok(())
    }

    /// Handle check command.
    ///
    /// This command checks the configuration for this connector.
    async fn check_command(&self, command: &CheckCommand) -> Result<()> {
        let result = match self.config_read(&command.config).await {
            Ok(_) => AirbyteConnectionStatus {
                status: Status::Succeeded,
                message: None,
            },
            Err(error) => AirbyteConnectionStatus {
                status: Status::Failed,
                message: Some(error.to_string()),
            },
        };
        let message = Message::ConnectionStatus(result);
        message.airbyte_message().send();
        Ok(())
    }
}
