package io.airbyte.integrations.base;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.lang.CloseableQueue;
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

public abstract class AbstractDestination implements Destination, DestinationConsumerCallback {

  public DestinationConsumer<AirbyteMessage> write(JsonNode config, ConfiguredAirbyteCatalog catalog) throws Exception {
    connectDatabase(config);
    final Map<String, WriteConfig> writeBuffers = new HashMap<>();
    final Set<String> schemaSet = new HashSet<>();
    // create tmp tables if not exist
    for (final ConfiguredAirbyteStream stream : catalog.getStreams()) {
      final String streamName = stream.getStream().getName();
      final String schemaName = getNamingResolver().getIdentifier(getDefaultSchemaName(config));
      final String tableName = getNamingResolver().getRawTableName(streamName);
      final String tmpTableName = getNamingResolver().getTmpTableName(streamName);
      if (!schemaSet.contains(schemaName)) {
        queryDatabase(createSchemaQuery(schemaName));
        schemaSet.add(schemaName);
      }
      queryDatabase(createRawTableQuery(schemaName, tmpTableName));

      final Path queueRoot = Files.createTempDirectory("queues");
      final BigQueue writeBuffer = new BigQueue(queueRoot.resolve(streamName), streamName);
      final SyncMode syncMode = stream.getSyncMode() == null ? SyncMode.FULL_REFRESH : stream.getSyncMode();
      writeBuffers.put(streamName, new WriteConfig(schemaName, tableName, tmpTableName, writeBuffer, syncMode));
    }
    // write to tmp tables
    // if success copy delete main table if exists. rename tmp tables to real tables.
    return new RecordConsumer(this, writeBuffers, catalog);
  }

  protected abstract void connectDatabase(JsonNode config);

  protected abstract void queryDatabase(String query);

  protected String getDefaultSchemaName(JsonNode config) {
    if (config.has("schema")) {
      return config.get("schema").asText();
    } else {
      return "public";
    }
  }

  protected String createSchemaQuery(String schemaName) {
    return String.format("CREATE SCHEMA IF NOT EXISTS %s;\n", schemaName);
  }

  protected abstract String createRawTableQuery(String schemaName, String streamName);

  public abstract void writeQuery(int batchSize, CloseableQueue<byte[]> writeBuffer, String schemaName, String tmpTableName);
  public abstract void commitRawTables(Map<String, WriteConfig> writeConfigs);
  public abstract void cleanupTmpTables(Map<String, WriteConfig> writeConfigs);
}
