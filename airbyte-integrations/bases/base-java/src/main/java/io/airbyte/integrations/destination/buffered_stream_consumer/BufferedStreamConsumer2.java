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
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

// Strategy:
// phase: start
// 1. onStart initialize a disk-backed queue for each stream.
// 2. execute any user provided onStart code (anything that needs to be run before any records are
// accepted).
// 3. launch an executor pool that polls the queues and attempt to write data from that queue to the
// destination using user-provided recordWriter.
// phase: accepting records (this phase begins after start has completed)
// 4. begin accepting records. immediately write them to the on-disk queue. each accept call does
// NOT directly try to right records to the destination.
// note: the background thread will be writing records to the destination in batch during this
// phase.
// phase: close (this phase begins after all records have been accepted)
// 5. terminate background thread gracefully.
// 6. flush all remaining records in the on-disk queues to the destination using user-provided
// recordWriter.
// 7. execute user-provided onClose code.

public class BufferedStreamConsumer2 extends FailureTrackingAirbyteMessageConsumer {

  private static final Logger LOGGER = LoggerFactory.getLogger(BufferedStreamConsumer2.class);
  private static final long THREAD_DELAY_MILLIS = 500L;

  private static final long GRACEFUL_SHUTDOWN_MINUTES = 5L;
  private static final int MIN_RECORDS = 500;
  private static final int BATCH_SIZE = 10000;

  private final VoidCallable onStart;
  private final RecordWriter recordWriter;
  private final CheckedConsumer<Boolean, Exception> onClose;
  private final Set<AirbyteStreamNameNamespacePair> pairs;
  private final BlockingQueue<AirbyteMessage> queue;
  private final ConfiguredAirbyteCatalog catalog;
  private final CheckedFunction<String, Boolean, Exception> isValidRecord;
  private final Map<AirbyteStreamNameNamespacePair, Long> pairToIgnoredRecordCount;

  private boolean hasStarted;

  private AirbyteStreamNameNamespacePair lastRecordStream;

  public BufferedStreamConsumer2(VoidCallable onStart,
                                 RecordWriter recordWriter,
                                 CheckedConsumer<Boolean, Exception> onClose,
                                 ConfiguredAirbyteCatalog catalog,
                                 Set<AirbyteStreamNameNamespacePair> pairs,
                                 CheckedFunction<String, Boolean, Exception> isValidRecord) {
    this.hasStarted = false;
    this.onStart = onStart;
    this.recordWriter = recordWriter;
    this.onClose = onClose;
    this.catalog = catalog;
    this.pairs = pairs;
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
    LOGGER.info("{} started.", BufferedStreamConsumer2.class);

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

      // need to know if it is the last reocrd? yes. we need to know when the stream neds..... before that
      // was handled externally. either we:
      // 1. continue to handle it externally and have a final clean up writ elike we used. which is fine.
      // 2. send an eof message in the queue.

      if (lastRecordStream != null && lastRecordStream.equals(stream)) {
        final ArrayList<AirbyteMessage> queueContents = new ArrayList<>();
        queue.drainTo(queueContents);
        final Map<Type, List<AirbyteMessage>> recordsByType = queueContents
            .stream()
            .collect(Collectors.groupingBy(AirbyteMessage::getType));
        recordWriter.accept(stream, recordsByType.get(Type.RECORD).stream().map(AirbyteMessage::getRecord).collect(Collectors.toList()));

        // handle state.
      }

      lastRecordStream = stream;
    }

    if (!queue.offer(message, 5, TimeUnit.HOURS)) {
      throw new IllegalStateException("Could not accept record despite waiting.");
    }
  }

  private void throwUnrecognizedStream(final ConfiguredAirbyteCatalog catalog, final AirbyteMessage message) {
    throw new IllegalArgumentException(
        String.format("Message contained record from a stream that was not in the catalog. \ncatalog: %s , \nmessage: %s",
            Jsons.serialize(catalog), Jsons.serialize(message)));
  }

  @SuppressWarnings("ResultOfMethodCallIgnored")
  @Override
  protected void close(boolean hasFailed) throws Exception {
    pairToIgnoredRecordCount
        .forEach((pair, count) -> LOGGER.warn("A total of {} record(s) of data from stream {} were invalid and were ignored.", count, pair));
    if (hasFailed) {
      LOGGER.error("executing on failed close procedure.");

      // kill executor pool fast.
      // writerPool.shutdown();
      // writerPool.awaitTermination(1, TimeUnit.SECONDS);
    } else {
      LOGGER.info("executing on success close procedure.");

      // shutdown executor pool with time to complete writes.
      // writerPool.shutdown();
      // writerPool.awaitTermination(GRACEFUL_SHUTDOWN_MINUTES, TimeUnit.MINUTES);

      // write anything that is left in the buffers.
      // writeStreamsWithNRecords(0, pairToWriteBuffer, recordWriter);
    }

    onClose.accept(hasFailed);

    // for (CloseableQueue<byte[]> writeBuffer : pairToWriteBuffer.values()) {
    // writeBuffer.close();
    // }
  }

  // private static void writeStreamsWithNRecords(int minRecords,
  // Map<AirbyteStreamNameNamespacePair, CloseableQueue<byte[]>> pairToWriteBuffers,
  // RecordWriter recordWriter) {
  // for (final AirbyteStreamNameNamespacePair pair : pairToWriteBuffers.keySet()) {
  // final CloseableQueue<byte[]> writeBuffer = pairToWriteBuffers.get(pair);
  // while (writeBuffer.size() > minRecords) {
  // try {
  // final List<AirbyteRecordMessage> records = Queues.toStream(writeBuffer)
  // .limit(BufferedStreamConsumer2.BATCH_SIZE)
  // .map(record -> Jsons.deserialize(new String(record, Charsets.UTF_8), AirbyteRecordMessage.class))
  // .collect(Collectors.toList());
  //
  // LOGGER.info("Writing stream {}. Max batch size: {}, Actual batch size: {}, Remaining buffered
  // records: {}",
  // pair, BufferedStreamConsumer2.BATCH_SIZE, records.size(), writeBuffer.size());
  // recordWriter.accept(pair, records.stream());
  // } catch (Exception e) {
  // throw new RuntimeException(e);
  // }
  // }
  // }
  // }

}
