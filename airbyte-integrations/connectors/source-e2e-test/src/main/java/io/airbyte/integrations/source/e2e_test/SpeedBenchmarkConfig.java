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
                                   int streamCount,
                                   int threadCount) {

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

  private static final AirbyteStream FIVE_STRING_COLUMNS_STREAM = new AirbyteStream()
      .withJsonSchema(Jsons.deserialize(FIVE_STRING_COLUMNS_SCHEMA))
      .withSupportedSyncModes(List.of(SyncMode.FULL_REFRESH));

  private static final String STREAM_PREFIX = "stream";

  /**
   * Enum lets you pick which stream schema you want. Then when getting the catalog, pass in the
   * number of streams with that schema that you want
   */
  enum SchemaType {

    FIVE_STRING_COLUMNS(FIVE_STRING_COLUMNS_STREAM);

    private final AirbyteStream baseStream;

    SchemaType(final AirbyteStream baseStream) {
      this.baseStream = baseStream;
    }

    public AirbyteCatalog getCatalog(final int streamCount) {
      return generateCatalog(streamCount);
    }

    private AirbyteCatalog generateCatalog(final int streamCount) {
      final List<AirbyteStream> streams = new ArrayList<>();
      for (int i = 1; i <= streamCount; i++) {
        streams.add(Jsons.clone(baseStream).withName(STREAM_PREFIX + i));
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
        config.has("stream_count") ? config.get("stream_count").asInt() : 1,
        config.has("thread_count") ? config.get("thread_count").asInt() : 1);
  }

  public AirbyteCatalog getCatalog() {
    return schemaType.getCatalog(streamCount);
  }

}
