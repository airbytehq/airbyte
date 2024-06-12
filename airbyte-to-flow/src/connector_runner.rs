use std::{ops::DerefMut, pin::Pin, sync::Arc, time::Instant};

use flow_cli_common::LogArgs;
use futures::{
    channel::{mpsc, oneshot},
    stream, StreamExt, TryStreamExt,
};
use tokio::{
    io::{copy, AsyncWrite, AsyncWriteExt},
    process::{Child, ChildStdin, ChildStdout},
    sync::Mutex,
};
use tokio_util::io::{ReaderStream, StreamReader};

use proto_flow::capture::response;
use proto_flow::capture::Response;
use proto_flow::flow::ConnectorState;

use crate::{
    apis::InterceptorStream,
    errors::{io_stream_to_interceptor_stream, Error},
    interceptors::airbyte_source_interceptor::{AirbyteSourceInterceptor, Operation},
    libs::command::{check_exit_status, invoke_connector_delayed},
};

const NEWLINE: u8 = 10;
const RUN_INTERVAL_FILE_NAME: &str = "run_interval_minutes.json";

async fn flow_read_stream() -> InterceptorStream {
    Box::pin(io_stream_to_interceptor_stream(ReaderStream::new(
        tokio::io::stdin(),
    )))
}

fn flow_write_stream() -> Arc<Mutex<Pin<Box<dyn AsyncWrite + Send + Sync>>>> {
    Arc::new(Mutex::new(Box::pin(tokio::io::stdout())))
}

fn airbyte_response_stream(child_stdout: ChildStdout) -> InterceptorStream {
    Box::pin(io_stream_to_interceptor_stream(ReaderStream::new(
        child_stdout,
    )))
}

pub fn parse_child(mut child: Child) -> Result<(Child, ChildStdin, ChildStdout), Error> {
    let stdout = child.stdout.take().ok_or(Error::MissingIOPipe)?;
    let stdin = child.stdin.take().ok_or(Error::MissingIOPipe)?;

    Ok((child, stdin, stdout))
}

pub async fn run_airbyte_source_connector(
    entrypoint: String,
    log_args: &LogArgs,
) -> Result<(), Error> {
    let mut airbyte_interceptor = AirbyteSourceInterceptor::new();

    let in_stream = flow_read_stream().await;
    let (op, first_request) = airbyte_interceptor.first_request(in_stream).await?;

    let config = first_request.open.as_ref().map(|o| serde_json::from_str::<serde_json::Value>(&o.capture.as_ref().unwrap().config_json));

    let args = airbyte_interceptor.adapt_command_args(&op);
    let full_entrypoint = format!("{} \"{}\"", entrypoint, args.join("\" \""));
    let log_level = log_args.level.to_string();

    let (child, child_stdin, child_stdout) =
        parse_child(invoke_connector_delayed(full_entrypoint, log_level)?)?;

    let adapted_request_stream = airbyte_interceptor.adapt_request_stream(&op, first_request)?;

    let adapted_response_stream =
        airbyte_interceptor.adapt_response_stream(&op, airbyte_response_stream(child_stdout))?;

    // Keep track of whether we did send a Driver Checkpoint as the final message of the response stream
    // See the comment of the block below for why this is necessary
    let (tp_sender, tp_receiver) = oneshot::channel::<bool>();
    let adapted_response_stream = if op == Operation::Capture {
        Box::pin(stream::try_unfold(
            (false, adapted_response_stream, tp_sender),
            |(transaction_pending, mut stream, sender)| async move {
                let (message, raw) = match stream.next().await {
                    Some(bytes) => {
                        let bytes = bytes?;
                        let mut buf = &bytes[..];
                        // This is infallible because we must encode a Response in response to
                        // a Request. See airbyte_source_interceptor.adapt_pull_response_stream
                        let msg = serde_json::from_slice::<Response>(&mut buf)?;
                        (msg, bytes)
                    }
                    None => {
                        sender
                            .send(transaction_pending)
                            .map_err(|_| Error::CheckpointPending)?;
                        return Ok(None);
                    }
                };

                Ok(Some((raw, (!message.checkpoint.is_some(), stream, sender))))
            },
        ))
    } else {
        adapted_response_stream
    }
    .map_ok(|bytes| bytes::Bytes::from([&bytes[..], &[NEWLINE]].concat()));

    // A channel to ping whenever a response is received from the connector
    // this allows us to monitor connectors for long inactivity and restart the connector
    // since it is a known issue that airbyte connectors can "hang"
    // see https://github.com/airbytehq/airbyte/issues/14499
    // https://github.com/airbytehq/airbyte/issues/11252
    // https://github.com/airbytehq/airbyte/issues/11792
    let (mut ping_sender, mut ping_receiver) = mpsc::channel::<()>(1);
    let monitored_response_stream = adapted_response_stream.inspect_ok(move |_| {
        let _ = ping_sender.try_send(());
    });

    // Four hour timeout on inactivity.
    let ping_timeout_task = async move {
        loop {
            tokio::select! {
                Some(_) = ping_receiver.next() => { continue },
                _ = tokio::time::sleep(tokio::time::Duration::from_secs(4 * 3600)) => {
                    tracing::warn!("Connector has been idle for the past four hours. Restarting...");
                    break
                }
            }
        }

        let r: Result<(), Error> = Err(Error::IdleConnector);
        r
    };

    let response_write = flow_write_stream();

    // Once the underlying connector has finished writing and has EOFd, then we don't need to wait anymore
    // for any more writes before we check the status code and exit. This channel allows us to make sure the underlying
    // connector has finished writing so we can exit gracefully and on time.
    let (response_finished_sender, response_finished_receiver) = oneshot::channel::<bool>();
    let streaming_all_task = streaming_all(
        adapted_request_stream,
        child_stdin,
        Box::pin(monitored_response_stream),
        response_write.clone(),
        response_finished_sender,
    );

    let op_ref = &op;
    let child_arc = &Arc::new(Mutex::new(child));
    let exit_status_task = async move {
        let c = Arc::clone(child_arc);

        let exit_status_result = check_exit_status(c.lock().await.wait().await);

        // There are some Airbyte connectors that write records, and exit successfully, without ever writing
        // a state (checkpoint). In those cases, we want to provide a default empty checkpoint. It's important that
        // this only happens if the connector exit successfully, otherwise we risk double-writing data.
        if exit_status_result.is_ok() && *op_ref == Operation::Capture {
            tracing::debug!("atf: waiting for tp_receiver");
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
                    }),
                });
                let mut encoded_response = serde_json::to_vec(&response)?;
                encoded_response.push(NEWLINE);
                let mut buf = &encoded_response[..];
                let mut writer = response_write.lock().await;
                copy(&mut buf, writer.deref_mut()).await?;
            }
        }

        if exit_status_result.is_ok() {
            // We give a timeout of 5 seconds to let any remaining writes to be done
            return tokio::select! {
                Ok(true) = response_finished_receiver => exit_status_result,
                _ = tokio::time::sleep(tokio::time::Duration::from_secs(5)) => exit_status_result
            };
        }

        exit_status_result
    };

    let start_time = Instant::now();

    // Some airbyte connectors are known for exhausting rate-limits of customers
    // So we allow connectors to be configured with a run_interval_minutes.json file
    // which specifies how frequently should the connector run
    let run_interval = async move {
        if *op_ref != Operation::Capture {
            return Ok(());
        };

        if let Some(Ok(cfg)) = config {
            if cfg.pointer("/_atf_skip_interval") == Some(&serde_json::Value::Bool(true)) {
                tracing::info!("atf: skipping interval");
                return Ok(());
            }
        }

        let run_interval_minutes = std::fs::read_to_string(RUN_INTERVAL_FILE_NAME)
            .ok()
            .map(|f| f.parse::<u64>())
            .transpose()?;

        // Make sure the process stays up for at least run_interval_minutes
        if let Some(interval_minutes) = run_interval_minutes {
            let elapsed = Instant::now().duration_since(start_time);
            let total_duration = tokio::time::Duration::from_secs(60 * interval_minutes);
            let remainder = total_duration.saturating_sub(elapsed);
            tracing::debug!("atf: sleeping for {remainder:?}");
            tokio::time::sleep(remainder).await;
        }

        let r: Result<(), Error> = Ok(());
        r
    };

    // If streaming_all_task errors out, we error out and don't wait for exit_status, on the other
    // hand once the connector has exit (exit_status_task completes), we don't wait for streaming
    // task anymore
    tokio::select! {
        Err(e) = streaming_all_task => Err(e),
        resp = exit_status_task => resp,
        // In case of a ping timeout, we do not report an error,
        // just exit and let the connector restart, since an idle connector
        // is not always an error.
        //
        // once a select branch resolves, other branches are cancelled, that's why we assume here
        // that the lock by `exit_status_task` is released and so we can obtain the lock here
        Err(_) = ping_timeout_task => {
            tracing::debug!("atf: killing child process");
            Arc::clone(child_arc).lock().await.kill().await?;
            Ok(())
        }
    }?;

    run_interval.await?;

    tracing::debug!("atf: connector_runner done");
    Ok(())
}

/// Stream request_stream into request_stream_writer and response_stream into
/// response_stream_writer.
async fn streaming_all(
    request_stream: InterceptorStream,
    mut request_stream_writer: ChildStdin,
    mut response_stream: InterceptorStream,
    response_stream_writer: Arc<Mutex<Pin<Box<dyn AsyncWrite + Sync + Send>>>>,
    response_finished_sender: oneshot::Sender<bool>,
) -> Result<(), Error> {
    let mut request_stream_reader = StreamReader::new(request_stream);

    let request_stream_copy = async move {
        copy(&mut request_stream_reader, &mut request_stream_writer).await?;
        tracing::debug!("atf: request_stream_copy done");
        Ok::<(), std::io::Error>(())
    };

    let response_stream_copy = async move {
        let mut writer = response_stream_writer.lock().await;

        while let Some(result) = response_stream.next().await {
            match result {
                Ok(bytes) => {
                    writer.write_all(&bytes).await?;
                }
                // This error usually happens because there is an underlying error
                // in the connector. We don't want this error to obscure the real error
                // so we just log it as a debug and let the last output error
                // to take precedence
                Err(e @ Error::EmptyStream) => {
                    tracing::debug!("{}", e.to_string());
                }
                Err(e) => Err::<(), std::io::Error>(e.into())?,
            }
        }
        writer.flush().await?;

        response_finished_sender
            .send(true)
            .expect("send write finished signal twice");
        tracing::debug!("atf: response_stream_copy done");
        Ok(())
    };

    tokio::try_join!(request_stream_copy, response_stream_copy)?;

    tracing::debug!("atf: streaming_all finished");
    Ok(())
}
