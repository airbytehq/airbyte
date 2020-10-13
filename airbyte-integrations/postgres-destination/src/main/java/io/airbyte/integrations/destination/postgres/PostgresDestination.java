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

package io.airbyte.integrations.destination.postgres;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.Charsets;
import io.airbyte.commons.concurrency.GracefulShutdownHandler;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.lang.CloseableQueue;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.config.DestinationConnectionSpecification;
import io.airbyte.config.Schema;
import io.airbyte.config.StandardCheckConnectionOutput;
import io.airbyte.config.StandardCheckConnectionOutput.Status;
import io.airbyte.config.StandardDiscoverSchemaOutput;
import io.airbyte.config.Stream;
import io.airbyte.db.DatabaseHelper;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.DestinationConsumer;
import io.airbyte.integrations.base.FailureTrackingConsumer;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.queue.BigQueue;
import io.airbyte.singer.SingerMessage;
import io.airbyte.singer.SingerMessage.Type;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.sql.SQLException;
import java.time.Instant;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;
import org.apache.commons.dbcp2.BasicDataSource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class PostgresDestination implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(PostgresDestination.class);
  static final String COLUMN_NAME = "data";

  @Override
  public DestinationConnectionSpecification spec() throws IOException {
    // return a jsonschema representation of the spec for the integration.
    final String resourceString = MoreResources.readResource("spec.json");
    return Jsons.deserialize(resourceString, DestinationConnectionSpecification.class);
  }

  @Override
  public StandardCheckConnectionOutput check(JsonNode config) {
    try {
      final BasicDataSource connectionPool = getConnectionPool(config);
      DatabaseHelper.query(connectionPool, ctx -> ctx.execute(
          "SELECT *\n"
              + "FROM pg_catalog.pg_tables\n"
              + "WHERE schemaname != 'pg_catalog' AND schemaname != 'information_schema';"));

      connectionPool.close();
    } catch (Exception e) {
      // todo (cgardens) - better error messaging for common cases. e.g. wrong password.
      return new StandardCheckConnectionOutput().withStatus(Status.FAILURE).withMessage(e.getMessage());
    }

    return new StandardCheckConnectionOutput().withStatus(Status.SUCCESS);
  }

  @Override
  public StandardDiscoverSchemaOutput discover(JsonNode config) {
    throw new RuntimeException("Not Implemented");
  }

  /**
   * Strategy:
   * <p>
   * 1. Create a temporary table for each stream
   * </p>
   * <p>
   * 2. Accumulate records in a buffer. One buffer per stream.
   * </p>
   * <p>
   * 3. As records accumulate write them in batch to the database. We set a minimum numbers of records
   * before writing to avoid wasteful record-wise writes.
   * </p>
   * <p>
   * 4. Once all records have been written to buffer, flush the buffer and write any remaining records
   * to the database (regardless of how few are left).
   * </p>
   * <p>
   * 5. In a single transaction, delete the target tables if they exist and rename the temp tables to
   * the final table name.
   * </p>
   *
   * @param config - integration-specific configuration object as json. e.g. { "username": "airbyte",
   *        "password": "super secure" }
   * @param schema - schema of the incoming messages.
   * @return consumer that writes singer messages to the database.
   * @throws Exception - anything could happen!
   */
  @Override
  public DestinationConsumer<SingerMessage> write(JsonNode config, Schema schema) throws Exception {
    // connect to db.
    final BasicDataSource connectionPool = getConnectionPool(config);
    Map<String, WriteConfig> writeBuffers = new HashMap<>();

    // create tmp tables if not exist
    for (final Stream stream : schema.getStreams()) {
      final String tableName = stream.getName();
      final String tmpTableName = stream.getName() + "_" + Instant.now().toEpochMilli();
      DatabaseHelper.query(connectionPool, ctx -> ctx.execute(String.format(
          "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";\n"
              + "CREATE TABLE \"%s\" ( \n"
              + "\"ab_id\" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),\n"
              + "\"%s\" jsonb,\n"
              + "\"ab_inserted_at\" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP\n"
              + ");",
          tmpTableName, COLUMN_NAME)));

      final Path queueRoot = Files.createTempDirectory("queues");
      final BigQueue writeBuffer = new BigQueue(queueRoot.resolve(stream.getName()), stream.getName());
      writeBuffers.put(stream.getName(), new WriteConfig(tableName, tmpTableName, writeBuffer));
    }

    // write to tmp tables
    // if success copy delete main table if exists. rename tmp tables to real tables.
    return new RecordConsumer(connectionPool, writeBuffers, schema);
  }

  public static class RecordConsumer extends FailureTrackingConsumer<SingerMessage> implements DestinationConsumer<SingerMessage> {

    private static final long THREAD_DELAY_MILLIS = 500L;

    private static final long GRACEFUL_SHUTDOWN_MINUTES = 5L;
    private static final int MIN_RECORDS = 500;
    private static final int BATCH_SIZE = 500;

    private final ScheduledExecutorService writerPool;
    private final BasicDataSource connectionPool;
    private final Map<String, WriteConfig> writeConfigs;
    private final Schema schema;

    public RecordConsumer(BasicDataSource connectionPool, Map<String, WriteConfig> writeConfigs, Schema schema) {
      this.connectionPool = connectionPool;
      this.writeConfigs = writeConfigs;
      this.schema = schema;
      this.writerPool = Executors.newSingleThreadScheduledExecutor();
      // todo (cgardens) - how long? boh.
      Runtime.getRuntime().addShutdownHook(new GracefulShutdownHandler(GRACEFUL_SHUTDOWN_MINUTES, TimeUnit.MINUTES, writerPool));

      writerPool.scheduleWithFixedDelay(
          () -> writeStreamsWithNRecords(MIN_RECORDS, BATCH_SIZE, writeConfigs, connectionPool),
          THREAD_DELAY_MILLIS,
          THREAD_DELAY_MILLIS,
          TimeUnit.MILLISECONDS);
    }

    /**
     * Write records from buffer to postgres in batch.
     *
     * @param minRecords - the minimum number of records in the buffer before writing. helps avoid
     *        wastefully writing one record at a time.
     * @param batchSize - the maximum number of records to write in a single insert.
     * @param writeBuffers - map of stream name to its respective buffer.
     * @param connectionPool - connection to the db.
     */
    private static void writeStreamsWithNRecords(int minRecords,
                                                 int batchSize,
                                                 Map<String, WriteConfig> writeBuffers,
                                                 BasicDataSource connectionPool) {
      for (final Map.Entry<String, WriteConfig> entry : writeBuffers.entrySet()) {
        final String tmpTableName = entry.getValue().getTmpTableName();
        final CloseableQueue<byte[]> writeBuffer = entry.getValue().getWriteBuffer();
        while (writeBuffer.size() > minRecords) {
          try {
            DatabaseHelper.query(connectionPool, ctx -> ctx.execute(buildWriteQuery(batchSize, writeBuffer, tmpTableName)));
          } catch (SQLException e) {
            throw new RuntimeException(e);
          }
        }
      }
    }

    // build the following query:
    // INSERT INTO <tableName>(data)
    // VALUES
    // ({ "my": "data" }),
    // ({ "my": "data" });
    private static String buildWriteQuery(int batchSize, CloseableQueue<byte[]> writeBuffer, String tmpTableName) {
      final StringBuilder query = new StringBuilder(String.format("INSERT INTO %s(%s)\n", tmpTableName, COLUMN_NAME))
          .append("VALUES \n");
      boolean firstRecordInQuery = true;
      for (int i = 0; i < batchSize; i++) {
        final byte[] record = writeBuffer.poll();
        if (record == null) {
          break;
        }

        // don't write comma before the first record.
        if (firstRecordInQuery) {
          firstRecordInQuery = false;
        } else {
          query.append(", \n");
        }
        query.append(String.format("('%s')", new String(record, Charsets.UTF_8)));
      }
      query.append(";");

      return query.toString();
    }

    @Override
    public void acceptTracked(SingerMessage singerMessage) {
      // ignore other message types.
      if (singerMessage.getType() == Type.RECORD) {
        if (!writeConfigs.containsKey(singerMessage.getStream())) {
          throw new IllegalArgumentException(
              String.format("Message contained record from a stream that was not in the catalog. \ncatalog: %s , \nmessage: %s",
                  Jsons.serialize(schema), Jsons.serialize(singerMessage)));
        }

        writeConfigs.get(singerMessage.getStream()).getWriteBuffer().offer(Jsons.toBytes(singerMessage.getRecord()));
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
        LOGGER.error("executing on success close procedure.");

        // shutdown executor pool with time to complete writes.
        writerPool.shutdown();
        writerPool.awaitTermination(GRACEFUL_SHUTDOWN_MINUTES, TimeUnit.MINUTES);

        // write anything that is left in the buffers.
        writeStreamsWithNRecords(0, 500, writeConfigs, connectionPool);

        // delete tables if already exist. copy new tables into their place.
        DatabaseHelper.transaction(connectionPool, ctx -> {
          final StringBuilder query = new StringBuilder();
          for (final WriteConfig writeConfig : writeConfigs.values()) {
            query.append(String.format("DROP TABLE IF EXISTS %s;\n", writeConfig.getTableName()));

            query.append(String.format("ALTER TABLE %s RENAME TO %s;\n", writeConfig.getTmpTableName(), writeConfig.getTableName()));
          }
          return ctx.execute(query.toString());
        });

      }

      // close buffers.
      for (final WriteConfig writeConfig : writeConfigs.values()) {
        writeConfig.getWriteBuffer().close();
      }
      cleanupTmpTables(connectionPool, writeConfigs);
    }

    private static void cleanupTmpTables(BasicDataSource connectionPool, Map<String, WriteConfig> writeConfigs) {
      for (WriteConfig writeConfig : writeConfigs.values()) {
        try {
          DatabaseHelper.query(connectionPool, ctx -> ctx.execute(String.format("DROP TABLE IF EXISTS %s;", writeConfig.getTmpTableName())));
        } catch (SQLException e) {
          throw new RuntimeException(e);
        }
      }
    }

  }

  private static class WriteConfig {

    private final String tableName;
    private final String tmpTableName;
    private final CloseableQueue<byte[]> writeBuffer;

    private WriteConfig(String tableName, String tmpTableName, CloseableQueue<byte[]> writeBuffer) {
      this.tableName = tableName;
      this.tmpTableName = tmpTableName;
      this.writeBuffer = writeBuffer;
    }

    public String getTableName() {
      return tableName;
    }

    public String getTmpTableName() {
      return tmpTableName;
    }

    public CloseableQueue<byte[]> getWriteBuffer() {
      return writeBuffer;
    }

  }

  private BasicDataSource getConnectionPool(JsonNode config) {
    return DatabaseHelper.getConnectionPool(
        config.get("username").asText(),
        config.get("password").asText(),
        String.format("jdbc:postgresql://%s:%s/%s",
            config.get("host").asText(),
            config.get("port").asText(),
            config.get("database").asText()));
  }

  public static void main(String[] args) throws Exception {
    final Destination destination = new PostgresDestination();
    LOGGER.info("starting destination: {}", PostgresDestination.class);
    new IntegrationRunner(destination).run(args);
    LOGGER.info("completed destination: {}", PostgresDestination.class);
  }

}
