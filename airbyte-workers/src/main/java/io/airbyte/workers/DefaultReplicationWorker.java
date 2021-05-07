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

import io.airbyte.config.StandardSyncInput;
import io.airbyte.config.StandardSyncOutput;
import io.airbyte.config.StandardSyncSummary;
import io.airbyte.config.StandardSyncSummary.Status;
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
  private final MessageTracker<AirbyteMessage> messageTracker;

  private final AtomicBoolean cancelled;

  public DefaultReplicationWorker(final String jobId,
                                  final int attempt,
                                  final Source<AirbyteMessage> source,
                                  final Mapper<AirbyteMessage> mapper,
                                  final Destination<AirbyteMessage> destination,
                                  final MessageTracker<AirbyteMessage> messageTracker) {
    this.jobId = jobId;
    this.attempt = attempt;
    this.source = source;
    this.mapper = mapper;
    this.destination = destination;
    this.messageTracker = messageTracker;

    this.cancelled = new AtomicBoolean(false);
  }

  @Override
  public StandardSyncOutput run(StandardSyncInput syncInput, Path jobRoot) throws WorkerException {
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

      // note: resources are closed in the opposite order in which they are declared. thus source will be
      // closed first (which is what we want).
      try (destination; source) {
        destination.start(destinationConfig, jobRoot);
        source.start(sourceConfig, jobRoot);

        while (!cancelled.get() && !source.isFinished()) {
          final Optional<AirbyteMessage> maybeMessage = source.attemptRead();
          if (maybeMessage.isPresent()) {
            final AirbyteMessage message = mapper.mapMessage(maybeMessage.get());

            messageTracker.accept(message);
            LOGGER.info("replication worker offer to destination: {}", message.getRecord().getData().get("column1").asText());
            destination.accept(message);
            LOGGER.info("replication worker offered to destination: {}", message.getRecord().getData().get("column1").asText());
            LOGGER.info("replication worker");
          }
        }
      }

      final StandardSyncSummary summary = new StandardSyncSummary()
          .withStatus(cancelled.get() ? Status.FAILED : Status.COMPLETED)
          .withRecordsSynced(messageTracker.getRecordCount())
          .withBytesSynced(messageTracker.getBytesCount())
          .withStartTime(startTime)
          .withEndTime(System.currentTimeMillis());

      LOGGER.info("sync summary: {}", summary);

      final StandardSyncOutput output = new StandardSyncOutput()
          .withStandardSyncSummary(summary)
          .withOutputCatalog(destinationConfig.getCatalog());

      messageTracker.getOutputState().ifPresent(capturedState -> {
        final State state = new State()
            .withState(capturedState);
        output.withState(state);
      });

      return output;
    } catch (Exception e) {
      throw new WorkerException("Sync failed", e);
    }

  }

  @Override
  public void cancel() {
    LOGGER.info("Cancelling sync worker...");
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
