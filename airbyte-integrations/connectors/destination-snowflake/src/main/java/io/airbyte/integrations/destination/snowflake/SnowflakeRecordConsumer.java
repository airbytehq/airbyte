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
import com.google.common.collect.Lists;
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
import java.util.List;
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
      final String schemaName = entry.getValue().getSchemaName();
      final String tmpTableName = entry.getValue().getTmpTableName();
      final CloseableQueue<byte[]> writeBuffer = entry.getValue().getWriteBuffer();
      while (writeBuffer.size() > minRecords) {
        executeWriteQuery(connectionFactory, batchSize, writeBuffer, schemaName, tmpTableName);
      }
    }
  }

  private static void executeWriteQuery(Supplier<Connection> connectionFactory,
                                        int batchSize,
                                        CloseableQueue<byte[]> writeBuffer,
                                        String schemaName,
                                        String tmpTableName) {
    final List<AirbyteRecordMessage> records = accumulateRecordsFromBuffer(writeBuffer, batchSize);

    LOGGER.info("max size of batch: {}", batchSize);
    LOGGER.info("actual size of batch: {}", records.size());

    if (records.isEmpty()) {
      return;
    }

    try (final Connection conn = connectionFactory.get()) {
      // Strategy: We want to use PreparedStatement because it handles binding values to the SQL query
      // (e.g. handling formatting timestamps). A PreparedStatement statement is created by supplying the
      // full SQL string at creation time. Then subsequently specifying which values are bound to the
      // string. Thus there will be two loops below.
      // 1) Loop over records to build the full string.
      // 2) Loop over the records and bind the appropriate values to the string.
      final StringBuilder sql = new StringBuilder().append(String.format(
          "INSERT INTO %s.%s (ab_id, %s, emitted_at) SELECT column1, parse_json(column2), column3 FROM VALUES\n",
          schemaName,
          tmpTableName,
          SnowflakeDestination.COLUMN_NAME));

      // first loop: build SQL string.
      records.forEach(r -> sql.append("(?, ?, ?),\n"));
      final String s = sql.toString();
      final String s1 = s.substring(0, s.length() - 2) + ";";

      try (final PreparedStatement statement = conn.prepareStatement(s1)) {
        // second loop: bind values to the SQL string.
        int i = 1;
        for (final AirbyteRecordMessage message : records) {
          // 1-indexed
          statement.setString(i, UUID.randomUUID().toString());
          statement.setString(i + 1, Jsons.serialize(message.getData()));
          statement.setTimestamp(i + 2, Timestamp.from(Instant.ofEpochMilli(message.getEmittedAt())));
          i += 3;
        }

        statement.execute();
      }
    } catch (SQLException e) {
      throw new RuntimeException(e);
    }
  }

  private static List<AirbyteRecordMessage> accumulateRecordsFromBuffer(CloseableQueue<byte[]> writeBuffer, int maxRecords) {
    final List<AirbyteRecordMessage> records = Lists.newArrayList();
    for (int i = 0; i < maxRecords; i++) {
      final byte[] record = writeBuffer.poll();
      if (record == null) {
        break;
      }
      final AirbyteRecordMessage message = Jsons.deserialize(new String(record, Charsets.UTF_8), AirbyteRecordMessage.class);
      records.add(message);
    }

    return records;
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
        query.append(String.format("DROP TABLE IF EXISTS %s.%s;\n", writeContext.getSchemaName(), writeContext.getTableName()));
        query.append(String.format("ALTER TABLE %s.%s RENAME TO %s.%s;\n", writeContext.getSchemaName(), writeContext.getTmpTableName(),
            writeContext.getSchemaName(), writeContext.getTableName()));
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
        SnowflakeDatabase.executeSync(connectionFactory,
            String.format("DROP TABLE IF EXISTS %s.%s;", writeContext.getSchemaName(), writeContext.getTmpTableName()));
      } catch (SQLException | InterruptedException e) {
        throw new RuntimeException(e);
      }
    }
  }

}
