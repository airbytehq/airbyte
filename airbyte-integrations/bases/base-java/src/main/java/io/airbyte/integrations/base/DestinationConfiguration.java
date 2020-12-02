package io.airbyte.integrations.base;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.text.Names;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import java.util.HashMap;
import java.util.Map;

public class DestinationConfiguration {

  private final SQLNamingResolvable namingResolver;

  public DestinationConfiguration(SQLNamingResolvable namingResolver) {
    this.namingResolver = namingResolver;
  }

  public Map<String, DestinationWriteContext> getDestinationWriteContext(JsonNode config, ConfiguredAirbyteCatalog catalog) {
    Map<String, DestinationWriteContext> result = new HashMap<>();
    for (final ConfiguredAirbyteStream stream : catalog.getStreams()) {
      final String streamName = stream.getStream().getName();
      final String schemaName = getNamingResolver().getSchemaName(config, stream);
      final String tableName = Names.concatNames(getNamingResolver().getTableName(streamName),"_raw");
      result.put(streamName, new DestinationWriteContext(schemaName, tableName, stream.getSyncMode()));
    }
    return result;
  }

  public SQLNamingResolvable getNamingResolver() {
    return namingResolver;
  }
}
