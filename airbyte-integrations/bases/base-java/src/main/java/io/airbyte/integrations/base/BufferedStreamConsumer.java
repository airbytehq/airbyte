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

package io.airbyte.integrations.base;

import com.google.common.base.Charsets;
import io.airbyte.commons.concurrency.GracefulShutdownHandler;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.lang.CloseableQueue;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.queue.BigQueue;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Duration;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class BufferedStreamConsumer extends FailureTrackingConsumer<AirbyteMessage> implements DestinationConsumerStrategy {

  private static final Logger LOGGER = LoggerFactory.getLogger(BufferedStreamConsumer.class);
  private static final long THREAD_DELAY_MILLIS = 500L;

  private static final long GRACEFUL_SHUTDOWN_MINUTES = 5L;
  private static final int MIN_RECORDS = 500;
  private static final int BATCH_SIZE = 500;

  private final BufferedWriteOperations destination;
  private Map<String, DestinationWriteContext> writeConfigs;
  private Map<String, CloseableQueue<byte[]>> writeBuffers;
  private final ScheduledExecutorService writerPool;
  private final ConfiguredAirbyteCatalog catalog;

  public BufferedStreamConsumer(BufferedWriteOperations destination, ConfiguredAirbyteCatalog catalog) {
    this.destination = destination;
    this.writeConfigs = new HashMap<>();
    this.writeBuffers = new HashMap<>();
    this.writerPool = Executors.newSingleThreadScheduledExecutor();
    this.catalog = catalog;
    Runtime.getRuntime().addShutdownHook(new GracefulShutdownHandler(Duration.ofMinutes(GRACEFUL_SHUTDOWN_MINUTES), writerPool));
  }

  @Override
  public void setContext(Map<String, DestinationWriteContext> configs) throws IOException {
    writeConfigs = configs;
    writeBuffers = new HashMap<>();
    final Path queueRoot = Files.createTempDirectory("queues");
    for (String streamName : configs.keySet()) {
      final BigQueue writeBuffer = new BigQueue(queueRoot.resolve(streamName), streamName);
      writeBuffers.put(streamName, writeBuffer);
    }
    writerPool.scheduleWithFixedDelay(
        () -> writeStreamsWithNRecords(MIN_RECORDS, BATCH_SIZE, writeConfigs, writeBuffers, destination),
        THREAD_DELAY_MILLIS,
        THREAD_DELAY_MILLIS,
        TimeUnit.MILLISECONDS);
  }

  private static void writeStreamsWithNRecords(int minRecords,
                                               int batchSize,
                                               Map<String, DestinationWriteContext> writeConfigs,
                                               Map<String, CloseableQueue<byte[]>> writeBuffers,
                                               BufferedWriteOperations destination) {
    for (final Map.Entry<String, DestinationWriteContext> entry : writeConfigs.entrySet()) {
      final String schemaName = entry.getValue().getOutputNamespaceName();
      final String tmpTableName = entry.getValue().getOutputTableName();
      final CloseableQueue<byte[]> writeBuffer = writeBuffers.get(entry.getKey());
      while (writeBuffer.size() > minRecords) {
        try {
          destination.insertBufferedRecords(batchSize, writeBuffer, schemaName, tmpTableName);
        } catch (Exception e) {
          throw new RuntimeException(e);
        }
      }
    }
  }

  @Override
  protected void acceptTracked(AirbyteMessage message) throws Exception {
    // ignore other message types.
    if (message.getType() == AirbyteMessage.Type.RECORD) {
      if (!writeConfigs.containsKey(message.getRecord().getStream())) {
        throw new IllegalArgumentException(
            String.format("Message contained record from a stream that was not in the catalog. \ncatalog: %s , \nmessage: %s",
                Jsons.serialize(catalog), Jsons.serialize(message)));
      }
      writeBuffers.get(message.getRecord().getStream()).offer(Jsons.serialize(message.getRecord()).getBytes(Charsets.UTF_8));
    }
  }

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
      writeStreamsWithNRecords(0, BATCH_SIZE, writeConfigs, writeBuffers, destination);
    }
    for (CloseableQueue<byte[]> writeBuffer : writeBuffers.values()) {
      writeBuffer.close();
    }
  }

}
