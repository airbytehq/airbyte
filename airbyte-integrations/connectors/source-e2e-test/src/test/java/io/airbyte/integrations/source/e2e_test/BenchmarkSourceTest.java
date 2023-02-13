package io.airbyte.integrations.source.e2e_test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.integrations.source.e2e_test.BenchmarkConfig.SchemaType;
import io.airbyte.integrations.source.e2e_test.BenchmarkConfig.TerminationCondition;
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

class BenchmarkSourceTest {

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
  public static final BenchmarkConfig CONFIG = new BenchmarkConfig(
      SchemaType.FIVE_STRING_COLUMNS,
      TerminationCondition.MAX_RECORDS,
      0,
      100
  );
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
      new AirbyteStream().withName("stream1").withJsonSchema(Jsons.deserialize(SCHEMA)).withSupportedSyncModes(List.of(SyncMode.FULL_REFRESH))
  ));

  @Test
  void testSpec() throws Exception {
    final BenchmarkSource benchmarkSource = new BenchmarkSource();

    assertEquals(Jsons.deserialize(MoreResources.readResource("spec.json"), ConnectorSpecification.class), benchmarkSource.spec());
  }


  @Test
  void testCheck() throws Exception {
    final BenchmarkSource benchmarkSource = new BenchmarkSource();

    final AirbyteConnectionStatus expectedOutput = new AirbyteConnectionStatus()
        .withStatus(Status.SUCCEEDED)
        .withMessage("Source config: " + CONFIG);

    assertEquals(expectedOutput, benchmarkSource.check(Jsons.deserialize(CONFIG_JSON)));
  }

  @Test
  void testDiscover() throws Exception {
    final BenchmarkSource benchmarkSource = new BenchmarkSource();

    assertEquals(CATALOG, benchmarkSource.discover(Jsons.deserialize(CONFIG_JSON)));
  }

  @Test
  void testSource() throws Exception {
    final BenchmarkSource benchmarkSource = new BenchmarkSource();

    final ConfiguredAirbyteCatalog configuredCatalog = new ConfiguredAirbyteCatalog().withStreams(List.of(new ConfiguredAirbyteStream()
        .withStream(CATALOG.getStreams().get(0))
        .withSyncMode(SyncMode.FULL_REFRESH)
        .withDestinationSyncMode(DestinationSyncMode.APPEND)
    ));

    final JsonNode config = Jsons.deserialize(CONFIG_JSON);
    ((ObjectNode) config.get("terminationCondition")).put("max", 3);

    try (final AutoCloseableIterator<AirbyteMessage> records = benchmarkSource
        .read(config, configuredCatalog, Jsons.emptyObject())) {

      assertEquals(getExpectRecordMessage(1), records.next());
      assertEquals(getExpectRecordMessage(2), records.next());
      assertEquals(getExpectRecordMessage(3), records.next());
      assertFalse(records.hasNext());
    }
  }

  @Test
  void testSource2() throws Exception {
    final BenchmarkSource benchmarkSource = new BenchmarkSource();

    final ConfiguredAirbyteCatalog configuredCatalog = new ConfiguredAirbyteCatalog().withStreams(List.of(new ConfiguredAirbyteStream()
        .withStream(CATALOG.getStreams().get(0))
        .withSyncMode(SyncMode.FULL_REFRESH)
        .withDestinationSyncMode(DestinationSyncMode.APPEND)
    ));

    final JsonNode config = Jsons.deserialize(CONFIG_JSON);
    ((ObjectNode) config.get("terminationCondition")).put("max", 3);

    try (final AutoCloseableIterator<AirbyteMessage> records = benchmarkSource
        .read(config, configuredCatalog, Jsons.emptyObject())) {

      final AirbyteMessage record1 = records.next();
      final AirbyteMessage record2 = records.next();
      final AirbyteMessage record3 = records.next();
      assertFalse(records.hasNext());

      assertEquals(getExpectRecordMessage(1), record1);
      assertEquals(getExpectRecordMessage(2), record2);
      assertEquals(getExpectRecordMessage(3), record3);
    }
  }

  private static AirbyteMessage getExpectRecordMessage(final int recordNumber) {
    return new AirbyteMessage().withType(Type.RECORD).withRecord(new AirbyteRecordMessage()
        .withStream("stream1")
        .withEmittedAt(Instant.EPOCH.toEpochMilli())
        .withData(Jsons.jsonNode(ImmutableMap.of(
        "field1", "valuevaluevaluevaluevalue1",
        "field2", "valuevaluevaluevaluevalue1",
        "field3", "valuevaluevaluevaluevalue1",
        "field4", "valuevaluevaluevaluevalue1",
        "field5", "valuevaluevaluevaluevalue1"
    ))));
  }
}
