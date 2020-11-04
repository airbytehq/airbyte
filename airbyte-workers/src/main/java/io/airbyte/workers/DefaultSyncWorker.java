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
import io.airbyte.config.StandardTapConfig;
import io.airbyte.config.StandardTargetConfig;
import io.airbyte.config.State;
import io.airbyte.workers.normalization.NormalizationRunner;
import io.airbyte.workers.protocols.Destination;
import io.airbyte.workers.protocols.MessageTracker;
import io.airbyte.workers.protocols.Source;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicBoolean;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DefaultSyncWorker<T> implements SyncWorker {

  private static final Logger LOGGER = LoggerFactory.getLogger(DefaultSyncWorker.class);

  private final Source<T> source;
  private final Destination<T> destination;
  private final MessageTracker<T> messageTracker;
  private final NormalizationRunner normalizationRunner;

  private final AtomicBoolean cancelled;

  public DefaultSyncWorker(final Source<T> source,
                           final Destination<T> destination,
                           final MessageTracker<T> messageTracker,
                           final NormalizationRunner normalizationRunner) {
    this.source = source;
    this.destination = destination;
    this.messageTracker = messageTracker;
    this.normalizationRunner = normalizationRunner;

    this.cancelled = new AtomicBoolean(false);
  }

  @Override
  public OutputAndStatus<StandardSyncOutput> run(StandardSyncInput syncInput, Path jobRoot) {
    long startTime = System.currentTimeMillis();

    final StandardTapConfig tapConfig = WorkerUtils.syncToTapConfig(syncInput);
    final StandardTargetConfig targetConfig = WorkerUtils.syncToTargetConfig(syncInput);

    try (destination; source) {

      destination.start(targetConfig, jobRoot);
      source.start(tapConfig, jobRoot);

      while (!cancelled.get() && !source.isFinished()) {
        final Optional<T> maybeMessage = source.attemptRead();
        if (maybeMessage.isPresent()) {
          final T message = maybeMessage.get();
          messageTracker.accept(message);
          destination.accept(message);
        }
      }

      destination.notifyEndOfStream();

      try (normalizationRunner) {
        LOGGER.info("Running normalization.");
        normalizationRunner.start();
        final Path normalizationRoot = Files.createDirectories(jobRoot.resolve("normalize"));
        if (!normalizationRunner.normalize(normalizationRoot, syncInput.getDestinationConnection().getConfiguration(), syncInput.getCatalog())) {
          throw new WorkerException("Normalization Failed.");
        }
      }
    } catch (Exception e) {
      LOGGER.error("Sync worker failed.", e);

      return new OutputAndStatus<>(JobStatus.FAILED, null);
    }

    StandardSyncSummary summary = new StandardSyncSummary()
        .withRecordsSynced(messageTracker.getRecordCount())
        .withStartTime(startTime)
        .withEndTime(System.currentTimeMillis());

    final StandardSyncOutput output = new StandardSyncOutput().withStandardSyncSummary(summary);
    messageTracker.getOutputState().ifPresent(capturedState -> {
      final State state = new State()
          .withConnectionId(tapConfig.getConnectionId())
          .withState(capturedState);
      output.withState(state);
    });

    return new OutputAndStatus<>(cancelled.get() ? JobStatus.FAILED : JobStatus.SUCCEEDED, output);
  }

  @Override
  public void cancel() {
    cancelled.set(true);
  }

}
