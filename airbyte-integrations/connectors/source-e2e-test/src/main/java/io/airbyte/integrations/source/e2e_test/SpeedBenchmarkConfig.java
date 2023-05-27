/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.e2e_test;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.v0.AirbyteCatalog;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.SyncMode;

import java.util.ArrayList;
import java.util.List;

public record SpeedBenchmarkConfig(SpeedBenchmarkConfig.SchemaType schemaType,
                                   SpeedBenchmarkConfig.TerminationCondition terminationCondition,
                                   long maxRecords,
                                   int streamNumber) {

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

  private static final AirbyteStream BASE_STREAM = new AirbyteStream()
      .withJsonSchema(Jsons.deserialize(FIVE_STRING_COLUMNS_SCHEMA))
      .withSupportedSyncModes(List.of(SyncMode.FULL_REFRESH));

  private static final String STREAM_PREFIX = "stream";

  private static final AirbyteCatalog FIVE_STRING_COLUMNS_CATALOG = new AirbyteCatalog().withStreams(List.of(
      new AirbyteStream().withName("stream1").withJsonSchema(Jsons.deserialize(FIVE_STRING_COLUMNS_SCHEMA))
          .withSupportedSyncModes(List.of(SyncMode.FULL_REFRESH))));

  enum SchemaType {

    FIVE_STRING_COLUMNS(FIVE_STRING_COLUMNS_CATALOG);

    private final AirbyteCatalog catalog;

    SchemaType(final AirbyteCatalog catalog) {
      this.catalog = catalog;
    }

    public AirbyteCatalog getCatalog(final int streamNumber) {
      return generateCatalog(streamNumber);
    }

    private AirbyteCatalog generateCatalog(final int streamNumber) {
      final List<AirbyteStream> streams = new ArrayList<>();
      for (int i = 1; i <= streamNumber; i++) {
        streams.add(Jsons.clone(BASE_STREAM).withName(STREAM_PREFIX + i));
      }
      return new AirbyteCatalog().withStreams(streams);
    }

  }

  enum TerminationCondition {
    MAX_RECORDS
  }

  public static SpeedBenchmarkConfig parseFromConfig(final JsonNode config) {
    final TerminationCondition terminationCondition = TerminationCondition.valueOf(config.get("terminationCondition").get("type").asText());

    return new SpeedBenchmarkConfig(
        SchemaType.valueOf(config.get("schema").asText()),
        terminationCondition,
        terminationCondition == TerminationCondition.MAX_RECORDS ? config.get("terminationCondition").get("max").asLong() : 0,
        config.has("stream_number") ? config.get("stream_number").asInt() : 1);
  }

  public AirbyteCatalog getCatalog() {
    return schemaType.getCatalog(streamNumber);
  }

}
