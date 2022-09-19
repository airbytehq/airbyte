use clap::Parser;
use flow_cli_common::{init_logging, LogArgs};

pub mod apis;
pub mod connector_runner;
pub mod errors;
pub mod interceptors;
pub mod libs;

use apis::FlowCaptureOperation;
use connector_runner::run_airbyte_source_connector;
use errors::Error;

#[derive(clap::Parser, Debug)]
#[clap(about = "Command to start an Airbyte to Flow protocol adaptor")]
pub struct Args {
    /// The command used to run the underlying airbyte connector
    #[clap(long)]
    connector_entrypoint: String,

    operation: FlowCaptureOperation,

    #[clap(long)]
    socket: String,

    #[clap(long)]
    stream_mode: StreamMode,

    #[clap(flatten)]
    log_args: LogArgs,
}

#[tokio::main]
async fn main() {
    let Args {
        connector_entrypoint,
        operation,
        socket,
        log_args,
    } = Args::parse();
    init_logging(&log_args);

    let result = run_airbyte_source_connector(connector_entrypoint, operation, socket).await;

    match result {
        Err(Error::CommandExecutionError(_)) => {
            // This error summarizes an error of a child process.
            // As its stderr is passed through, we don't log its failure again here.
            std::process::exit(1);
        }
        Err(err) => {
            tracing::error!(error = ?err, message = "airbyte-to-flow failed");
            std::process::exit(1);
        }
        Ok(()) => {
            tracing::info!(message = "airbyte-to-flow exiting");
        }
    }
}
