use super::Connector;
use crate::command::*;
use anyhow::Result;
use async_trait::async_trait;
use clap::Parser;

#[async_trait]
pub trait SourceConnector: Connector {
    async fn main(&self) -> Result<()> {
        let command = SourceCommand::parse();
        self.run(&command).await
    }

    async fn run(&self, command: &SourceCommand) -> Result<()> {
        use SourceCommand::*;
        match command {
            Spec(command) => self.spec_command(&command).await,
            Check(command) => self.check_command(&command).await,
            _ => todo!(),
        }
    }
}
