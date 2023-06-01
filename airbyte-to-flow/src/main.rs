use anyhow::Context;
use clap::{Parser, ValueEnum};
use errors::Error;
use flow_cli_common::{init_logging, LogArgs, LogLevel};

pub mod apis;
pub mod connector_runner;
pub mod errors;
pub mod interceptors;
pub mod libs;

use connector_runner::run_airbyte_source_connector;

#[derive(clap::Parser, Debug)]
/// airbyte-to-flow sits in-between an airbyte connector and Flow
/// as an adaptor that reads from connector stdout and writes to connector stdin
/// while on the other hand connects to Flow using a TCP socket
///
/// airbyte-to-flow supports patching of spec schema and document schemas using
/// certain files. Patching is done using RFC7396 JSON Merge Patch and the files
/// are:
/// spec.patch.json -> for patching spec response of airbyte connector
/// oauth2.patch.json -> for patching oauth2 response of airbyte connector
/// documentation_url.patch.json -> for patching documentation url of airbyte connector
/// streams/{stream-name}.patch.json -> for patching document schema of stream {stream-name}
pub struct Args {
    /// The command used to run the underlying airbyte connector
    #[clap(long)]
    connector_entrypoint: String,
}

fn main() -> anyhow::Result<()> {
    let Args {
        connector_entrypoint,
    } = Args::parse();

    let log_level = std::env::var("LOG_LEVEL")
        .ok()
        .and_then(|s| LogLevel::from_str(&s, true).ok())
        .unwrap_or(LogLevel::Info);
    let log_args = LogArgs {
        level: log_level,
        format: None,
    };
    init_logging(&log_args);

    let runtime = tokio::runtime::Builder::new_current_thread()
        .enable_all()
        .build()
        .context("building tokio runtime")?;

    let result = runtime.block_on(run_airbyte_source_connector(
        connector_entrypoint,
        &log_args,
    ));

    // Explicitly call Runtime::shutdown_background as an alternative to calling Runtime::Drop.
    // This shuts down the runtime without waiting for blocking background tasks to complete,
    // which is good because they likely never will. Consider a blocking call to read from stdin,
    // where the sender is itself waiting for us to exit or write to our stdout.
    // (Note that tokio::io maps AsyncRead of file descriptors to blocking tasks under the hood).
    runtime.shutdown_background();

    match result {
        Err(Error::ExitCode(code)) => {
            std::process::exit(code);
        }
        Err(err) => Err(err.into()),
        Ok(()) => {
            tracing::info!(message = "atf exiting");
            Ok(())
        }
    }
}
