use bytes::Bytes;
use futures::Stream;
use std::pin::Pin;

use crate::errors::Error;

// An interceptor modifies the request/response streams between Flow runtime and the connector.
// InterceptorStream defines the type of input and output streams handled by interceptors.
pub type InterceptorStream = Pin<Box<dyn Stream<Item = Result<Bytes, Error>> + Send + Sync>>;
