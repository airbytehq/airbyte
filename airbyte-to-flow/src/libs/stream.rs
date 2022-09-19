use crate::libs::airbyte_catalog::Message;
use crate::{apis::InterceptorStream, errors::create_custom_error};

use crate::errors::raise_err;
use bytelines::AsyncByteLines;
use bytes::Bytes;
use futures::{StreamExt, TryStream, TryStreamExt};
use tokio_util::io::StreamReader;
use validator::Validate;

use super::airbyte_catalog::{Log, LogLevel, MessageType};
use super::protobuf::decode_message;

// Creates a stream of bytes of lines from the given stream
// This allows our other methods such as stream_airbyte_responses to operate
// on lines, simplifying their logic
pub fn stream_lines(
    in_stream: InterceptorStream,
) -> impl TryStream<Item = std::io::Result<Bytes>, Error = std::io::Error, Ok = bytes::Bytes> {
    AsyncByteLines::new(StreamReader::new(in_stream))
        .into_stream()
        .map_ok(Bytes::from)
}

/// Given a stream of lines, try to deserialize them into Airbyte Messages.
/// This can be used when reading responses from the Airbyte connector, and will
/// handle validation of messages as well as handling of AirbyteLogMessages.
/// Will ignore* lines that cannot be parsed to an AirbyteMessage.
/// * See https://docs.airbyte.com/understanding-airbyte/airbyte-specification#the-airbyte-protocol
pub fn stream_airbyte_responses(
    in_stream: InterceptorStream,
) -> impl TryStream<Item = std::io::Result<Message>, Ok = Message, Error = std::io::Error> {
    stream_lines(in_stream).try_filter_map(|line| async move {
        let message: Message = match serde_json::from_slice(&line) {
            Ok(m) => m,
            Err(e) => {
                // It is currently ambiguous for us whether Airbyte protocol specification
                // mandates that there must be no plaintext or not, as such we handle all
                // errors in parsing of stdout lines by logging the issue, but not failing
                Message {
                    message_type: MessageType::Log,
                    connection_status: None,
                    state: None,
                    record: None,
                    spec: None,
                    catalog: None,
                    log: Some(Log {
                        level: LogLevel::Debug,
                        message: format!("Encountered error while trying to parse Airbyte Message: {:?} in line {:?}", e, line)
                    })
                }
            }
        };

        message
            .validate()
            .map_err(|e| create_custom_error(&format!("error in validating message {:?}", e)))?;

        Ok(Some(message))
    })
    .try_filter_map(|message| async {
        // For AirbyteLogMessages, log them and then filter them out
        // so that we don't have to handle them elsewhere
        if let Some(log) = message.log {
            log.log();
            Ok(None)
        } else {
            Ok(Some(message))
        }
    })
}

/// Read the given stream and try to find an Airbyte message that matches the predicate
/// ignoring* other message kinds. This can be used to work with Airbyte connector responses.
/// * See https://docs.airbyte.com/understanding-airbyte/airbyte-specification#the-airbyte-protocol
pub fn get_airbyte_response<F: 'static>(
    in_stream: InterceptorStream,
    predicate: F,
) -> impl futures::Future<Output = std::io::Result<Message>>
where
    F: Fn(&Message) -> bool,
{
    async move {
        let stream_head = Box::pin(stream_airbyte_responses(in_stream)).next().await;

        let message = match stream_head {
            Some(m) => m,
            None => return raise_err("Could not find message in stream"),
        }?;

        if predicate(&message) {
            Ok(message)
        } else {
            raise_err("Could not find message matching condition")
        }
    }
}

/// Read the given stream of bytes from runtime and try to decode it to type <T>
pub fn get_decoded_message<'a, T>(
    in_stream: InterceptorStream,
) -> impl futures::Future<Output = std::io::Result<T>>
where
    T: prost::Message + std::default::Default,
{
    async move {
        let mut reader = StreamReader::new(in_stream);
        decode_message::<T, _>(&mut reader)
            .await?
            .ok_or(create_custom_error("missing request"))
    }
}

// Stream bytes from runtime and continuously decode them into message type T in a stream
pub fn stream_runtime_messages<T: prost::Message + std::default::Default>(
    in_stream: InterceptorStream,
) -> impl TryStream<Item = std::io::Result<T>, Ok = T, Error = std::io::Error> {
    let reader = StreamReader::new(in_stream);

    futures::stream::try_unfold(reader, |mut reader| async {
        match decode_message::<T, _>(&mut reader).await {
            Ok(Some(msg)) => Ok(Some((msg, reader))),
            Ok(None) => Ok(None),
            Err(e) => Err(e)
        }
    })
}

#[cfg(test)]
mod test {
    use std::{collections::HashMap, pin::Pin};

    use bytes::BytesMut;
    use futures::stream;
    use proto_flow::{
        flow::EndpointType,
        materialize::{validate_request, ValidateRequest},
    };
    use tokio_util::io::ReaderStream;

    use crate::libs::{
        airbyte_catalog::{ConnectionStatus, MessageType, Status},
        protobuf::encode_message,
    };

    use super::*;

    fn create_stream<T>(
        input: Vec<T>,
    ) -> Pin<Box<impl TryStream<Item = std::io::Result<T>, Ok = T, Error = std::io::Error>>> {
        Box::pin(stream::iter(input.into_iter().map(Ok::<T, std::io::Error>)))
    }

    #[tokio::test]
    async fn test_stream_lines() {
        let line_0 = "{\"test\": \"hello\"}".as_bytes();
        let line_1 = "other".as_bytes();
        let line_2 = "{\"object\": {}}".as_bytes();
        let newline = "\n".as_bytes();
        let mut input = BytesMut::new();
        input.extend_from_slice(line_0);
        input.extend_from_slice(newline);
        input.extend_from_slice(line_1);
        input.extend_from_slice(newline);
        input.extend_from_slice(line_2);
        let stream = create_stream(vec![Bytes::from(input)]);
        let all_bytes = Box::pin(stream_lines(stream));

        let result: Vec<Bytes> = all_bytes.try_collect::<Vec<Bytes>>().await.unwrap();
        assert_eq!(result, vec![line_0, line_1, line_2]);
    }

    #[tokio::test]
    async fn test_stream_airbyte_responses_eof_split_json() {
        let input_message = Message {
            message_type: MessageType::ConnectionStatus,
            log: None,
            state: None,
            record: None,
            spec: None,
            catalog: None,
            connection_status: Some(ConnectionStatus {
                status: Status::Succeeded,
                message: Some("test".to_string()),
            }),
        };
        let input = vec![
            Bytes::from("{\"type\": \"CONNECTION_STATUS\", \"connectionStatus\": {"),
            Bytes::from("\"status\": \"SUCCEEDED\",\"message\":\"test\"}}"),
        ];
        let stream = create_stream(input);

        let mut messages = Box::pin(stream_airbyte_responses(stream));

        let result = messages.next().await.unwrap().unwrap();
        assert_eq!(
            result.connection_status.unwrap(),
            input_message.connection_status.unwrap()
        );
    }

    #[tokio::test]
    async fn test_stream_airbyte_responses_eof_split_json_partial() {
        let input_message = Message {
            message_type: MessageType::ConnectionStatus,
            log: None,
            state: None,
            record: None,
            spec: None,
            catalog: None,
            connection_status: Some(ConnectionStatus {
                status: Status::Succeeded,
                message: Some("test".to_string()),
            }),
        };
        let input = vec![
            Bytes::from("{}\n{\"type\": \"CONNECTION_STATUS\", \"connectionStatus\": {"),
            Bytes::from("\"status\": \"SUCCEEDED\",\"message\":\"test\"}}"),
        ];
        let stream = create_stream(input);

        let mut messages = Box::pin(stream_airbyte_responses(stream));

        let result = messages.next().await.unwrap().unwrap();
        assert_eq!(
            result.connection_status.unwrap(),
            input_message.connection_status.unwrap()
        );
    }

    #[tokio::test]
    async fn test_stream_airbyte_responses_plaintext_mixed() {
        let input_message = Message {
            message_type: MessageType::ConnectionStatus,
            log: None,
            state: None,
            record: None,
            spec: None,
            catalog: None,
            connection_status: Some(ConnectionStatus {
                status: Status::Succeeded,
                message: Some("test".to_string()),
            }),
        };
        let input = vec![
            Bytes::from(
                "I am plaintext!\n{\"type\": \"CONNECTION_STATUS\", \"connectionStatus\": {",
            ),
            Bytes::from("\"status\": \"SUCCEEDED\",\"message\":\"test\"}}"),
        ];
        let stream = create_stream(input);

        let mut messages = Box::pin(stream_airbyte_responses(stream));

        let result = messages.next().await.unwrap().unwrap();
        assert_eq!(
            result.connection_status.unwrap(),
            input_message.connection_status.unwrap()
        );
    }

    #[tokio::test]
    async fn test_get_decoded_message() {
        let msg = ValidateRequest {
            materialization: "materialization".to_string(),
            endpoint_type: EndpointType::AirbyteSource.into(),
            endpoint_spec_json: "{}".to_string(),
            bindings: vec![validate_request::Binding {
                resource_spec_json: "{}".to_string(),
                collection: None,
                field_config_json: HashMap::new(),
            }],
        };

        let msg_buf = encode_message(&msg).unwrap();
        let read_stream = ReaderStream::new(std::io::Cursor::new(msg_buf));

        let stream: InterceptorStream = Box::pin(read_stream);
        let result = get_decoded_message::<ValidateRequest>(stream)
            .await
            .unwrap();

        assert_eq!(result, msg);
    }

    #[tokio::test]
    async fn test_stream_runtime_messages() {
        let msg1 = ValidateRequest {
            materialization: "materialization".to_string(),
            endpoint_type: EndpointType::AirbyteSource.into(),
            endpoint_spec_json: "{}".to_string(),
            bindings: vec![validate_request::Binding {
                resource_spec_json: "{}".to_string(),
                collection: None,
                field_config_json: HashMap::new(),
            }],
        };
        let msg2 = ValidateRequest {
            materialization: "materialization 2".to_string(),
            endpoint_type: EndpointType::AirbyteSource.into(),
            endpoint_spec_json: "{}".to_string(),
            bindings: vec![validate_request::Binding {
                resource_spec_json: "{}".to_string(),
                collection: None,
                field_config_json: HashMap::new(),
            }],
        };

        let msg_buf1 = encode_message(&msg1).unwrap();
        let msg_buf2 = encode_message(&msg2).unwrap();
        let read_stream = ReaderStream::new(std::io::Cursor::new([msg_buf1, msg_buf2].concat()));

        let stream: InterceptorStream = Box::pin(read_stream);
        let result = stream_runtime_messages::<ValidateRequest>(stream)
            .collect::<Vec<std::io::Result<ValidateRequest>>>()
            .await
            .into_iter()
            .filter_map(|item| {
                match item {
                    Ok(msg) => Some(msg),
                    Err(_) => None
                }
            }).collect::<Vec<ValidateRequest>>();

        assert_eq!(result, vec![msg1, msg2]);
    }
}
