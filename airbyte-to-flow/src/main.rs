use anyhow::Context;
use clap::Parser;
use flow_cli_common::{init_logging, LogArgs};

pub mod apis;
pub mod connector_runner;
pub mod errors;
pub mod interceptors;
pub mod libs;

use apis::FlowCaptureOperation;
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

fn main() -> anyhow::Result<()> {
    let Args {
        connector_entrypoint,
        operation,
        log_args,
    } = Args::parse();
    init_logging(&log_args);

    let runtime = tokio::runtime::Builder::new_current_thread()
        .enable_all()
        .build()
        .context("building tokio runtime")?;

    let result = runtime.block_on(run_airbyte_source_connector(connector_entrypoint, operation));

    // Explicitly call Runtime::shutdown_background as an alternative to calling Runtime::Drop.
    // This shuts down the runtime without waiting for blocking background tasks to complete,
    // which is good because they likely never will. Consider a blocking call to read from stdin,
    // where the sender is itself waiting for us to exit or write to our stdout.
    // (Note that tokio::io maps AsyncRead of file descriptors to blocking tasks under the hood).
    runtime.shutdown_background();

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
