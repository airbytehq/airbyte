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

import com.google.common.base.Charsets;
import com.google.common.base.Preconditions;
import io.airbyte.commons.concurrency.GracefulShutdownHandler;
import io.airbyte.commons.concurrency.VoidCallable;
import io.airbyte.commons.functional.CheckedBiConsumer;
import io.airbyte.commons.functional.CheckedConsumer;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.lang.CloseableQueue;
import io.airbyte.commons.lang.Queues;
import io.airbyte.integrations.base.FailureTrackingAirbyteMessageConsumer;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.queue.BigQueue;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Duration;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;
import java.util.stream.Stream;
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

public class BufferedStreamConsumer extends FailureTrackingAirbyteMessageConsumer {

  private static final Logger LOGGER = LoggerFactory.getLogger(BufferedStreamConsumer.class);
  private static final long THREAD_DELAY_MILLIS = 500L;

  private static final long GRACEFUL_SHUTDOWN_MINUTES = 5L;
  private static final int MIN_RECORDS = 500;
  private static final int BATCH_SIZE = 10000;

  private final VoidCallable onStart;
  private final CheckedBiConsumer<String, Stream<AirbyteRecordMessage>, Exception> recordWriter;
  private final CheckedConsumer<Boolean, Exception> onClose;
  private final Set<String> streamNames;
  private final Map<String, CloseableQueue<byte[]>> writeBuffers;
  private final ScheduledExecutorService writerPool;
  private final ConfiguredAirbyteCatalog catalog;

  private boolean hasStarted;

  public BufferedStreamConsumer(VoidCallable onStart,
                                CheckedBiConsumer<String, Stream<AirbyteRecordMessage>, Exception> recordWriter,
                                CheckedConsumer<Boolean, Exception> onClose,
                                ConfiguredAirbyteCatalog catalog,
                                Set<String> streamNames) {
    this.hasStarted = false;
    this.onStart = onStart;
    this.recordWriter = recordWriter;
    this.onClose = onClose;
    this.catalog = catalog;
    this.streamNames = streamNames;

    this.writerPool = Executors.newSingleThreadScheduledExecutor();
    Runtime.getRuntime().addShutdownHook(new GracefulShutdownHandler(Duration.ofMinutes(GRACEFUL_SHUTDOWN_MINUTES), writerPool));

    this.writeBuffers = new HashMap<>();
  }

  @Override
  protected void startTracked() throws Exception {
    // todo (cgardens) - if we reuse this pattern, consider moving it into FailureTrackingConsumer.
    Preconditions.checkState(!hasStarted, "Consumer has already been started.");
    hasStarted = true;

    LOGGER.info("{} started.", BufferedStreamConsumer.class);

    LOGGER.info("Buffer creation started for {} streams.", streamNames.size());
    final Path queueRoot = Files.createTempDirectory("queues");
    for (String streamName : streamNames) {
      LOGGER.info("Buffer creation for stream {}.", streamName);
      final BigQueue writeBuffer = new BigQueue(queueRoot.resolve(streamName), streamName);
      writeBuffers.put(streamName, writeBuffer);
    }
    LOGGER.info("Buffer creation completed.");

    onStart.call();

    writerPool.scheduleWithFixedDelay(
        () -> writeStreamsWithNRecords(MIN_RECORDS, streamNames, writeBuffers, recordWriter),
        THREAD_DELAY_MILLIS,
        THREAD_DELAY_MILLIS,
        TimeUnit.MILLISECONDS);
  }

  @Override
  protected void acceptTracked(AirbyteMessage message) {
    Preconditions.checkState(hasStarted, "Cannot accept records until consumer has started");

    // ignore other message types.
    if (message.getType() == AirbyteMessage.Type.RECORD) {
      final String streamName = message.getRecord().getStream();
      if (!streamNames.contains(streamName)) {
        throw new IllegalArgumentException(
            String.format("Message contained record from a stream that was not in the catalog. \ncatalog: %s , \nmessage: %s",
                Jsons.serialize(catalog), Jsons.serialize(message)));
      }
      writeBuffers.get(streamName).offer(Jsons.serialize(message.getRecord()).getBytes(Charsets.UTF_8));
    }
  }

  @SuppressWarnings("ResultOfMethodCallIgnored")
  @Override
  protected void close(boolean hasFailed) throws Exception {
    if (hasFailed) {
      LOGGER.error("executing on failed close procedure.");

      // kill executor pool fast.
      writerPool.shutdown();
      writerPool.awaitTermination(1, TimeUnit.SECONDS);
    } else {
      LOGGER.info("executing on success close procedure.");

      // shutdown executor pool with time to complete writes.
      writerPool.shutdown();
      writerPool.awaitTermination(GRACEFUL_SHUTDOWN_MINUTES, TimeUnit.MINUTES);

      // write anything that is left in the buffers.
      writeStreamsWithNRecords(0, streamNames, writeBuffers, recordWriter);
    }

    onClose.accept(hasFailed);

    for (CloseableQueue<byte[]> writeBuffer : writeBuffers.values()) {
      writeBuffer.close();
    }
  }

  private static void writeStreamsWithNRecords(int minRecords,
                                               Set<String> streamNames,
                                               Map<String, CloseableQueue<byte[]>> writeBuffers,
                                               CheckedBiConsumer<String, Stream<AirbyteRecordMessage>, Exception> recordWriter) {
    for (final String streamName : streamNames) {
      final CloseableQueue<byte[]> writeBuffer = writeBuffers.get(streamName);
      while (writeBuffer.size() > minRecords) {
        try {
          final List<AirbyteRecordMessage> records = Queues.toStream(writeBuffer)
              .limit(BufferedStreamConsumer.BATCH_SIZE)
              .map(record -> Jsons.deserialize(new String(record, Charsets.UTF_8), AirbyteRecordMessage.class))
              .collect(Collectors.toList());

          LOGGER.info("Writing stream {}. Max batch size: {}, Actual batch size: {}, Remaining buffered records: {}",
              streamName, BufferedStreamConsumer.BATCH_SIZE, records.size(), writeBuffer.size());
          recordWriter.accept(streamName, records.stream());
        } catch (Exception e) {
          throw new RuntimeException(e);
        }
      }
    }
  }

  public interface OnStartFunction extends VoidCallable {}

  public interface RecordWriter extends CheckedBiConsumer<String, Stream<AirbyteRecordMessage>, Exception> {

    @Override
    void accept(String streamName, Stream<AirbyteRecordMessage> recordStream) throws Exception;

  }

  public interface OnCloseFunction extends CheckedConsumer<Boolean, Exception> {

    @Override
    void accept(Boolean hasFailed) throws Exception;

  }

}
