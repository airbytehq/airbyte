use clap::Parser;
use std::path::PathBuf;

#[derive(Debug, Parser)]
pub enum TargetCommand {
    /// Output JSON specification for configuration.
    Spec(SpecCommand),
    /// Check JSON configuration.
    Check(CheckCommand),
    /// Write data to destination.
    Write(WriteCommand),
}

#[derive(Debug, Parser)]
pub enum SourceCommand {
    /// Output JSON specification for configuration.
    Spec(SpecCommand),
    /// Check JSON configuration.
    Check(CheckCommand),
    /// Detectsand describe the structure of the data in the data store and which Airbyte
    /// configurations can be applied to that data.
    Discover(DiscoverCommand),
    /// Extract data from the underlying data store and emit it.
    Read(ReadCommand),
}

#[derive(Debug, Parser)]
pub struct SpecCommand;

#[derive(Debug, Parser)]
pub struct CheckCommand {
    #[clap(long)]
    pub config: PathBuf,
}

#[derive(Debug, Parser)]
pub struct DiscoverCommand {
    #[clap(long)]
    pub config: PathBuf,
}

#[derive(Debug, Parser)]
pub struct ReadCommand {
    #[clap(long)]
    pub config: PathBuf,

    #[clap(long)]
    pub catalog: PathBuf,

    #[clap(long)]
    pub state: PathBuf,
}

#[derive(Debug, Parser)]
pub struct WriteCommand {
    #[clap(long)]
    pub config: PathBuf,

    #[clap(long)]
    pub catalog: PathBuf,
}
