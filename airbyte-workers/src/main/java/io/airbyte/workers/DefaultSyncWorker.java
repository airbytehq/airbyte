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
import io.airbyte.workers.normalization.NormalizationRunner;
import io.airbyte.workers.protocols.Destination;
import io.airbyte.workers.protocols.Mapper;
import io.airbyte.workers.protocols.MessageTracker;
import io.airbyte.workers.protocols.Source;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DefaultSyncWorker implements SyncWorker {

  private static final Logger LOGGER = LoggerFactory.getLogger(DefaultSyncWorker.class);

  private final String jobId;
  private final int attempt;
  private final Source<AirbyteMessage> source;
  private final Mapper<AirbyteMessage> mapper;
  private final Destination<AirbyteMessage> destination;
  private final MessageTracker<AirbyteMessage> messageTracker;
  private final NormalizationRunner normalizationRunner;

  private final AtomicBoolean cancelled;

  public DefaultSyncWorker(
                           final String jobId,
                           final int attempt,
                           final Source<AirbyteMessage> source,
                           final Mapper<AirbyteMessage> mapper,
                           final Destination<AirbyteMessage> destination,
                           final MessageTracker<AirbyteMessage> messageTracker,
                           final NormalizationRunner normalizationRunner) {
    this.jobId = jobId;
    this.attempt = attempt;
    this.source = source;
    this.mapper = mapper;
    this.destination = destination;
    this.messageTracker = messageTracker;
    this.normalizationRunner = normalizationRunner;

    this.cancelled = new AtomicBoolean(false);
  }

  @Override
  public StandardSyncOutput run(StandardSyncInput syncInput, Path jobRoot) throws WorkerException {
    long startTime = System.currentTimeMillis();

    LOGGER.info("configured sync modes: {}", syncInput.getCatalog().getStreams()
        .stream()
        .collect(Collectors.toMap(s -> s.getStream().getName(), s -> String.format("%s - %s", s.getSyncMode(), s.getDestinationSyncMode()))));
    final StandardTapConfig tapConfig = WorkerUtils.syncToTapConfig(syncInput);
    final StandardTargetConfig targetConfig = WorkerUtils.syncToTargetConfig(syncInput);
    targetConfig.setCatalog(mapper.mapCatalog(targetConfig.getCatalog()));

    try (destination; source) {
      destination.start(targetConfig, jobRoot);
      source.start(tapConfig, jobRoot);

      while (!cancelled.get() && !source.isFinished()) {
        final Optional<AirbyteMessage> maybeMessage = source.attemptRead();
        if (maybeMessage.isPresent()) {
          final AirbyteMessage message = mapper.mapMessage(maybeMessage.get());

          messageTracker.accept(message);
          destination.accept(message);
        }
      }

    } catch (Exception e) {
      throw new WorkerException("Sync worker failed.", e);
    }

    try (normalizationRunner) {
      LOGGER.info("Running normalization.");
      normalizationRunner.start();
      final Path normalizationRoot = Files.createDirectories(jobRoot.resolve("normalize"));
      if (!normalizationRunner.normalize(jobId, attempt, normalizationRoot, syncInput.getDestinationConfiguration(), targetConfig.getCatalog())) {
        throw new WorkerException("Normalization Failed.");
      }
    } catch (Exception e) {
      throw new WorkerException("Normalization Failed.", e);
    }

    final StandardSyncSummary summary = new StandardSyncSummary()
        .withStatus(cancelled.get() ? Status.FAILED : Status.COMPLETED)
        .withRecordsSynced(messageTracker.getRecordCount())
        .withBytesSynced(messageTracker.getBytesCount())
        .withStartTime(startTime)
        .withEndTime(System.currentTimeMillis());

    LOGGER.info("sync summary: {}", summary);

    if (cancelled.get()) {
      throw new WorkerException("Sync was cancelled.");
    }

    final StandardSyncOutput output = new StandardSyncOutput().withStandardSyncSummary(summary);
    messageTracker.getOutputState().ifPresent(capturedState -> {
      final State state = new State()
          .withState(capturedState);
      output.withState(state);
    });

    return output;
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

    LOGGER.info("Cancelling normalization runner...");
    try {
      normalizationRunner.close();
    } catch (Exception e) {
      e.printStackTrace();
    }
  }

}
