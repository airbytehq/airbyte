use std::num::ParseIntError;

use bytes::Bytes;
use futures::{TryStream, Stream, TryStreamExt};
use validator::ValidationErrors;

use crate::apis::InterceptorStream;

#[derive(thiserror::Error, Debug)]
pub enum Error {
    #[error("Failed to execute command: {0}")]
    CommandExecutionError(String),

    #[error("Unable to create an IO pipe to the connector")]
    MissingIOPipe,

    #[error(transparent)]
    IOError(#[from] std::io::Error),

    #[error(transparent)]
    JsonError(#[from] serde_json::Error),

    #[error("ATF Connector's pending checkpoint was not committed, this can happen if the connector exits abruptly")]
    CheckpointPending,

    #[error("Stream is empty, expected to find a message but could not find any")]
    EmptyStream,

    #[error("Could not find expected message in stream: {0}")]
    MessageNotFound(&'static str),

    #[error("{0}")]
    ConnectionStatusUnsuccessful(String),

    #[error("Validation request is missing")]
    MissingValidateRequest,

    #[error("Connector output a Record that does not belong to any known stream: {0}")]
    DanglingConnectorRecord(String),

    #[error("Invalid PullResponse received from connector")]
    InvalidPullResponse,

    #[error("Invalid connector catalog: {0}")]
    InvalidCatalog(ValidationErrors),

    #[error("Adapting ATF schema to Flow: {0}")]
    InvalidSchema(String),

    #[error("Adapting ATF schema to Flow: {0}")]
    InvalidMapping(String),

    #[error("Invalid primary key patch file: {0}")]
    InvalidPKPatch(String),

    #[error("Unknown operation: {0}")]
    UnknownOperation(String),

    #[error("Connector has been idle")]
    IdleConnector,

    #[error("Could not parse run interval")]
    ParseIntError(#[from] ParseIntError)
}

pub fn raise_err<T>(message: &str) -> Result<T, std::io::Error> {
    Err(create_custom_error(message))
}

pub fn create_custom_error(message: &str) -> std::io::Error {
    std::io::Error::new(std::io::ErrorKind::Other, message)
}

pub fn interceptor_stream_to_io_stream(stream: InterceptorStream) -> impl TryStream<Item = std::io::Result<Bytes>, Ok = Bytes, Error = std::io::Error> {
    stream.map_err(|e| create_custom_error(&e.to_string()))
}

pub fn io_stream_to_interceptor_stream(stream: impl Stream<Item = std::io::Result<Bytes>> + Send + Sync + 'static) -> InterceptorStream {
    Box::pin(stream.map_err(|e| Error::IOError(e)))
}
