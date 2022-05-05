/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers;

import io.airbyte.config.FailureReason;
import io.airbyte.config.ReplicationAttemptSummary;
import io.airbyte.config.ReplicationOutput;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.config.StandardSyncSummary.ReplicationStatus;
import io.airbyte.config.State;
import io.airbyte.config.StreamSyncStats;
import io.airbyte.config.SyncStats;
import io.airbyte.config.WorkerDestinationConfig;
import io.airbyte.config.WorkerSourceConfig;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.workers.helper.FailureHelper;
import io.airbyte.workers.protocols.airbyte.AirbyteDestination;
import io.airbyte.workers.protocols.airbyte.AirbyteMapper;
import io.airbyte.workers.protocols.airbyte.AirbyteSource;
import io.airbyte.workers.protocols.airbyte.MessageTracker;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicReference;
import java.util.stream.Collectors;
import org.apache.commons.io.FileUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.slf4j.MDC;

/**
 * This worker is the "data shovel" of ETL. It is responsible for moving data from the Source
 * container to the Destination container. It manages the full lifecycle of this process. This
 * includes:
 * <ul>
 * <li>Starting the Source and Destination containers</li>
 * <li>Passing data from Source to Destination</li>
 * <li>Executing any configured map-only operations (Mappers) in between the Source and
 * Destination</li>
 * <li>Collecting metadata about the data that is passing from Source to Destination</li>
 * <li>Listening for state messages emitted from the Destination to keep track of what data has been
 * replicated.</li>
 * <li>Handling shutdown of the Source and Destination</li>
 * <li>Handling failure cases and returning state for partially completed replications (so that the
 * next replication can pick up where it left off instead of starting from the beginning)</li>
 * </ul>
 */
public class DefaultReplicationWorker implements ReplicationWorker {

  private static final Logger LOGGER = LoggerFactory.getLogger(DefaultReplicationWorker.class);

  private final String jobId;
  private final int attempt;
  private final AirbyteSource source;
  private final AirbyteMapper mapper;
  private final AirbyteDestination destination;
  private final MessageTracker messageTracker;

  private final ExecutorService executors;
  private final AtomicBoolean cancelled;
  private final AtomicBoolean hasFailed;

  public DefaultReplicationWorker(final String jobId,
                                  final int attempt,
                                  final AirbyteSource source,
                                  final AirbyteMapper mapper,
                                  final AirbyteDestination destination,
                                  final MessageTracker messageTracker) {
    this.jobId = jobId;
    this.attempt = attempt;
    this.source = source;
    this.mapper = mapper;
    this.destination = destination;
    this.messageTracker = messageTracker;
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
  public ReplicationOutput run(final StandardSyncInput syncInput, final Path jobRoot) throws WorkerException {
    LOGGER.info("start sync worker. job id: {} attempt id: {}", jobId, attempt);

    // todo (cgardens) - this should not be happening in the worker. this is configuration information
    // that is independent of workflow executions.
    final WorkerDestinationConfig destinationConfig = WorkerUtils.syncToWorkerDestinationConfig(syncInput);
    destinationConfig.setCatalog(mapper.mapCatalog(destinationConfig.getCatalog()));

    final long startTime = System.currentTimeMillis();
    final AtomicReference<FailureReason> replicationRunnableFailureRef = new AtomicReference<>();
    final AtomicReference<FailureReason> destinationRunnableFailureRef = new AtomicReference<>();

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

        // note: `whenComplete` is used instead of `exceptionally` so that the original exception is still
        // thrown
        final CompletableFuture<?> destinationOutputThreadFuture = CompletableFuture.runAsync(
            getDestinationOutputRunnable(destination, cancelled, messageTracker, mdc),
            executors).whenComplete((msg, ex) -> {
              if (ex != null) {
                if (ex.getCause() instanceof DestinationException) {
                  destinationRunnableFailureRef.set(FailureHelper.destinationFailure(ex, Long.valueOf(jobId), attempt));
                } else {
                  destinationRunnableFailureRef.set(FailureHelper.replicationFailure(ex, Long.valueOf(jobId), attempt));
                }
              }
            });

        final CompletableFuture<?> replicationThreadFuture = CompletableFuture.runAsync(
            getReplicationRunnable(source, destination, cancelled, mapper, messageTracker, mdc),
            executors).whenComplete((msg, ex) -> {
              if (ex != null) {
                if (ex.getCause() instanceof SourceException) {
                  replicationRunnableFailureRef.set(FailureHelper.sourceFailure(ex, Long.valueOf(jobId), attempt));
                } else if (ex.getCause() instanceof DestinationException) {
                  replicationRunnableFailureRef.set(FailureHelper.destinationFailure(ex, Long.valueOf(jobId), attempt));
                } else {
                  replicationRunnableFailureRef.set(FailureHelper.replicationFailure(ex, Long.valueOf(jobId), attempt));
                }
              }
            });

        LOGGER.info("Waiting for source and destination threads to complete.");
        // CompletableFuture#allOf waits until all futures finish before returning, even if one throws an
        // exception. So in order to handle exceptions from a future immediately without needing to wait for
        // the other future to finish, we first call CompletableFuture#anyOf.
        CompletableFuture.anyOf(replicationThreadFuture, destinationOutputThreadFuture).get();
        LOGGER.info("One of source or destination thread complete. Waiting on the other.");
        CompletableFuture.allOf(replicationThreadFuture, destinationOutputThreadFuture).get();
        LOGGER.info("Source and destination threads complete.");

      } catch (final Exception e) {
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

      final SyncStats totalSyncStats = new SyncStats()
          .withRecordsEmitted(messageTracker.getTotalRecordsEmitted())
          .withBytesEmitted(messageTracker.getTotalBytesEmitted())
          .withStateMessagesEmitted(messageTracker.getTotalStateMessagesEmitted());

      if (outputStatus == ReplicationStatus.COMPLETED) {
        totalSyncStats.setRecordsCommitted(totalSyncStats.getRecordsEmitted());
      } else if (messageTracker.getTotalRecordsCommitted().isPresent()) {
        totalSyncStats.setRecordsCommitted(messageTracker.getTotalRecordsCommitted().get());
      } else {
        LOGGER.warn("Could not reliably determine committed record counts, committed record stats will be set to null");
        totalSyncStats.setRecordsCommitted(null);
      }

      // assume every stream with stats is in streamToEmittedRecords map
      final List<StreamSyncStats> streamSyncStats = messageTracker.getStreamToEmittedRecords().keySet().stream().map(stream -> {
        final SyncStats syncStats = new SyncStats()
            .withRecordsEmitted(messageTracker.getStreamToEmittedRecords().get(stream))
            .withBytesEmitted(messageTracker.getStreamToEmittedBytes().get(stream))
            .withStateMessagesEmitted(null); // TODO (parker) populate per-stream state messages emitted once supported in V2

        if (outputStatus == ReplicationStatus.COMPLETED) {
          syncStats.setRecordsCommitted(messageTracker.getStreamToEmittedRecords().get(stream));
        } else if (messageTracker.getStreamToCommittedRecords().isPresent()) {
          syncStats.setRecordsCommitted(messageTracker.getStreamToCommittedRecords().get().get(stream));
        } else {
          syncStats.setRecordsCommitted(null);
        }
        return new StreamSyncStats()
            .withStreamName(stream)
            .withStats(syncStats);
      }).collect(Collectors.toList());

      final ReplicationAttemptSummary summary = new ReplicationAttemptSummary()
          .withStatus(outputStatus)
          .withRecordsSynced(messageTracker.getTotalRecordsEmitted()) // TODO (parker) remove in favor of totalRecordsEmitted
          .withBytesSynced(messageTracker.getTotalBytesEmitted()) // TODO (parker) remove in favor of totalBytesEmitted
          .withTotalStats(totalSyncStats)
          .withStreamStats(streamSyncStats)
          .withStartTime(startTime)
          .withEndTime(System.currentTimeMillis());

      LOGGER.info("sync summary: {}", summary);
      final ReplicationOutput output = new ReplicationOutput()
          .withReplicationAttemptSummary(summary)
          .withOutputCatalog(destinationConfig.getCatalog());

      // only .setFailures() if a failure occurred
      final FailureReason sourceFailure = replicationRunnableFailureRef.get();
      final FailureReason destinationFailure = destinationRunnableFailureRef.get();
      final List<FailureReason> failures = new ArrayList<>();
      if (sourceFailure != null) {
        failures.add(sourceFailure);
      }
      if (destinationFailure != null) {
        failures.add(destinationFailure);
      }
      if (!failures.isEmpty()) {
        output.setFailures(failures);
      }

      if (messageTracker.getSourceOutputState().isPresent()) {
        LOGGER.info("Source output at least one state message");
      } else {
        LOGGER.info("Source did not output any state messages");
      }

      if (messageTracker.getDestinationOutputState().isPresent()) {
        LOGGER.info("State capture: Updated state to: {}", messageTracker.getDestinationOutputState());
        final State state = messageTracker.getDestinationOutputState().get();
        output.withState(state);
      } else if (syncInput.getState() != null) {
        LOGGER.warn("State capture: No new state, falling back on input state: {}", syncInput.getState());
        output.withState(syncInput.getState());
      } else {
        LOGGER.warn("State capture: No state retained.");
      }

      return output;
    } catch (final Exception e) {
      throw new WorkerException("Sync failed", e);
    }

  }

  private static Runnable getReplicationRunnable(final AirbyteSource source,
                                                 final AirbyteDestination destination,
                                                 final AtomicBoolean cancelled,
                                                 final AirbyteMapper mapper,
                                                 final MessageTracker messageTracker,
                                                 final Map<String, String> mdc) {
    return () -> {
      MDC.setContextMap(mdc);
      LOGGER.info("Replication thread started.");
      var recordsRead = 0;
      try {
        while (!cancelled.get() && !source.isFinished()) {
          final Optional<AirbyteMessage> messageOptional;
          try {
            messageOptional = source.attemptRead();
          } catch (final Exception e) {
            throw new SourceException("Source process read attempt failed", e);
          }
          if (messageOptional.isPresent()) {
            final AirbyteMessage message = mapper.mapMessage(messageOptional.get());

            messageTracker.acceptFromSource(message);
            try {
              destination.accept(message);
            } catch (final Exception e) {
              throw new DestinationException("Destination process message delivery failed", e);
            }
            recordsRead += 1;

            if (recordsRead % 1000 == 0) {
              LOGGER.info("Records read: {} ({})", recordsRead, FileUtils.byteCountToDisplaySize(messageTracker.getTotalBytesEmitted()));
            }
          } else {
            LOGGER.info("Source has no more messages, closing connection.");
            try {
              source.close();
            } catch (final Exception e) {
              throw new SourceException("Source cannot be stopped!", e);
            }
          }
        }
        LOGGER.info("Total records read: {} ({})", recordsRead, FileUtils.byteCountToDisplaySize(messageTracker.getTotalBytesEmitted()));
        try {
          destination.notifyEndOfStream();
        } catch (final Exception e) {
          throw new DestinationException("Destination process end of stream notification failed", e);
        }
        if (!cancelled.get() && source.getExitValue() != 0) {
          throw new SourceException("Source process exited with non-zero exit code " + source.getExitValue());
        }
      } catch (final Exception e) {
        if (!cancelled.get()) {
          // Although this thread is closed first, it races with the source's closure and can attempt one
          // final read after the source is closed before it's terminated.
          // This read will fail and throw an exception. Because of this, throw exceptions only if the worker
          // was not cancelled.

          if (e instanceof SourceException || e instanceof DestinationException) {
            // Surface Source and Destination exceptions directly so that they can be classified properly by the
            // worker
            throw e;
          } else {
            throw new RuntimeException(e);
          }
        }
      }
    };
  }

  private static Runnable getDestinationOutputRunnable(final AirbyteDestination destination,
                                                       final AtomicBoolean cancelled,
                                                       final MessageTracker messageTracker,
                                                       final Map<String, String> mdc) {
    return () -> {
      MDC.setContextMap(mdc);
      LOGGER.info("Destination output thread started.");
      try {
        while (!cancelled.get() && !destination.isFinished()) {
          final Optional<AirbyteMessage> messageOptional;
          try {
            messageOptional = destination.attemptRead();
          } catch (final Exception e) {
            throw new DestinationException("Destination process read attempt failed", e);
          }
          if (messageOptional.isPresent()) {
            LOGGER.info("State in DefaultReplicationWorker from destination: {}", messageOptional.get());
            messageTracker.acceptFromDestination(messageOptional.get());
          }
        }
        if (!cancelled.get() && destination.getExitValue() != 0) {
          throw new DestinationException("Destination process exited with non-zero exit code " + destination.getExitValue());
        }
      } catch (final Exception e) {
        if (!cancelled.get()) {
          // Although this thread is closed first, it races with the destination's closure and can attempt one
          // final read after the destination is closed before it's terminated.
          // This read will fail and throw an exception. Because of this, throw exceptions only if the worker
          // was not cancelled.

          if (e instanceof DestinationException) {
            // Surface Destination exceptions directly so that they can be classified properly by the worker
            throw e;
          } else {
            throw new RuntimeException(e);
          }
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
    } catch (final InterruptedException e) {
      e.printStackTrace();
    }
    cancelled.set(true);

    LOGGER.info("Cancelling destination...");
    try {
      destination.cancel();
    } catch (final Exception e) {
      LOGGER.info("Error cancelling destination: ", e);
    }

    LOGGER.info("Cancelling source...");
    try {
      source.cancel();
    } catch (final Exception e) {
      LOGGER.info("Error cancelling source: ", e);
    }

  }

  private static class SourceException extends RuntimeException {

    SourceException(final String message) {
      super(message);
    }

    SourceException(final String message, final Throwable cause) {
      super(message, cause);
    }

  }

  private static class DestinationException extends RuntimeException {

    DestinationException(final String message) {
      super(message);
    }

    DestinationException(final String message, final Throwable cause) {
      super(message, cause);
    }

  }

}
