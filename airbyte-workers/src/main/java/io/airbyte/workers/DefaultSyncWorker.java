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

import com.google.common.collect.Sets;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.config.StandardSyncOutput;
import io.airbyte.config.StandardSyncSummary;
import io.airbyte.config.StandardTapConfig;
import io.airbyte.config.StandardTargetConfig;
import io.airbyte.config.State;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.workers.protocols.Destination;
import io.airbyte.workers.protocols.MessageTracker;
import io.airbyte.workers.protocols.Source;
import java.nio.file.Path;
import java.util.HashSet;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DefaultSyncWorker implements SyncWorker {

  private static final Logger LOGGER = LoggerFactory.getLogger(DefaultSyncWorker.class);

  private final Source<AirbyteMessage> source;
  private final Destination<AirbyteMessage> destination;
  private final MessageTracker<AirbyteMessage> messageTracker;

  private final AtomicBoolean cancelled;

  public DefaultSyncWorker(final Source<AirbyteMessage> source,
                           final Destination<AirbyteMessage> destination,
                           final MessageTracker<AirbyteMessage> messageTracker) {
    this.source = source;
    this.destination = destination;
    this.messageTracker = messageTracker;

    this.cancelled = new AtomicBoolean(false);
  }

  @Override
  public OutputAndStatus<StandardSyncOutput> run(StandardSyncInput syncInput, Path jobRoot) {
    long startTime = System.currentTimeMillis();

    // clean catalog object
    removeInvalidStreams(syncInput.getCatalog());

    final StandardTapConfig tapConfig = WorkerUtils.syncToTapConfig(syncInput);
    final StandardTargetConfig targetConfig = WorkerUtils.syncToTargetConfig(syncInput);

    try (destination; source) {
      destination.start(targetConfig, jobRoot);
      source.start(tapConfig, jobRoot);

      while (!cancelled.get() && !source.isFinished()) {
        final Optional<AirbyteMessage> maybeMessage = source.attemptRead();
        if (maybeMessage.isPresent()) {
          final AirbyteMessage message = maybeMessage.get();

          if (message.getType().equals(AirbyteMessage.Type.RECORD) && !CatalogHelpers.isValidIdentifier(message.getRecord().getStream())) {
            LOGGER.error("Filtered out record for invalid stream: " + message.getRecord().getStream());
          } else {
            messageTracker.accept(message);
            destination.accept(message);
          }
        }
      }

      destination.notifyEndOfStream();
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

  private void removeInvalidStreams(ConfiguredAirbyteCatalog catalog) {
    final Set<String> invalidStreams = Sets.union(
        new HashSet<>(CatalogHelpers.getInvalidStreamNames(catalog)),
        CatalogHelpers.getInvalidFieldNames(catalog).keySet());

    final List<ConfiguredAirbyteStream> streams = catalog.getStreams().stream()
        .filter(stream -> !invalidStreams.contains(stream.getName()))
        .collect(Collectors.toList());

    catalog.setStreams(streams);
  }

}
