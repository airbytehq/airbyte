/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers;

import io.airbyte.config.ReplicationAttemptSummary;
import io.airbyte.config.ReplicationOutput;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.config.StandardSyncSummary.ReplicationStatus;
import io.airbyte.config.State;
import io.airbyte.config.WorkerDestinationConfig;
import io.airbyte.config.WorkerSourceConfig;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.workers.protocols.Destination;
import io.airbyte.workers.protocols.Mapper;
import io.airbyte.workers.protocols.MessageTracker;
import io.airbyte.workers.protocols.Source;
import java.nio.file.Path;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.slf4j.MDC;

public class DefaultReplicationWorker implements ReplicationWorker {

  private static final Logger LOGGER = LoggerFactory.getLogger(DefaultReplicationWorker.class);

  private final String jobId;
  private final int attempt;
  private final Source<AirbyteMessage> source;
  private final Mapper<AirbyteMessage> mapper;
  private final Destination<AirbyteMessage> destination;
  private final MessageTracker<AirbyteMessage> sourceMessageTracker;
  private final MessageTracker<AirbyteMessage> destinationMessageTracker;

  private final ExecutorService executors;
  private final AtomicBoolean cancelled;
  private final AtomicBoolean hasFailed;

  public DefaultReplicationWorker(final String jobId,
                                  final int attempt,
                                  final Source<AirbyteMessage> source,
                                  final Mapper<AirbyteMessage> mapper,
                                  final Destination<AirbyteMessage> destination,
                                  final MessageTracker<AirbyteMessage> sourceMessageTracker,
                                  final MessageTracker<AirbyteMessage> destinationMessageTracker) {
    this.jobId = jobId;
    this.attempt = attempt;
    this.source = source;
    this.mapper = mapper;
    this.destination = destination;
    this.sourceMessageTracker = sourceMessageTracker;
    this.destinationMessageTracker = destinationMessageTracker;
    this.executors = Executors.newFixedThreadPool(2);

    this.cancelled = new AtomicBoolean(false);
    this.hasFailed = new AtomicBoolean(false);
  }

  /**
   * Run executes two threads. The first pipes data from STDOUT of the source to STDIN of the
   * destination. The second listen on STDOUT of the destination. The goal of this second thread is to
   * detect when the destination emits state messages. Only state messages emitted by the destination
   * should be treated as state that is safe to return from run. In the case when the destination
   * emits no state, we fall back on whatever state is pass in as an argument to this method.
   *
   * @param syncInput all configuration for running replication
   * @param jobRoot file root that worker is allowed to use
   * @return output of the replication attempt (including state)
   * @throws WorkerException
   */
  @Override
  public ReplicationOutput run(StandardSyncInput syncInput, Path jobRoot) throws WorkerException {
    LOGGER.info("start sync worker. job id: {} attempt id: {}", jobId, attempt);

    // todo (cgardens) - this should not be happening in the worker. this is configuration information
    // that is independent of workflow executions.
    final WorkerDestinationConfig destinationConfig = WorkerUtils.syncToWorkerDestinationConfig(syncInput);
    destinationConfig.setCatalog(mapper.mapCatalog(destinationConfig.getCatalog()));

    long startTime = System.currentTimeMillis();
    try {
      LOGGER.info("configured sync modes: {}", syncInput.getCatalog().getStreams()
          .stream()
          .collect(Collectors.toMap(s -> s.getStream().getNamespace() + "." + s.getStream().getName(),
              s -> String.format("%s - %s", s.getSyncMode(), s.getDestinationSyncMode()))));
      final WorkerSourceConfig sourceConfig = WorkerUtils.syncToWorkerSourceConfig(syncInput);

      final Map<String, String> mdc = MDC.getCopyOfContextMap();

      // note: resources are closed in the opposite order in which they are declared. thus source will be
      // closed first (which is what we want).
      try (destination; source) {
        destination.start(destinationConfig, jobRoot);
        source.start(sourceConfig, jobRoot);

        final Future<?> destinationOutputThreadFuture = executors.submit(getDestinationOutputRunnable(
            destination,
            cancelled,
            destinationMessageTracker,
            mdc));

        final Future<?> replicationThreadFuture = executors.submit(getReplicationRunnable(
            source,
            destination,
            cancelled,
            mapper,
            sourceMessageTracker,
            mdc));

        LOGGER.info("Waiting for source thread to join.");
        replicationThreadFuture.get();
        LOGGER.info("Source thread complete.");
        LOGGER.info("Waiting for destination thread to join.");
        destinationOutputThreadFuture.get();
        LOGGER.info("Destination thread complete.");

      } catch (Exception e) {
        hasFailed.set(true);
        LOGGER.error("Sync worker failed.", e);
      } finally {
        executors.shutdownNow();
      }

      final ReplicationStatus outputStatus;
      // First check if the process was cancelled. Cancellation takes precedence over failures.
      if (cancelled.get()) {
        outputStatus = ReplicationStatus.CANCELLED;
      }
      // if the process was not cancelled but still failed, then it's an actual failure
      else if (hasFailed.get()) {
        outputStatus = ReplicationStatus.FAILED;
      } else {
        outputStatus = ReplicationStatus.COMPLETED;
      }

      final ReplicationAttemptSummary summary = new ReplicationAttemptSummary()
          .withStatus(outputStatus)
          .withRecordsSynced(sourceMessageTracker.getRecordCount())
          .withBytesSynced(sourceMessageTracker.getBytesCount())
          .withStartTime(startTime)
          .withEndTime(System.currentTimeMillis());

      LOGGER.info("sync summary: {}", summary);

      final ReplicationOutput output = new ReplicationOutput()
          .withReplicationAttemptSummary(summary)
          .withOutputCatalog(destinationConfig.getCatalog());

      if (sourceMessageTracker.getOutputState().isPresent()) {
        LOGGER.info("Source output at least one state message");
      } else {
        LOGGER.info("Source did not output any state messages");
      }

      if (destinationMessageTracker.getOutputState().isPresent()) {
        LOGGER.info("State capture: Updated state to: {}", destinationMessageTracker.getOutputState());
        final State state = destinationMessageTracker.getOutputState().get();
        output.withState(state);
      } else if (syncInput.getState() != null) {
        LOGGER.warn("State capture: No new state, falling back on input state: {}", syncInput.getState());
        output.withState(syncInput.getState());
      } else {
        LOGGER.warn("State capture: No state retained.");
      }

      return output;
    } catch (Exception e) {
      throw new WorkerException("Sync failed", e);
    }

  }

  private static Runnable getReplicationRunnable(Source<AirbyteMessage> source,
                                                 Destination<AirbyteMessage> destination,
                                                 AtomicBoolean cancelled,
                                                 Mapper<AirbyteMessage> mapper,
                                                 MessageTracker<AirbyteMessage> sourceMessageTracker,
                                                 Map<String, String> mdc) {
    return () -> {
      MDC.setContextMap(mdc);
      LOGGER.info("Replication thread started.");
      var recordsRead = 0;
      try {
        while (!cancelled.get() && !source.isFinished()) {
          final Optional<AirbyteMessage> messageOptional = source.attemptRead();
          if (messageOptional.isPresent()) {
            final AirbyteMessage message = mapper.mapMessage(messageOptional.get());

            sourceMessageTracker.accept(message);
            destination.accept(message);
            recordsRead += 1;

            if (recordsRead % 1000 == 0) {
              LOGGER.info("Records read: {}", recordsRead);
            }
          }
        }
        destination.notifyEndOfStream();
      } catch (Exception e) {
        if (!cancelled.get()) {
          // Although this thread is closed first, it races with the source's closure and can attempt one
          // final read after the source is closed before it's terminated.
          // This read will fail and throw an exception. Because of this, throw exceptions only if the worker
          // was not cancelled.
          throw new RuntimeException(e);
        }
      }
    };
  }

  private static Runnable getDestinationOutputRunnable(Destination<AirbyteMessage> destination,
                                                       AtomicBoolean cancelled,
                                                       MessageTracker<AirbyteMessage> destinationMessageTracker,
                                                       Map<String, String> mdc) {
    return () -> {
      MDC.setContextMap(mdc);
      LOGGER.info("Destination output thread started.");
      try {
        while (!cancelled.get() && !destination.isFinished()) {
          final Optional<AirbyteMessage> messageOptional = destination.attemptRead();
          if (messageOptional.isPresent()) {
            LOGGER.info("state in DefaultReplicationWorker from Destination: {}", messageOptional.get());
            destinationMessageTracker.accept(messageOptional.get());
          }
        }
      } catch (Exception e) {
        if (!cancelled.get()) {
          // Although this thread is closed first, it races with the destination's closure and can attempt one
          // final read after the destination is closed before it's terminated.
          // This read will fail and throw an exception. Because of this, throw exceptions only if the worker
          // was not cancelled.
          throw new RuntimeException(e);
        }
      }
    };
  }

  @Override
  public void cancel() {
    // Resources are closed in the opposite order they are declared.
    LOGGER.info("Cancelling replication worker...");
    try {
      executors.awaitTermination(10, TimeUnit.SECONDS);
    } catch (InterruptedException e) {
      e.printStackTrace();
    }
    cancelled.set(true);

    LOGGER.info("Cancelling destination...");
    try {
      destination.cancel();
    } catch (Exception e) {
      LOGGER.info("Error cancelling destination: ", e);
    }

    LOGGER.info("Cancelling source...");
    try {
      source.cancel();
    } catch (Exception e) {
      LOGGER.info("Error cancelling source: ", e);
    }

  }

}
