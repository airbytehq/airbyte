use clap::{Parser, ValueEnum};
use errors::Error;
use flow_cli_common::{init_logging, LogArgs};

pub mod apis;
pub mod connector_runner;
pub mod errors;
pub mod interceptors;
pub mod libs;

use apis::{FlowCaptureOperation, StreamMode};
use connector_runner::run_airbyte_source_connector;

#[derive(clap::Parser, Debug)]
#[clap(about = "Command to start an Airbyte to Flow protocol adaptor")]
pub struct Args {
    /// The command used to run the underlying airbyte connector
    #[clap(long)]
    connector_entrypoint: String,

    #[clap(value_enum)]
    operation: FlowCaptureOperation,

    #[clap(flatten)]
    log_args: LogArgs,
}

#[tokio::main]
async fn main() -> Result<(), Error> {
    let Args {
        connector_entrypoint,
        operation,
        log_args,
    } = Args::parse();
    init_logging(&log_args);

    let stream_mode = StreamMode::TCP;
    let socket = "0.0.0.0:2222";

    let result = run_airbyte_source_connector(connector_entrypoint, operation, socket, stream_mode).await;

    match result {
        Err(err) => {
            Err(err.into())
        }
        Ok(()) => {
            tracing::info!(message = "connector-proxy exiting");
            Ok(())
        }
    }
}
