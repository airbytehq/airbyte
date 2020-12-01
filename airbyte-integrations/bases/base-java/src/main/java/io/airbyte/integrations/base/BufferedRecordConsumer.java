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
import java.sql.SQLException;
import java.time.Duration;
import java.util.Map;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class BufferedRecordConsumer extends FailureTrackingConsumer<AirbyteMessage> implements DestinationConsumer<AirbyteMessage> {

  private static final Logger LOGGER = LoggerFactory.getLogger(BufferedRecordConsumer.class);

  private static final long THREAD_DELAY_MILLIS = 500L;

  private static final long GRACEFUL_SHUTDOWN_MINUTES = 5L;
  private static final int MIN_RECORDS = 500;
  private static final int BATCH_SIZE = 500;

  private final DestinationConsumerCallback destination;
  private final Map<String, BufferedWriteConfig> writeConfigs;
  private final ConfiguredAirbyteCatalog catalog;
  private final ScheduledExecutorService writerPool;

  public BufferedRecordConsumer(DestinationConsumerCallback destination,
                                Map<String, BufferedWriteConfig> writeConfigs,
                                ConfiguredAirbyteCatalog catalog) {
    this.destination = destination;
    this.writeConfigs = writeConfigs;
    this.catalog = catalog;
    this.writerPool = Executors.newSingleThreadScheduledExecutor();
    Runtime.getRuntime().addShutdownHook(new GracefulShutdownHandler(Duration.ofMinutes(GRACEFUL_SHUTDOWN_MINUTES), writerPool));

    writerPool.scheduleWithFixedDelay(
        () -> writeStreamsWithNRecords(MIN_RECORDS, BATCH_SIZE, writeConfigs, destination),
        THREAD_DELAY_MILLIS,
        THREAD_DELAY_MILLIS,
        TimeUnit.MILLISECONDS);
  }

  /**
   * Write records from buffer to destination in batch.
   *
   * @param minRecords - the minimum number of records in the buffer before writing. helps avoid
   *        wastefully writing one record at a time.
   * @param batchSize - the maximum number of records to write in a single insert.
   * @param writeBuffers - map of stream name to its respective buffer.
   * @param destination - Connection to destination
   */
  private static void writeStreamsWithNRecords(int minRecords,
                                               int batchSize,
                                               Map<String, BufferedWriteConfig> writeBuffers,
                                               DestinationConsumerCallback destination) {
    for (final Map.Entry<String, BufferedWriteConfig> entry : writeBuffers.entrySet()) {
      final String schemaName = entry.getValue().getSchemaName();
      final String tmpTableName = entry.getValue().getTmpTableName();
      final CloseableQueue<byte[]> writeBuffer = entry.getValue().getWriteBuffer();
      while (writeBuffer.size() > minRecords) {
        destination.writeBufferedRecords(batchSize, writeBuffer, schemaName, tmpTableName);
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
      writeConfigs.get(message.getRecord().getStream()).getWriteBuffer().offer(Jsons.serialize(message.getRecord()).getBytes(Charsets.UTF_8));
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
      writeStreamsWithNRecords(0, 500, writeConfigs, destination);

      commitRawTable();
    }

    // close buffers.
    for (final BufferedWriteConfig writeContext : writeConfigs.values()) {
      writeContext.getWriteBuffer().close();
    }
    for (BufferedWriteConfig writeContext : writeConfigs.values()) {
      try {
        destination.queryDatabase(String.format("DROP TABLE IF EXISTS %s.%s;", writeContext.getSchemaName(), writeContext.getTmpTableName()));
      } catch (SQLException | InterruptedException e) {
        throw new RuntimeException(e);
      }
    }
  }

  private void commitRawTable() throws Exception {
    final StringBuilder query = new StringBuilder();
    for (final BufferedWriteConfig writeConfig : writeConfigs.values()) {
      // create tables if not exist.
      destination.queryDatabase(destination.createTableQuery(writeConfig.getSchemaName(), writeConfig.getTableName()));

      switch (writeConfig.getSyncMode()) {
        case FULL_REFRESH -> query.append(String.format("TRUNCATE TABLE %s.%s;\n", writeConfig.getSchemaName(), writeConfig.getTableName()));
        case INCREMENTAL -> {}
        default -> throw new IllegalStateException("Unrecognized sync mode: " + writeConfig.getSyncMode());
      }
      // always copy data from tmp table into "main" table.
      query.append(String.format("INSERT INTO %s.%s SELECT * FROM %s.%s;\n", writeConfig.getSchemaName(),
          writeConfig.getTableName(), writeConfig.getSchemaName(), writeConfig.getTmpTableName()));
    }
    destination.queryDatabaseInTransaction(query.toString());
  }

}
