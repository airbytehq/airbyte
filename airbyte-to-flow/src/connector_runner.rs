use std::{pin::Pin, sync::{Arc}, ops::DerefMut};

use flow_cli_common::LogArgs;
use futures::{channel::oneshot, stream, StreamExt};
use tokio::{io::{AsyncWrite, copy}, process::{ChildStdout, ChildStdin, Child}, sync::Mutex};
use tokio_util::io::{ReaderStream, StreamReader};

use proto_flow::capture::Response;
use proto_flow::capture::response;
use proto_flow::flow::ConnectorState;

use crate::{apis::{InterceptorStream, FlowCaptureOperation}, interceptors::airbyte_source_interceptor::AirbyteSourceInterceptor, errors::{Error, io_stream_to_interceptor_stream, interceptor_stream_to_io_stream}, libs::{command::{invoke_connector_delayed, check_exit_status}, protobuf::{decode_message, encode_message}}};

async fn flow_read_stream() -> InterceptorStream {
    Box::pin(io_stream_to_interceptor_stream(ReaderStream::new(tokio::io::stdin())))
}

fn flow_write_stream() -> Arc<Mutex<Pin<Box<dyn AsyncWrite + Send + Sync>>>> {
    Arc::new(Mutex::new(Box::pin(tokio::io::stdout())))
}

fn airbyte_response_stream(child_stdout: ChildStdout) -> InterceptorStream {
    Box::pin(io_stream_to_interceptor_stream(ReaderStream::new(child_stdout)))
}

pub fn parse_child(mut child: Child) -> Result<(Child, ChildStdin, ChildStdout), Error> {
    let stdout = child.stdout.take().ok_or(Error::MissingIOPipe)?;
    let stdin = child.stdin.take().ok_or(Error::MissingIOPipe)?;

    Ok((child, stdin, stdout))
}

pub async fn run_airbyte_source_connector(
    entrypoint: String,
    op: FlowCaptureOperation,
    log_args: &LogArgs,
) -> Result<(), Error> {
    let mut airbyte_interceptor = AirbyteSourceInterceptor::new();

    let args = airbyte_interceptor.adapt_command_args(&op);
    let full_entrypoint = format!("{} \"{}\"", entrypoint, args.join("\" \""));
    let log_level = log_args.level.to_string();

    let (mut child, child_stdin, child_stdout) =
        parse_child(invoke_connector_delayed(full_entrypoint, log_level)?)?;

    // std::thread::sleep(std::time::Duration::from_secs(400));
    let adapted_request_stream = airbyte_interceptor.adapt_request_stream(
        &op,
        flow_read_stream().await
    )?;

    let adapted_response_stream =
        airbyte_interceptor.adapt_response_stream(&op, airbyte_response_stream(child_stdout))?;

    // Keep track of whether we did send a Driver Checkpoint as the final message of the response stream
    // See the comment of the block below for why this is necessary
    let (tp_sender, tp_receiver) = oneshot::channel::<bool>();
    let adapted_response_stream = if op == FlowCaptureOperation::Pull {
        Box::pin(stream::try_unfold(
            (false, adapted_response_stream, tp_sender),
            |(transaction_pending, mut stream, sender)| async move {
                let (message, raw) = match stream.next().await {
                    Some(bytes) => {
                        let bytes = bytes?;
                        let mut buf = &bytes[..];
                        // This is infallible because we must encode a Response in response to
                        // a Request. See airbyte_source_interceptor.adapt_pull_response_stream
                        let msg = decode_message::<Response, _>(&mut buf)
                            .await
                            .unwrap()
                            .unwrap();
                        (msg, bytes)
                    }
                    None => {
                        sender.send(transaction_pending).map_err(|_| Error::AirbyteCheckpointPending)?;
                        return Ok(None);
                    }
                };

                Ok(Some((raw, (!message.checkpoint.is_some(), stream, sender))))
            },
        ))
    } else {
        adapted_response_stream
    };

    let response_write = flow_write_stream();

    let streaming_all_task = streaming_all(
        adapted_request_stream,
        child_stdin,
        Box::pin(adapted_response_stream),
        response_write.clone(),
    );

    let cloned_op = op.clone();
    let exit_status_task = async move {
        let exit_status_result = check_exit_status("airbyte-to-flow:", child.wait().await);

        // There are some Airbyte connectors that write records, and exit successfully, without ever writing
        // a state (checkpoint). In those cases, we want to provide a default empty checkpoint. It's important that
        // this only happens if the connector exit successfully, otherwise we risk double-writing data.
        if exit_status_result.is_ok() && cloned_op == FlowCaptureOperation::Pull {
            tracing::debug!("airbyte-to-flow: waiting for tp_receiver");
            // the received value (transaction_pending) is true if the connector writes output messages and exits _without_ writing
            // a final state checkpoint.
            if tp_receiver.await.unwrap() {
                // We generate a synthetic commit now, and the empty checkpoint means the assumed behavior
                // of the next invocation will be "full refresh".
                tracing::warn!("go.estuary.dev/W001: connector exited without writing a final state checkpoint, writing an empty object {{}} merge patch driver checkpoint.");
                let mut response = Response::default();
                response.checkpoint = Some(response::Checkpoint {
                    state: Some(ConnectorState {
                        updated_json: "{}".to_string(),
                        merge_patch: true,
                    })
                });
                let encoded_response = &encode_message(&response)?;
                let mut buf = &encoded_response[..];
                let mut writer = response_write.lock().await;
                copy(&mut buf, writer.deref_mut()).await?;
            }
        }

        if exit_status_result.is_ok() {
            // We wait a few seconds to let any remaining writes to be done
            // since the select below will not wait for `streaming_all` task to finish
            // once exit_status has been received.
            tokio::time::sleep(tokio::time::Duration::from_secs(5)).await;
        }

        exit_status_result
    };

    // If streaming_all_task errors out, we error out and don't wait for exit_status, on the other
    // hand once the connector has exit (exit_status_task completes), we don't wait for streaming
    // task anymore
    tokio::select! {
        Err(e) = streaming_all_task => Err(e),
        resp = exit_status_task => resp,
    }?;

    tracing::debug!("airbyte-to-flow: connector_runner done");
    Ok(())
}

/// Stream request_stream into request_stream_writer and response_stream into
/// response_stream_writer.
async fn streaming_all(
    request_stream: InterceptorStream,
    mut request_stream_writer: ChildStdin,
    response_stream: InterceptorStream,
    response_stream_writer: Arc<Mutex<Pin<Box<dyn AsyncWrite + Sync + Send>>>>,
) -> Result<(), Error> {
    let mut request_stream_reader = StreamReader::new(interceptor_stream_to_io_stream(request_stream));
    let mut response_stream_reader = StreamReader::new(interceptor_stream_to_io_stream(response_stream));

    let request_stream_copy = async move {
        copy(&mut request_stream_reader, &mut request_stream_writer).await?;
        tracing::debug!("airbyte-to-flow: request_stream_copy done");
        Ok::<(), std::io::Error>(())
    };

    let response_stream_copy = async move {
        let mut writer = response_stream_writer.lock().await;
        copy(&mut response_stream_reader, writer.deref_mut()).await?;
        tracing::debug!("airbyte-to-flow: response_stream_copy done");
        Ok(())
    };

    tokio::try_join!(
        request_stream_copy,
        response_stream_copy
    )?;

    tracing::debug!("airbyte-to-flow: streaming_all finished");
    Ok(())
}
