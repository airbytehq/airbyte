use super::Connector;
use crate::{command::*, types::*};
use anyhow::{Context, Result};
use async_trait::async_trait;
use clap::Parser;
use futures::StreamExt;
use serde_json::from_str;
use tokio::fs::read_to_string;

/// Airbyte Target Connector.
#[async_trait]
pub trait TargetConnector: Connector {
    /// Launch connector.
    async fn main(&self) -> Result<()> {
        let command = TargetCommand::parse();
        self.run(&command).await
    }

    /// Handle write command.
    ///
    /// Listens on standard input for messages and writes to the destination.
    async fn write_command(&self, command: &WriteCommand) -> Result<()> {
        // read and parse catalog
        let catalog = self.catalog_read(&command.catalog).await.context("Reading catalog")?;
        let config = self.config_read(&command.config).await.context("Reading config")?;

        // handle messages
        let mut messages = self.message_stream().await;
        while let Some(message) = messages.next().await {
            let message = message.context("Decoding message")?;
            match message {
                Message::Record(record) => self.write_record(&config, &catalog, record).await?,
                _ => todo!(),
            }
        }

        self.write_finish(&config, &catalog).await?;

        Ok(())
    }

    /// Write a single record.
    async fn write_record(
        &self,
        config: &Self::Config,
        catalog: &AirbyteCatalog,
        record: AirbyteRecordMessage,
    ) -> Result<()>;

    /// Finish writing.
    async fn write_finish(&self, config: &Self::Config, catalog: &AirbyteCatalog) -> Result<()> {
        Ok(())
    }

    /// Run the specified command.
    async fn run(&self, command: &TargetCommand) -> Result<()> {
        use TargetCommand::*;
        match command {
            Spec(command) => self.spec_command(&command).await,
            Check(command) => self.check_command(&command).await,
            Write(command) => self.write_command(&command).await,
        }
    }
}
