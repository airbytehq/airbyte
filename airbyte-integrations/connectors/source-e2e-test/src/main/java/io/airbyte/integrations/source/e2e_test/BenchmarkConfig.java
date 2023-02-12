package io.airbyte.integrations.source.e2e_test;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.v0.AirbyteCatalog;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.SyncMode;
import java.util.List;

public record BenchmarkConfig(io.airbyte.integrations.source.e2e_test.BenchmarkConfig.SchemaType schemaType,
                              io.airbyte.integrations.source.e2e_test.BenchmarkConfig.TerminationCondition terminationCondition,
                              long maxBytes,
                              long maxRecords) {

  private static final String FIVE_STRING_COLUMNS_SCHEMA = """
          {
                "type": "object",
                "properties": {
                  "field1": {
                    "type": "string"
                  },
                  "field2": {
                    "type": "string"
                  },
                  "field3": {
                    "type": "string"
                  },
                  "field4": {
                    "type": "string"
                  },
                  "field5": {
                    "type": "string"
                  }
                }
              }
      """;

  private static final AirbyteCatalog FIVE_STRING_COLUMNS_CATALOG = new AirbyteCatalog().withStreams(List.of(
      new AirbyteStream().withName("stream1").withJsonSchema(Jsons.deserialize(FIVE_STRING_COLUMNS_SCHEMA)).withSupportedSyncModes(List.of(SyncMode.FULL_REFRESH))
  ));

  enum SchemaType {
    FIVE_STRING_COLUMNS(FIVE_STRING_COLUMNS_CATALOG);

    private final AirbyteCatalog catalog;

    SchemaType(final AirbyteCatalog catalog) {
      this.catalog = catalog;
    }

    public AirbyteCatalog getCatalog() {
      return catalog;
    }
  }

  enum TerminationCondition {
    MAX_RECORDS,
    MAX_BYTES
  }


  public static BenchmarkConfig parseFromConfig(final JsonNode config) {
    final TerminationCondition terminationCondition = TerminationCondition.valueOf(config.get("terminationCondition").get("type").asText());

    return new BenchmarkConfig(
        SchemaType.valueOf(config.get("schema").asText()),
        terminationCondition,
        terminationCondition == TerminationCondition.MAX_BYTES ? config.get("terminationCondition").get("max").asLong() : 0,
        terminationCondition == TerminationCondition.MAX_RECORDS ? config.get("terminationCondition").get("max").asLong() : 0
    );
  }

  public AirbyteCatalog getCatalog() {
    return schemaType.getCatalog();
  }
}
