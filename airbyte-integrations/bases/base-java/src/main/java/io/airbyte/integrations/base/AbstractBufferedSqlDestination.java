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
import io.airbyte.protocol.models.SyncMode;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

/**
 * This abstract destination subclass adds some on-disk buffering functionalities to each stream and expose the necessary abstractions for write operations
 * required to interact with a SQL-type of destination
 */
public abstract class AbstractBufferedSqlDestination extends AbstractDestination implements BufferedWriteOperations {

  @Override
  protected WriteConfig configureStream(String streamName, String schemaName, String tableName, String tmpTableName, SyncMode syncMode) throws IOException {
    return new BufferedWriteConfig(streamName, schemaName, tableName, tmpTableName, syncMode);
  }

  @Override
  protected DestinationConsumer<AirbyteMessage> createConsumer(Map<String, WriteConfig> writeConfigs, ConfiguredAirbyteCatalog catalog) {
    Map<String, BufferedWriteConfig> bufferedConfigs = new HashMap<>();
    for (Map.Entry<String, WriteConfig> entry : writeConfigs.entrySet()) {
      if (entry.getValue() instanceof BufferedWriteConfig){
        bufferedConfigs.put(entry.getKey(), (BufferedWriteConfig) entry.getValue());
      }
    }
    return new BufferedRecordConsumer(this, bufferedConfigs, catalog);
  }

  @Override
  protected String getDefaultSchemaName(JsonNode config) {
    if (config.has("schema")) {
      return config.get("schema").asText();
    } else {
      return "public";
    }
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

  protected abstract void queryDatabase(String query) throws Exception;

  protected abstract void queryDatabaseInTransaction(String queries) throws Exception;

}
