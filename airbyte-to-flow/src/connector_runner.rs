use std::pin::Pin;

use futures::{channel::oneshot, stream, StreamExt};
use tokio::{net::{UnixStream, TcpStream}, task::JoinHandle, io::{AsyncWrite, copy}, process::{ChildStdout, ChildStdin, Child}};
use tokio_util::io::{ReaderStream, StreamReader};

use proto_flow::capture::PullResponse;
use proto_flow::flow::DriverCheckpoint;

use crate::{apis::{InterceptorStream, FlowCaptureOperation, StreamMode}, interceptors::airbyte_source_interceptor::AirbyteSourceInterceptor, errors::{Error, io_stream_to_interceptor_stream, interceptor_stream_to_io_stream}, libs::{command::{invoke_connector_delayed, check_exit_status}, protobuf::{decode_message, encode_message}}};

async fn flatten_join_handle<T, E: std::convert::From<tokio::task::JoinError>>(
    handle: JoinHandle<Result<T, E>>,
) -> Result<T, E> {
    match handle.await {
        Ok(Ok(result)) => Ok(result),
        Ok(Err(err)) => Err(err),
        Err(err) => Err(err.into()),
    }
}

async fn flow_read_stream(socket_path: &str, mode: &StreamMode) -> Result<InterceptorStream, Error> {
    match mode {
        StreamMode::UnixSocket => 
            Ok(Box::pin(io_stream_to_interceptor_stream(ReaderStream::new(UnixStream::connect(&socket_path).await?)))),
        StreamMode::TCP =>
            Ok(Box::pin(io_stream_to_interceptor_stream(ReaderStream::new(TcpStream::connect(&socket_path).await?))))
    }
}

async fn flow_write_stream(socket_path: &str, mode: &StreamMode) -> Result<Pin<Box<dyn AsyncWrite + Send>>, Error> {
    match mode {
        StreamMode::UnixSocket => 
            Ok(Box::pin(UnixStream::connect(socket_path).await?)),
        StreamMode::TCP =>
            Ok(Box::pin(TcpStream::connect(socket_path).await?))
    }
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
    socket_path: String,
    stream_mode: StreamMode,
) -> Result<(), Error> {
    let mut airbyte_interceptor = AirbyteSourceInterceptor::new();

    let args = airbyte_interceptor.adapt_command_args(&op);
    let full_entrypoint = format!("{} \"{}\"", entrypoint, args.join("\" \""));

    let (mut child, child_stdin, child_stdout) =
        parse_child(invoke_connector_delayed(full_entrypoint)?)?;

    let adapted_request_stream = airbyte_interceptor.adapt_request_stream(
        &op,
        flow_read_stream(&socket_path, &stream_mode).await?
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
                        // This is infallible because we must encode a PullResponse in response to
                        // a PullRequest. See airbyte_source_interceptor.adapt_pull_response_stream
                        let msg = decode_message::<PullResponse, _>(&mut buf)
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

    let response_write = flow_write_stream(&socket_path, &stream_mode).await?;

    let streaming_all_task = tokio::spawn(streaming_all(
        child_stdin,
        adapted_request_stream,
        adapted_response_stream,
        response_write,
    ));

    let cloned_op = op.clone();
    let exit_status_task = tokio::spawn(async move {
        let exit_status_result = check_exit_status("airbyte source connector:", child.wait().await);

        // There are some Airbyte connectors that write records, and exit successfully, without ever writing
        // a state (checkpoint). In those cases, we want to provide a default empty checkpoint. It's important that
        // this only happens if the connector exit successfully, otherwise we risk double-writing data.
        if exit_status_result.is_ok() && cloned_op == FlowCaptureOperation::Pull {
            // the received value (transaction_pending) is true if the connector writes output messages and exits _without_ writing
            // a final state checkpoint.
            if tp_receiver.await.unwrap() {
                // We generate a synthetic commit now, and the empty checkpoint means the assumed behavior
                // of the next invocation will be "full refresh".
                tracing::warn!("go.estuary.dev/W001: connector exited without writing a final state checkpoint, writing an empty object {{}} merge patch driver checkpoint.");
                let mut resp = PullResponse::default();
                resp.checkpoint = Some(DriverCheckpoint {
                    driver_checkpoint_json: b"{}".to_vec(),
                    rfc7396_merge_patch: true,
                });
                let encoded_response = &encode_message(&resp)?;
                let mut buf = &encoded_response[..];
                copy(&mut buf, &mut tokio::io::stdout()).await?;
            }
        }

        // Once the airbyte connector has exited, we must close stdout of connector_proxy
        // so that the runtime knows the RPC is over. In turn, the runtime will close the stdin
        // from their end. This is necessary to avoid a deadlock where runtime is waiting for
        // connector_proxy to close stdout, and connector_proxy is waiting for runtime to close
        // stdin.
        if exit_status_result.is_ok() {
            // We wait a few seconds to let any remaining writes to be done
            tokio::time::sleep(tokio::time::Duration::from_secs(5)).await;
            std::process::exit(0);
        }

        exit_status_result
    });

    tokio::try_join!(
        flatten_join_handle(streaming_all_task),
        flatten_join_handle(exit_status_task)
    )?;

    Ok(())
}

async fn streaming_all(
    mut request_stream_writer: ChildStdin,
    request_stream: InterceptorStream,
    response_stream: InterceptorStream,
    mut response_stream_writer: Pin<Box<dyn AsyncWrite + Send>>,
) -> Result<(), Error> {
    let mut request_stream_reader = StreamReader::new(interceptor_stream_to_io_stream(request_stream));
    let mut response_stream_reader = StreamReader::new(interceptor_stream_to_io_stream(response_stream));

    let request_stream_copy =
        tokio::spawn(
            async move { copy(&mut request_stream_reader, &mut request_stream_writer).await },
        );

    let response_stream_copy = tokio::spawn(async move {
        copy(&mut response_stream_reader, &mut response_stream_writer).await
    });

    let (req_stream_bytes, resp_stream_bytes) = tokio::try_join!(
        flatten_join_handle(request_stream_copy),
        flatten_join_handle(response_stream_copy)
    )?;

    tracing::debug!(
        req_stream = req_stream_bytes,
        resp_stream = resp_stream_bytes,
        "streaming_all finished"
    );
    Ok(())
}
