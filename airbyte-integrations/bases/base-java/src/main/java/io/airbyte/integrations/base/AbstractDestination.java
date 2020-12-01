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

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.SyncMode;
import io.airbyte.queue.BigQueue;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

public abstract class AbstractDestination implements Destination, DestinationWriteOperations {

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
    connectDatabase(config);
    final Map<String, BufferedWriteConfig> writeBuffers = new HashMap<>();
    final Set<String> schemaSet = new HashSet<>();
    // create tmp tables if not exist
    for (final ConfiguredAirbyteStream stream : catalog.getStreams()) {
      final String streamName = stream.getStream().getName();
      final String schemaName = getNamingResolver().getIdentifier(getDefaultSchemaName(config));
      final String tableName = getNamingResolver().getRawTableName(streamName);
      final String tmpTableName = getNamingResolver().getTmpTableName(streamName);
      if (!schemaSet.contains(schemaName)) {
        createSchema(schemaName);
        schemaSet.add(schemaName);
      }
      createTable(schemaName, tmpTableName);

      final Path queueRoot = Files.createTempDirectory("queues");
      final BigQueue writeBuffer = new BigQueue(queueRoot.resolve(streamName), streamName);
      final SyncMode syncMode = stream.getSyncMode() == null ? SyncMode.FULL_REFRESH : stream.getSyncMode();
      writeBuffers.put(streamName, new BufferedWriteConfig(schemaName, tableName, tmpTableName, writeBuffer, syncMode));
    }
    // write to tmp tables
    // if success copy delete main table if exists. rename tmp tables to real tables.
    return new BufferedRecordConsumer(this, writeBuffers, catalog);
  }

  @Override
  public void createSchema(String schemaName) throws Exception {
    queryDatabase(createSchemaQuery(schemaName));
  }

  protected String createSchemaQuery(String schemaName) {
    return String.format("CREATE SCHEMA IF NOT EXISTS %s;\n", schemaName);
  }

  @Override
  public void createTable(String schemaName, String tableName) throws Exception {
    queryDatabase(createTableQuery(schemaName, tableName));
  }

  protected abstract String createTableQuery(String schemaName, String tableName);

  @Override
  public void commitFinalTables(Map<String, BufferedWriteConfig> writeConfigs) throws Exception {
    final StringBuilder query = new StringBuilder();
    for (final BufferedWriteConfig writeConfig : writeConfigs.values()) {
      // create tables if not exist.
      createTable(writeConfig.getSchemaName(), writeConfig.getTableName());

      switch (writeConfig.getSyncMode()) {
        case FULL_REFRESH -> query.append(truncateTableQuery(writeConfig.getSchemaName(), writeConfig.getTableName()));
        case INCREMENTAL -> {}
        default -> throw new IllegalStateException("Unrecognized sync mode: " + writeConfig.getSyncMode());
      }
      // always copy data from tmp table into "main" table.
      query.append(
          insertIntoFromQuery(writeConfig.getSchemaName(), writeConfig.getTmpTableName(), writeConfig.getSchemaName(), writeConfig.getTableName()));
    }
    queryDatabaseInTransaction(query.toString());
  }

  protected String insertIntoFromQuery(String srcSchemaName, String srcTableName, String dstSchemaName, String dstTableName) {
    return String.format("INSERT INTO %s.%s SELECT * FROM %s.%s;\n", dstSchemaName, dstTableName, srcSchemaName, srcTableName);
  }

  protected String truncateTableQuery(String schemaName, String tableName) {
    return String.format("TRUNCATE TABLE %s.%s;\n", schemaName, tableName);
  }

  @Override
  public void dropTable(String schemaName, String tableName) throws Exception {
    queryDatabase(dropTableQuery(schemaName, tableName));
  }

  protected String dropTableQuery(String schemaName, String tableName) {
    return String.format("DROP TABLE IF EXISTS %s.%s;\n", schemaName, tableName);
  }

  protected abstract void connectDatabase(JsonNode config);

  protected abstract void queryDatabase(String query) throws Exception;

  protected abstract void queryDatabaseInTransaction(String queries) throws Exception;

  protected String getDefaultSchemaName(JsonNode config) {
    if (config.has("schema")) {
      return config.get("schema").asText();
    } else {
      return "public";
    }
  }

}
