use bytes::Bytes;
use futures::{TryStream, Stream, TryStreamExt};
use validator::ValidationErrors;

use crate::apis::InterceptorStream;

#[derive(thiserror::Error, Debug)]
pub enum Error {
    #[error("go.estuary.dev/E001: Network Tunnel startup timeout of 5 seconds exceeded. Please troubleshoot your network tunnel configuration and connection and try again")]
    ChannelTimeoutError,

    #[error("go.estuary.dev/E002: Failed to execute command: {0}")]
    CommandExecutionError(String),

    #[error("go.estuary.dev/E003: {0:?} key already exists in connector's endpoint specification schema, unable to add this key to the endpoint specification schema")]
    DuplicatedKeyError(&'static str),

    #[error("go.estuary.dev/E004: Unable to find the entrypoint of the connector's container. Please make sure your container defines a valid entrypoint")]
    EmptyEntrypointError,

    #[error("go.estuary.dev/E005: Unable to parse the container image inspect file")]
    InvalidImageInspectFile,

    #[error("go.estuary.dev/E006: Unable to create an IO pipe to the connector")]
    MissingIOPipe,

    #[error("go.estuary.dev/E007: The connector's protocol does not match the requested protocol. Connector protocol is {0}, requested protocol is {1}")]
    MismatchingRuntimeProtocol(String, &'static str),

    #[error("go.estuary.dev/E008: IO Error")]
    IOError(#[from] std::io::Error),

    #[error("go.estuary.dev/E009: Json Error")]
    JsonError(#[from] serde_json::Error),

    #[error("go.estuary.dev/E010: Decoding protobuf RPC messages")]
    MessageDecodeError(#[from] prost::DecodeError),

    #[error("go.estuary.dev/E010: Encoding protobuf RPC messages")]
    MessageEncodeError(#[from] prost::EncodeError),

    #[error("go.estuary.dev/E011: Missing required image inspect file. Specify it via --image-inspect-json-path in command line")]
    MissingImageInspectFile,

    #[error("go.estuary.dev/E013: Creating and persisting temporary file")]
    TempfilePersistError(#[from] tempfile::PersistError),

    #[error("go.estuary.dev/E014: Executing and joining a concurrent task failed")]
    TokioTaskExecutionError(#[from] tokio::task::JoinError),

    #[error("go.estuary.dev/E015: Airbyte connector's pending checkpoint was not committed, this can happen if the connector exits abruptly")]
    AirbyteCheckpointPending,

    #[error("go.estuary.dev/E016: Stream is empty, expected to find a message but could not find any")]
    EmptyStream,

    #[error("go.estuary.dev/E017: Could not find expected message in stream: {0}")]
    MessageNotFound(&'static str),

    #[error("go.estuary.dev/E018: Connector's connection status is not successful")]
    ConnectionStatusUnsuccessful,

    #[error("go.estuary.dev/E019: Validation request is missing")]
    MissingValidateRequest,

    #[error("go.estuary.dev/E020: Connector output a record that does not belong to any known stream: {0}")]
    DanglingConnectorRecord(String),

    #[error("go.estuary.dev/E021: Invalid PullResponse received from connector")]
    InvalidPullResponse,

    #[error("go.estuary.dev/E023: Invalid connector catalog: {0}")]
    InvalidCatalog(ValidationErrors),

    #[error("go.estuary.dev/E032: Invalid socket specification: {0}")]
    InvalidSocketSpecification(String),

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
