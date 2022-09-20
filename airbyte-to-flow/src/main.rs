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

    // We wait for a line of stdin that tells us where the socket is listening on
    let mut buf = String::new();
    let stdin = std::io::stdin();
    stdin.read_line(&mut buf)?;

    // the received line must be in the format of
    // <Protocol> <Address>
    // e.g.: unix-socket /flow-socket
    //       tcp localhost:2222
    let words = buf.split(" ").collect::<Vec<&str>>();
    if words.len() != 2 {
        return Err(Error::InvalidSocketSpecification("socket specification requires two words".to_string()))
    }
    let stream_mode = StreamMode::from_str(words[0], true).map_err(Error::InvalidSocketSpecification)?;
    let socket = words[1].to_string();

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
