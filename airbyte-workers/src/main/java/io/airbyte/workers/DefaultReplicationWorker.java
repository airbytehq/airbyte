/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.workers;

import io.airbyte.config.ReplicationAttemptSummary;
import io.airbyte.config.ReplicationOutput;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.config.StandardSyncSummary.ReplicationStatus;
import io.airbyte.config.StandardTapConfig;
import io.airbyte.config.StandardTargetConfig;
import io.airbyte.config.State;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.workers.protocols.Destination;
import io.airbyte.workers.protocols.Mapper;
import io.airbyte.workers.protocols.MessageTracker;
import io.airbyte.workers.protocols.Source;
import java.nio.file.Path;
import java.util.Optional;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DefaultReplicationWorker implements ReplicationWorker {

  private static final Logger LOGGER = LoggerFactory.getLogger(DefaultReplicationWorker.class);

  private final String jobId;
  private final int attempt;
  private final Source<AirbyteMessage> source;
  private final Mapper<AirbyteMessage> mapper;
  private final Destination<AirbyteMessage> destination;
  private final MessageTracker<AirbyteMessage> sourceMessageTracker;
  private final MessageTracker<AirbyteMessage> destinationMessageTracker;

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

    this.cancelled = new AtomicBoolean(false);
    this.hasFailed = new AtomicBoolean(false);
  }

  @Override
  public ReplicationOutput run(StandardSyncInput syncInput, Path jobRoot) throws WorkerException {
    LOGGER.info("start sync worker. job id: {} attempt id: {}", jobId, attempt);

    // todo (cgardens) - this should not be happening in the worker. this is configuration information
    // that is independent of workflow executions.
    final StandardTargetConfig destinationConfig = WorkerUtils.syncToTargetConfig(syncInput);
    destinationConfig.setCatalog(mapper.mapCatalog(destinationConfig.getCatalog()));

    long startTime = System.currentTimeMillis();
    try {
      LOGGER.info("configured sync modes: {}", syncInput.getCatalog().getStreams()
          .stream()
          .collect(Collectors.toMap(s -> s.getStream().getNamespace() + "." + s.getStream().getName(),
              s -> String.format("%s - %s", s.getSyncMode(), s.getDestinationSyncMode()))));
      final StandardTapConfig sourceConfig = WorkerUtils.syncToTapConfig(syncInput);

      final ExecutorService executorService = Executors.newFixedThreadPool(2);

      // note: resources are closed in the opposite order in which they are declared. thus source will be
      // closed first (which is what we want).
      try (destination; source) {
        destination.start(destinationConfig, jobRoot);
        source.start(sourceConfig, jobRoot);

        final Future<?> destinationOutputThreadFuture = executorService.submit(getDestinationOutputRunnable(
            destination,
            cancelled,
            destinationMessageTracker));

        final Future<?> replicationThreadFuture = executorService.submit(getReplicationRunnable(
            source,
            destination,
            cancelled,
            mapper,
            sourceMessageTracker));

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
        executorService.shutdownNow();
      }

      final ReplicationStatus outputStatus;
      if (cancelled.get()) {
        outputStatus = ReplicationStatus.CANCELLED;
      } else if (hasFailed.get()) {
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
                                                 MessageTracker<AirbyteMessage> sourceMessageTracker) {
    return () -> {
      try {
        while (!cancelled.get() && !source.isFinished()) {
          final Optional<AirbyteMessage> messageOptional = source.attemptRead();
          if (messageOptional.isPresent()) {
            final AirbyteMessage message = mapper.mapMessage(messageOptional.get());

            LOGGER.info("record in DefaultReplicationWorker: {}", message);

            sourceMessageTracker.accept(message);
            destination.accept(message);
          }
        }
        destination.notifyEndOfStream();
      } catch (Exception e) {
        throw new RuntimeException(e);
      }
    };
  }

  private static Runnable getDestinationOutputRunnable(Destination<AirbyteMessage> destination,
                                                       AtomicBoolean cancelled,
                                                       MessageTracker<AirbyteMessage> destinationMessageTracker) {
    return () -> {
      try {
        while (!cancelled.get() && !destination.isFinished()) {
          final Optional<AirbyteMessage> messageOptional = destination.attemptRead();
          if (messageOptional.isPresent()) {
            LOGGER.info("state in DefaultReplicationWorker from Destination: {}", messageOptional.get());
            destinationMessageTracker.accept(messageOptional.get());
          }
        }
      } catch (Exception e) {
        throw new RuntimeException(e);
      }
    };
  }

  @Override
  public void cancel() {
    LOGGER.info("Cancelling replication worker...");
    cancelled.set(true);

    LOGGER.info("Cancelling source...");
    try {
      source.cancel();
    } catch (Exception e) {
      e.printStackTrace();
    }

    LOGGER.info("Cancelling destination...");
    try {
      destination.cancel();
    } catch (Exception e) {
      e.printStackTrace();
    }
  }

}
