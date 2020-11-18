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

package io.airbyte.integrations.destination.snowflake;

import com.google.common.base.Charsets;
import io.airbyte.commons.concurrency.GracefulShutdownHandler;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.lang.CloseableQueue;
import io.airbyte.integrations.base.DestinationConsumer;
import io.airbyte.integrations.base.FailureTrackingConsumer;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.time.Duration;
import java.time.Instant;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;
import java.util.function.Supplier;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SnowflakeRecordConsumer extends FailureTrackingConsumer<AirbyteMessage> implements DestinationConsumer<AirbyteMessage> {

  private static final Logger LOGGER = LoggerFactory.getLogger(SnowflakeRecordConsumer.class);

  private static final long THREAD_DELAY_MILLIS = 500L;

  private static final long GRACEFUL_SHUTDOWN_MINUTES = 5L;
  private static final int MIN_RECORDS = 500;
  private static final int BATCH_SIZE = 500;

  private final ScheduledExecutorService writerPool;
  private final Supplier<Connection> connectionFactory;
  private final Map<String, SnowflakeWriteContext> writeContexts;
  private final ConfiguredAirbyteCatalog catalog;

  public SnowflakeRecordConsumer(Supplier<Connection> connectionFactory,
                                 Map<String, SnowflakeWriteContext> writeContexts,
                                 ConfiguredAirbyteCatalog catalog) {
    this.connectionFactory = connectionFactory;
    this.writeContexts = writeContexts;
    this.catalog = catalog;
    this.writerPool = Executors.newSingleThreadScheduledExecutor();
    Runtime.getRuntime().addShutdownHook(new GracefulShutdownHandler(Duration.ofMinutes(GRACEFUL_SHUTDOWN_MINUTES), writerPool));

    writerPool.scheduleWithFixedDelay(
        () -> writeStreamsWithNRecords(MIN_RECORDS, BATCH_SIZE, writeContexts, connectionFactory),
        THREAD_DELAY_MILLIS,
        THREAD_DELAY_MILLIS,
        TimeUnit.MILLISECONDS);
  }

  /**
   * Write records from buffer to Snowflake in batch.
   *
   * @param minRecords - the minimum number of records in the buffer before writing. helps avoid
   *        wastefully writing one record at a time.
   * @param batchSize - the maximum number of records to write in a single insert.
   * @param writeBuffers - map of stream name to its respective buffer.
   * @param connectionFactory - factory to produce a connection
   */
  private static void writeStreamsWithNRecords(int minRecords,
                                               int batchSize,
                                               Map<String, SnowflakeWriteContext> writeBuffers,
                                               Supplier<Connection> connectionFactory) {
    for (final Map.Entry<String, SnowflakeWriteContext> entry : writeBuffers.entrySet()) {
      final String tmpTableName = entry.getValue().getTmpTableName();
      final CloseableQueue<byte[]> writeBuffer = entry.getValue().getWriteBuffer();
      while (writeBuffer.size() > minRecords) {
        executeWriteQuery(connectionFactory, batchSize, writeBuffer, tmpTableName);
      }
    }
  }

  private static void executeWriteQuery(Supplier<Connection> connectionFactory,
                                        int batchSize,
                                        CloseableQueue<byte[]> writeBuffer,
                                        String tmpTableName) {
    try (Connection conn = connectionFactory.get()) {
      conn.setAutoCommit(false);

      try (PreparedStatement statement = conn.prepareStatement(
          String.format("INSERT INTO \"%s\" (\"ab_id\", \"%s\", \"emitted_at\") SELECT ?, parse_json(?), ?", tmpTableName,
              SnowflakeDestination.COLUMN_NAME))) {

        for (int i = 0; i < batchSize; i++) {
          final byte[] record = writeBuffer.poll();
          if (record == null) {
            break;
          }
          final AirbyteRecordMessage message = Jsons.deserialize(new String(record, Charsets.UTF_8), AirbyteRecordMessage.class);

          // 1-indexed
          statement.setString(1, UUID.randomUUID().toString());
          statement.setString(2, Jsons.serialize(message.getData()));
          statement.setTimestamp(3, Timestamp.from(Instant.ofEpochMilli(message.getEmittedAt())));
          statement.addBatch();
        }

        statement.executeBatch();
        conn.commit();
      }
    } catch (SQLException e) {
      throw new RuntimeException(e);
    }
  }

  @Override
  public void acceptTracked(AirbyteMessage message) {
    // ignore other message types.
    if (message.getType() == AirbyteMessage.Type.RECORD) {
      if (!writeContexts.containsKey(message.getRecord().getStream())) {
        throw new IllegalArgumentException(
            String.format("Message contained record from a stream that was not in the catalog. \ncatalog: %s , \nmessage: %s",
                Jsons.serialize(catalog), Jsons.serialize(message)));
      }

      writeContexts.get(message.getRecord().getStream()).getWriteBuffer().offer(Jsons.serialize(message.getRecord()).getBytes(Charsets.UTF_8));
    }
  }

  @Override
  public void close(boolean hasFailed) throws Exception {
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

      // flush buffers
      writeStreamsWithNRecords(0, 500, writeContexts, connectionFactory);

      // delete tables if already exist. move new tables into their place.
      final StringBuilder query = new StringBuilder();
      query.append("BEGIN;");
      for (final SnowflakeWriteContext writeContext : writeContexts.values()) {
        query.append(String.format("DROP TABLE IF EXISTS \"%s\";\n", writeContext.getTableName()));
        query.append(String.format("ALTER TABLE \"%s\" RENAME TO \"%s\";\n", writeContext.getTmpTableName(), writeContext.getTableName()));
      }
      query.append("COMMIT;");

      final String renameQuery = query.toString();

      SnowflakeDatabase.executeSync(connectionFactory, renameQuery, true, rs -> null);
    }

    // close buffers.
    for (final SnowflakeWriteContext writeContext : writeContexts.values()) {
      writeContext.getWriteBuffer().close();
    }
    cleanupTmpTables(connectionFactory, writeContexts);
  }

  private static void cleanupTmpTables(Supplier<Connection> connectionFactory, Map<String, SnowflakeWriteContext> writeContexts) {
    for (SnowflakeWriteContext writeContext : writeContexts.values()) {
      try {
        SnowflakeDatabase.executeSync(connectionFactory, String.format("DROP TABLE IF EXISTS \"%s\";", writeContext.getTmpTableName()));
      } catch (SQLException | InterruptedException e) {
        throw new RuntimeException(e);
      }
    }
  }

}
