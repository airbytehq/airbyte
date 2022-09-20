use bytes::Bytes;
use futures::Stream;
use std::pin::Pin;

use crate::errors::Error;

// Flow Capture operations defined in
// https://github.com/estuary/flow/blob/master/go/protocols/capture/capture.proto
#[derive(Debug, strum_macros::Display, clap::ArgEnum, PartialEq, Clone)]
#[strum(serialize_all = "kebab_case")]
pub enum FlowCaptureOperation {
    Spec,
    Discover,
    Validate,
    ApplyUpsert,
    ApplyDelete,
    Pull,
}

// Mode of streaming, Unix socket or TCP
#[derive(Clone, strum_macros::Display, clap::ArgEnum, PartialEq, Debug)]
#[strum(serialize_all = "kebab_case")]
pub enum StreamMode {
    UnixSocket,
    TCP,
}

// An interceptor modifies the request/response streams between Flow runtime and the connector.
// InterceptorStream defines the type of input and output streams handled by interceptors.
pub type InterceptorStream = Pin<Box<dyn Stream<Item = Result<Bytes, Error>> + Send + Sync>>;
