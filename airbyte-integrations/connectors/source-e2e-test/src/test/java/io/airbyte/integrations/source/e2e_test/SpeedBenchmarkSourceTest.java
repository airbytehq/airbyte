/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.e2e_test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.integrations.source.e2e_test.SpeedBenchmarkConfig.SchemaType;
import io.airbyte.integrations.source.e2e_test.SpeedBenchmarkConfig.TerminationCondition;
import io.airbyte.protocol.models.v0.AirbyteCatalog;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.ConnectorSpecification;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.SyncMode;
import java.time.Instant;
import java.util.List;
import org.junit.jupiter.api.Test;

class SpeedBenchmarkSourceTest {

  public static final String CONFIG_JSON = """
                                           {
                                             "type": "BENCHMARK",
                                             "schema": "FIVE_STRING_COLUMNS",
                                             "terminationCondition": {
                                               "type": "MAX_RECORDS",
                                               "max": "100"
                                             }
                                           }
                                           """;
  public static final SpeedBenchmarkConfig CONFIG = new SpeedBenchmarkConfig(
      SchemaType.FIVE_STRING_COLUMNS,
      TerminationCondition.MAX_RECORDS,
      100);
  public static final String SCHEMA = """
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
  public static final AirbyteCatalog CATALOG = new AirbyteCatalog().withStreams(List.of(
      new AirbyteStream().withName("stream1").withJsonSchema(Jsons.deserialize(SCHEMA)).withSupportedSyncModes(List.of(SyncMode.FULL_REFRESH))));

  @Test
  void testSpec() throws Exception {
    final SpeedBenchmarkSource speedBenchmarkSource = new SpeedBenchmarkSource();

    assertEquals(Jsons.deserialize(MoreResources.readResource("spec.json"), ConnectorSpecification.class), speedBenchmarkSource.spec());
  }

  @Test
  void testCheck() {
    final SpeedBenchmarkSource speedBenchmarkSource = new SpeedBenchmarkSource();

    final AirbyteConnectionStatus expectedOutput = new AirbyteConnectionStatus()
        .withStatus(Status.SUCCEEDED)
        .withMessage("Source config: " + CONFIG);

    assertEquals(expectedOutput, speedBenchmarkSource.check(Jsons.deserialize(CONFIG_JSON)));
  }

  @Test
  void testDiscover() throws Exception {
    final SpeedBenchmarkSource speedBenchmarkSource = new SpeedBenchmarkSource();

    assertEquals(CATALOG, speedBenchmarkSource.discover(Jsons.deserialize(CONFIG_JSON)));
  }

  @Test
  @SuppressWarnings("try")
  void testSource() throws Exception {
    final SpeedBenchmarkSource speedBenchmarkSource = new SpeedBenchmarkSource();

    final ConfiguredAirbyteCatalog configuredCatalog = new ConfiguredAirbyteCatalog().withStreams(List.of(new ConfiguredAirbyteStream()
        .withStream(CATALOG.getStreams().get(0))
        .withSyncMode(SyncMode.FULL_REFRESH)
        .withDestinationSyncMode(DestinationSyncMode.APPEND)));

    final JsonNode config = Jsons.deserialize(CONFIG_JSON);
    ((ObjectNode) config.get("terminationCondition")).put("max", 3);

    try (final AutoCloseableIterator<AirbyteMessage> records = speedBenchmarkSource
        .read(config, configuredCatalog, Jsons.emptyObject())) {

      assertEquals(getExpectRecordMessage(1), records.next());
      assertEquals(getExpectRecordMessage(2), records.next());
      assertEquals(getExpectRecordMessage(3), records.next());
      assertFalse(records.hasNext());
    }
  }

  private static AirbyteMessage getExpectRecordMessage(final int recordNumber) {
    return new AirbyteMessage().withType(Type.RECORD).withRecord(new AirbyteRecordMessage()
        .withStream("stream1")
        .withEmittedAt(Instant.EPOCH.toEpochMilli())
        .withData(Jsons.jsonNode(ImmutableMap.of(
            "field1", "valuevaluevaluevaluevalue" + recordNumber,
            "field2", "valuevaluevaluevaluevalue" + recordNumber,
            "field3", "valuevaluevaluevaluevalue" + recordNumber,
            "field4", "valuevaluevaluevaluevalue" + recordNumber,
            "field5", "valuevaluevaluevaluevalue" + recordNumber))));
  }

}
