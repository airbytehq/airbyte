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

package io.airbyte.integrations.destination.buffered_stream_consumer;

import com.google.common.annotations.VisibleForTesting;
import com.google.common.base.Preconditions;
import io.airbyte.commons.concurrency.VoidCallable;
import io.airbyte.commons.functional.CheckedConsumer;
import io.airbyte.commons.functional.CheckedFunction;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
import io.airbyte.integrations.base.FailureTrackingAirbyteMessageConsumer;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.TimeUnit;
import java.util.function.Consumer;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class BufferedStreamConsumer extends FailureTrackingAirbyteMessageConsumer {

  private static final Logger LOGGER = LoggerFactory.getLogger(BufferedStreamConsumer.class);
  private static final int BATCH_SIZE = 10000;

  private final VoidCallable onStart;
  private final RecordWriter recordWriter;
  private final CheckedConsumer<Boolean, Exception> onClose;
  private final Set<AirbyteStreamNameNamespacePair> pairs;
  private final BlockingQueue<AirbyteMessage> queue;
  private final ConfiguredAirbyteCatalog catalog;
  private final CheckedFunction<String, Boolean, Exception> isValidRecord;
  private final Map<AirbyteStreamNameNamespacePair, Long> pairToIgnoredRecordCount;
  private final Consumer<AirbyteStateMessage> checkpointConsumer;

  private boolean hasStarted;
  private boolean hasClosed;

  private AirbyteStreamNameNamespacePair lastRecordStream;
  private AirbyteStateMessage lastCommittedState;
  private AirbyteStateMessage pendingState;

  public BufferedStreamConsumer(VoidCallable onStart,
                                RecordWriter recordWriter,
                                CheckedConsumer<Boolean, Exception> onClose,
                                ConfiguredAirbyteCatalog catalog,
                                CheckedFunction<String, Boolean, Exception> isValidRecord) {
    this(onStart, recordWriter, onClose, catalog, isValidRecord, (stateMessage) -> {});
  }

  // todo (cgardens) checkpointConsumer will become relevant once we start actually checkpointing.
  @VisibleForTesting
  BufferedStreamConsumer(VoidCallable onStart,
                         RecordWriter recordWriter,
                         CheckedConsumer<Boolean, Exception> onClose,
                         ConfiguredAirbyteCatalog catalog,
                         CheckedFunction<String, Boolean, Exception> isValidRecord,
                         Consumer<AirbyteStateMessage> checkpointConsumer) {
    this.checkpointConsumer = checkpointConsumer;
    this.hasStarted = false;
    this.hasClosed = false;
    this.onStart = onStart;
    this.recordWriter = recordWriter;
    this.onClose = onClose;
    this.catalog = catalog;
    this.pairs = AirbyteStreamNameNamespacePair.fromConfiguredCatalog(catalog);
    this.isValidRecord = isValidRecord;
    this.queue = new ArrayBlockingQueue<>(BATCH_SIZE);

    this.pairToIgnoredRecordCount = new HashMap<>();
  }

  @Override
  protected void startTracked() throws Exception {
    // todo (cgardens) - if we reuse this pattern, consider moving it into FailureTrackingConsumer.
    Preconditions.checkState(!hasStarted, "Consumer has already been started.");
    hasStarted = true;

    pairToIgnoredRecordCount.clear();
    LOGGER.info("{} started.", BufferedStreamConsumer.class);

    onStart.call();
  }

  @Override
  protected void acceptTracked(AirbyteMessage message) throws Exception {
    Preconditions.checkState(hasStarted, "Cannot accept records until consumer has started");

    if (message.getType() == Type.RECORD) {
      final AirbyteRecordMessage recordMessage = message.getRecord();
      final AirbyteStreamNameNamespacePair stream = AirbyteStreamNameNamespacePair.fromRecordMessage(recordMessage);
      final String data = Jsons.serialize(message);

      if (!pairs.contains(stream)) {
        throwUnrecognizedStream(catalog, message);
      }

      if (!isValidRecord.apply(data)) {
        pairToIgnoredRecordCount.put(stream, pairToIgnoredRecordCount.getOrDefault(stream, 0L) + 1L);
        return;
      }

      if (lastRecordStream != null && !lastRecordStream.equals(stream)) {
        flushQueueToDestination();
        // handle state.
      }

      lastRecordStream = stream;
    } else if (message.getType() == Type.STATE) {
      pendingState = message.getState();
    } else {
      LOGGER.warn("Unexpected message: " + message.getType());
    }

    // only put records in here.
    if (!queue.offer(message, 5, TimeUnit.HOURS)) {
      throw new IllegalStateException("Could not accept record despite waiting.");
    }
  }

  private void flushQueueToDestination() throws Exception {
    final List<AirbyteMessage> queueContents = new ArrayList<>();
    queue.drainTo(queueContents);
    final Map<Type, List<AirbyteMessage>> recordsByType = queueContents
        .stream()
        .collect(Collectors.groupingBy(AirbyteMessage::getType));

    final List<AirbyteRecordMessage> records = recordsByType.getOrDefault(Type.RECORD, new ArrayList<>())
        .stream()
        .map(AirbyteMessage::getRecord)
        .collect(Collectors.toList());
    recordWriter.accept(lastRecordStream, records);
    if (pendingState != null) {
      lastCommittedState = pendingState;
      pendingState = null;
      checkpointConsumer.accept(lastCommittedState);
    }
  }

  private void throwUnrecognizedStream(final ConfiguredAirbyteCatalog catalog, final AirbyteMessage message) {
    throw new IllegalArgumentException(
        String.format("Message contained record from a stream that was not in the catalog. \ncatalog: %s , \nmessage: %s",
            Jsons.serialize(catalog), Jsons.serialize(message)));
  }

  @Override
  protected void close(boolean hasFailed) throws Exception {
    Preconditions.checkState(hasStarted, "Cannot close; has not started.");
    Preconditions.checkState(!hasClosed, "Has already closed.");
    hasClosed = true;

    pairToIgnoredRecordCount
        .forEach((pair, count) -> LOGGER.warn("A total of {} record(s) of data from stream {} were invalid and were ignored.", count, pair));
    if (hasFailed) {
      LOGGER.error("executing on failed close procedure.");
    } else {
      LOGGER.info("executing on success close procedure.");
      flushQueueToDestination();
    }

    onClose.accept(hasFailed);
  }

}
