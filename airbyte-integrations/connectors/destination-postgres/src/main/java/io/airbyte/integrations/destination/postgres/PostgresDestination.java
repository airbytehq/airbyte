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

import static org.jooq.impl.DSL.field;
import static org.jooq.impl.DSL.name;
import static org.jooq.impl.DSL.table;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.Charsets;
import io.airbyte.commons.concurrency.GracefulShutdownHandler;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.lang.CloseableQueue;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.db.Database;
import io.airbyte.db.Databases;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.DestinationConsumer;
import io.airbyte.integrations.base.FailureTrackingConsumer;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.SQLNamingResolvable;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.protocol.models.SyncMode;
import io.airbyte.queue.BigQueue;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.sql.SQLException;
import java.time.Duration;
import java.time.LocalDateTime;
import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;
import org.jooq.DSLContext;
import org.jooq.InsertValuesStep3;
import org.jooq.JSONB;
import org.jooq.Record;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class PostgresDestination implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(PostgresDestination.class);
  static final String COLUMN_NAME = "data";

  private final SQLNamingResolvable namingResolver;

  public PostgresDestination() {
    namingResolver = new PostgresSQLNaming();
  }

  @Override
  public ConnectorSpecification spec() throws IOException {
    // return a jsonschema representation of the spec for the integration.
    final String resourceString = MoreResources.readResource("spec.json");
    return Jsons.deserialize(resourceString, ConnectorSpecification.class);
  }

  @Override
  public AirbyteConnectionStatus check(JsonNode config) {
    try (final Database database = getDatabase(config)) {
      database.query(ctx -> ctx.execute(
          "SELECT *\n"
              + "FROM pg_catalog.pg_tables\n"
              + "WHERE schemaname != 'pg_catalog' AND schemaname != 'information_schema' LIMIT 1;"));

      return new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED);
    } catch (Exception e) {
      // todo (cgardens) - better error messaging for common cases. e.g. wrong password.
      return new AirbyteConnectionStatus().withStatus(Status.FAILED).withMessage("Can't connect with provided configuration.");
    }
  }

  @Override
  public SQLNamingResolvable getNamingResolver() {
    return namingResolver;
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
   * @param catalog - schema of the incoming messages.
   * @return consumer that writes singer messages to the database.
   * @throws Exception - anything could happen!
   */
  @Override
  public DestinationConsumer<AirbyteMessage> write(JsonNode config, ConfiguredAirbyteCatalog catalog) throws Exception {
    // connect to db.
    final Database database = getDatabase(config);
    final Map<String, WriteConfig> writeBuffers = new HashMap<>();
    final Set<String> schemaSet = new HashSet<>();
    // create tmp tables if not exist
    for (final ConfiguredAirbyteStream stream : catalog.getStreams()) {
      final String streamName = stream.getStream().getName();
      final String schemaName = getNamingResolver().getRawSchemaName(config, getConfigSchemaName(config), streamName);
      final String tableName = getNamingResolver().getRawTableName(config, streamName);
      final String tmpTableName = getNamingResolver().getTmpTableName(config, streamName);
      if (!schemaSet.contains(schemaName)) {
        database.query(ctx -> ctx.execute(createSchemaQuery(schemaName)));
        schemaSet.add(schemaName);
      }
      database.query(ctx -> ctx.execute(createRawTableQuery(schemaName, tmpTableName)));

      final Path queueRoot = Files.createTempDirectory("queues");
      final BigQueue writeBuffer = new BigQueue(queueRoot.resolve(streamName), streamName);
      final SyncMode syncMode = stream.getSyncMode() == null ? SyncMode.FULL_REFRESH : stream.getSyncMode();
      writeBuffers.put(streamName, new WriteConfig(schemaName, tableName, tmpTableName, writeBuffer, syncMode));
    }

    // write to tmp tables
    // if success copy delete main table if exists. rename tmp tables to real tables.
    return new RecordConsumer(database, writeBuffers, catalog);
  }

  static String createSchemaQuery(String schemaName) {
    return String.format("CREATE SCHEMA IF NOT EXISTS %s;\n", schemaName);
  }

  static String createRawTableQuery(String schemaName, String streamName) {
    return String.format(
        "CREATE TABLE IF NOT EXISTS %s.%s ( \n"
            + "ab_id VARCHAR PRIMARY KEY,\n"
            + "%s JSONB,\n"
            + "emitted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP\n"
            + ");\n",
        schemaName, streamName, COLUMN_NAME);
  }

  public static class RecordConsumer extends FailureTrackingConsumer<AirbyteMessage> implements DestinationConsumer<AirbyteMessage> {

    private static final long THREAD_DELAY_MILLIS = 500L;

    private static final long GRACEFUL_SHUTDOWN_MINUTES = 5L;
    private static final int MIN_RECORDS = 500;
    private static final int BATCH_SIZE = 500;

    private final ScheduledExecutorService writerPool;
    private final Database database;
    private final Map<String, WriteConfig> writeConfigs;
    private final ConfiguredAirbyteCatalog catalog;

    public RecordConsumer(Database database, Map<String, WriteConfig> writeConfigs, ConfiguredAirbyteCatalog catalog) {
      this.database = database;
      this.writeConfigs = writeConfigs;
      this.catalog = catalog;
      this.writerPool = Executors.newSingleThreadScheduledExecutor();
      // todo (cgardens) - how long? boh.
      Runtime.getRuntime().addShutdownHook(new GracefulShutdownHandler(Duration.ofMinutes(GRACEFUL_SHUTDOWN_MINUTES), writerPool));

      writerPool.scheduleWithFixedDelay(
          () -> writeStreamsWithNRecords(MIN_RECORDS, BATCH_SIZE, writeConfigs, database),
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
     * @param database - connection to the db.
     */
    private static void writeStreamsWithNRecords(int minRecords,
                                                 int batchSize,
                                                 Map<String, WriteConfig> writeBuffers,
                                                 Database database) {
      for (final Map.Entry<String, WriteConfig> entry : writeBuffers.entrySet()) {
        final String schemaName = entry.getValue().getSchemaName();
        final String tmpTableName = entry.getValue().getTmpTableName();
        final CloseableQueue<byte[]> writeBuffer = entry.getValue().getWriteBuffer();
        while (writeBuffer.size() > minRecords) {
          try {
            database.query(ctx -> buildWriteQuery(ctx, batchSize, writeBuffer, schemaName, tmpTableName).execute());
          } catch (SQLException e) {
            throw new RuntimeException(e);
          }
        }
      }
    }

    // build the following query:
    // INSERT INTO <schemaName>.<tableName>(data)
    // VALUES
    // ({ "my": "data" }),
    // ({ "my": "data" });
    private static InsertValuesStep3<Record, String, JSONB, OffsetDateTime> buildWriteQuery(DSLContext ctx,
                                                                                            int batchSize,
                                                                                            CloseableQueue<byte[]> writeBuffer,
                                                                                            String schemaName,
                                                                                            String tmpTableName) {
      InsertValuesStep3<Record, String, JSONB, OffsetDateTime> step =
          ctx.insertInto(table(name(schemaName, tmpTableName)), field("ab_id", String.class),
              field(COLUMN_NAME, JSONB.class), field("emitted_at", OffsetDateTime.class));

      for (int i = 0; i < batchSize; i++) {
        final byte[] record = writeBuffer.poll();
        if (record == null) {
          break;
        }
        final AirbyteRecordMessage message = Jsons.deserialize(new String(record, Charsets.UTF_8), AirbyteRecordMessage.class);

        step = step.values(UUID.randomUUID().toString(), JSONB.valueOf(Jsons.serialize(message.getData())),
            OffsetDateTime.of(LocalDateTime.ofEpochSecond(message.getEmittedAt() / 1000, 0, ZoneOffset.UTC), ZoneOffset.UTC));
      }

      return step;
    }

    @Override
    public void acceptTracked(AirbyteMessage message) {
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
        writeStreamsWithNRecords(0, 500, writeConfigs, database);

        database.transaction(ctx -> {
          final StringBuilder query = new StringBuilder();
          for (final WriteConfig writeConfig : writeConfigs.values()) {
            // create tables if not exist.
            final String schemaName = writeConfig.getSchemaName();
            query.append(createRawTableQuery(writeConfig.getSchemaName(), writeConfig.getTableName()));

            switch (writeConfig.getSyncMode()) {
              case FULL_REFRESH -> {
                // truncate table if already exist.
                query.append(String.format("TRUNCATE TABLE %s.%s;\n", writeConfig.getSchemaName(), writeConfig.getTableName()));
              }
              case INCREMENTAL -> {}
              default -> throw new IllegalStateException("Unrecognized sync mode: " + writeConfig.getSyncMode());
            }
            // always copy data from tmp table into "main" table.
            query.append(String.format("INSERT INTO %s.%s SELECT * FROM %s.%s;\n", writeConfig.getSchemaName(),
                writeConfig.getTableName(), writeConfig.getSchemaName(), writeConfig.getTmpTableName()));
          }
          return ctx.execute(query.toString());
        });
      }

      // close buffers.
      for (final WriteConfig writeConfig : writeConfigs.values()) {
        writeConfig.getWriteBuffer().close();
      }
      cleanupTmpTables(database, writeConfigs);
      database.close();
    }

    private static void cleanupTmpTables(Database database, Map<String, WriteConfig> writeConfigs) {
      for (WriteConfig writeConfig : writeConfigs.values()) {
        try {
          database.query(
              ctx -> ctx.execute(String.format("DROP TABLE IF EXISTS %s.%s;", writeConfig.getSchemaName(), writeConfig.getTmpTableName())));
        } catch (SQLException e) {
          throw new RuntimeException(e);
        }
      }
    }

  }

  private static class WriteConfig {

    private final String schemaName;
    private final String tableName;
    private final String tmpTableName;
    private final CloseableQueue<byte[]> writeBuffer;
    private final SyncMode syncMode;

    private WriteConfig(String schemaName, String tableName, String tmpTableName, CloseableQueue<byte[]> writeBuffer, SyncMode syncMode) {
      this.schemaName = schemaName;
      this.tableName = tableName;
      this.tmpTableName = tmpTableName;
      this.writeBuffer = writeBuffer;
      this.syncMode = syncMode;
    }

    public String getSchemaName() {
      return schemaName;
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

    public SyncMode getSyncMode() {
      return syncMode;
    }

  }

  private Database getDatabase(JsonNode config) {
    return Databases.createPostgresDatabase(
        config.get("username").asText(),
        config.get("password").asText(),
        String.format("jdbc:postgresql://%s:%s/%s",
            config.get("host").asText(),
            config.get("port").asText(),
            config.get("database").asText()));
  }

  private static String getConfigSchemaName(JsonNode config) {
    if (config.has("schema")) {
      return config.get("schema").asText();
    } else {
      return "public";
    }
  }

  public static void main(String[] args) throws Exception {
    final Destination destination = new PostgresDestination();
    LOGGER.info("starting destination: {}", PostgresDestination.class);
    new IntegrationRunner(destination).run(args);
    LOGGER.info("completed destination: {}", PostgresDestination.class);
  }

}
