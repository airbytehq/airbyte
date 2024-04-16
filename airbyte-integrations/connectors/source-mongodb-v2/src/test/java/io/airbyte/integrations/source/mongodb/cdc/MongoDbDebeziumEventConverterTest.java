/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.cdc;

import static io.airbyte.integrations.source.mongodb.cdc.MongoDbCdcEventUtils.ID_FIELD;
import static io.airbyte.integrations.source.mongodb.cdc.MongoDbCdcEventUtils.OBJECT_ID_FIELD;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.cdk.integrations.debezium.CdcMetadataInjector;
import io.airbyte.cdk.integrations.debezium.internals.ChangeEventWithMetadata;
import io.airbyte.cdk.integrations.debezium.internals.RelationalDbDebeziumEventConverter;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.debezium.engine.ChangeEvent;
import java.io.IOException;
import java.time.Instant;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.Test;

class MongoDbDebeziumEventConverterTest {

  @Test
  void testConvertRelationalDbChangeEvent() throws IOException {
    final String stream = "names";
    final Instant emittedAt = Instant.now();
    final CdcMetadataInjector<Long> cdcMetadataInjector = new DummyMetadataInjector();
    final ChangeEventWithMetadata insertChangeEvent = mockChangeEvent("insert_change_event.json", "");
    final ChangeEventWithMetadata updateChangeEvent = mockChangeEvent("update_change_event.json", "");
    final ChangeEventWithMetadata deleteChangeEvent = mockChangeEvent("delete_change_event.json", "");
    final var eventConverter = new RelationalDbDebeziumEventConverter(cdcMetadataInjector, emittedAt);

    final AirbyteMessage actualInsert = eventConverter.toAirbyteMessage(insertChangeEvent);
    final AirbyteMessage actualUpdate = eventConverter.toAirbyteMessage(updateChangeEvent);
    final AirbyteMessage actualDelete = eventConverter.toAirbyteMessage(deleteChangeEvent);

    final AirbyteMessage expectedInsert = createAirbyteMessage(stream, emittedAt, "insert_message.json");
    final AirbyteMessage expectedUpdate = createAirbyteMessage(stream, emittedAt, "update_message.json");
    final AirbyteMessage expectedDelete = createAirbyteMessage(stream, emittedAt, "delete_message.json");

    deepCompare(expectedInsert, actualInsert);
    deepCompare(expectedUpdate, actualUpdate);
    deepCompare(expectedDelete, actualDelete);
  }

  @Test
  void testConvertMongoDbChangeEvent() throws IOException {
    final String objectId = "64f24244f95155351c4185b1";
    final String stream = "names";
    final Instant emittedAt = Instant.now();
    final CdcMetadataInjector<Long> cdcMetadataInjector = new DummyMetadataInjector();
    final ChangeEventWithMetadata insertChangeEvent = mockChangeEvent("mongodb/change_event_insert.json", "");
    final ChangeEventWithMetadata updateChangeEvent = mockChangeEvent("mongodb/change_event_update.json", "");
    final ChangeEventWithMetadata deleteChangeEvent = mockChangeEvent("mongodb/change_event_delete.json", "");
    final ChangeEventWithMetadata deleteChangeEventNoBefore = mockChangeEvent("mongodb/change_event_delete_no_before.json",
        "{\\\"" + OBJECT_ID_FIELD + "\\\": \\\"" + objectId + "\\\"}");

    final AirbyteMessage expectedInsert = createAirbyteMessage(stream, emittedAt, "mongodb/insert_airbyte_message.json");
    final AirbyteMessage expectedUpdate = createAirbyteMessage(stream, emittedAt, "mongodb/update_airbyte_message.json");
    final AirbyteMessage expectedDelete = createAirbyteMessage(stream, emittedAt, "mongodb/delete_airbyte_message.json");
    final AirbyteMessage expectedDeleteNoBefore = createAirbyteMessage(stream, emittedAt, "mongodb/delete_no_before_airbyte_message.json");

    final AirbyteMessage actualInsert = new MongoDbDebeziumEventConverter(
        cdcMetadataInjector, buildFromAirbyteMessage(expectedInsert), emittedAt, Jsons.emptyObject())
            .toAirbyteMessage(insertChangeEvent);
    final AirbyteMessage actualUpdate = new MongoDbDebeziumEventConverter(
        cdcMetadataInjector, buildFromAirbyteMessage(expectedUpdate), emittedAt, Jsons.emptyObject())
            .toAirbyteMessage(updateChangeEvent);
    final AirbyteMessage actualDelete = new MongoDbDebeziumEventConverter(
        cdcMetadataInjector, buildFromAirbyteMessage(expectedDelete), emittedAt, Jsons.emptyObject())
            .toAirbyteMessage(deleteChangeEvent);
    final AirbyteMessage actualDeleteNoBefore = new MongoDbDebeziumEventConverter(
        cdcMetadataInjector, buildFromAirbyteMessage(expectedDeleteNoBefore), emittedAt, Jsons.emptyObject())
            .toAirbyteMessage(deleteChangeEventNoBefore);

    deepCompare(expectedInsert, actualInsert);
    deepCompare(expectedUpdate, actualUpdate);
    deepCompare(expectedDelete, actualDelete);
    deepCompare(expectedDeleteNoBefore, actualDeleteNoBefore);
  }

  @Test
  void testConvertMongoDbChangeEventNoSchema() throws IOException {
    final String objectId = "64f24244f95155351c4185b1";
    final String stream = "names";
    final Instant emittedAt = Instant.now();
    final CdcMetadataInjector<Long> cdcMetadataInjector = new DummyMetadataInjector();
    final ChangeEventWithMetadata insertChangeEvent = mockChangeEvent("mongodb/change_event_insert.json", "");
    final ChangeEventWithMetadata updateChangeEvent = mockChangeEvent("mongodb/change_event_update.json", "");
    final ChangeEventWithMetadata deleteChangeEvent = mockChangeEvent("mongodb/change_event_delete.json", "");
    final ChangeEventWithMetadata deleteChangeEventNoBefore = mockChangeEvent("mongodb/change_event_delete_no_before.json",
        "{\\\"" + OBJECT_ID_FIELD + "\\\": \\\"" + objectId + "\\\"}");

    final AirbyteMessage expectedInsert = createAirbyteMessage(stream, emittedAt, "mongodb/insert_airbyte_message_no_schema.json");
    final AirbyteMessage expectedUpdate = createAirbyteMessage(stream, emittedAt, "mongodb/update_airbyte_message_no_schema.json");
    final AirbyteMessage expectedDelete = createAirbyteMessage(stream, emittedAt, "mongodb/delete_airbyte_message_no_schema.json");
    final AirbyteMessage expectedDeleteNoBefore = createAirbyteMessage(stream, emittedAt, "mongodb/delete_no_before_airbyte_message_no_schema.json");

    final ConfiguredAirbyteCatalog insertConfiguredAirbyteCatalog = buildFromAirbyteMessage(expectedInsert);
    final ConfiguredAirbyteCatalog updateConfiguredAirbyteCatalog = buildFromAirbyteMessage(expectedUpdate);
    final ConfiguredAirbyteCatalog deleteConfiguredAirbyteCatalog = buildFromAirbyteMessage(expectedDelete);
    final ConfiguredAirbyteCatalog deleteNoBeforeConfiguredAirbyteCatalog = buildFromAirbyteMessage(expectedDeleteNoBefore);

    final JsonNode noSchemaConfig =
        Jsons.jsonNode(Map.of(MongoDbDebeziumConstants.Configuration.SCHEMA_ENFORCED_CONFIGURATION_KEY, false));
    final AirbyteMessage actualInsert = new MongoDbDebeziumEventConverter(
        cdcMetadataInjector, buildFromAirbyteMessage(expectedInsert), emittedAt, noSchemaConfig)
            .toAirbyteMessage(insertChangeEvent);
    final AirbyteMessage actualUpdate = new MongoDbDebeziumEventConverter(
        cdcMetadataInjector, buildFromAirbyteMessage(expectedUpdate), emittedAt, noSchemaConfig)
            .toAirbyteMessage(updateChangeEvent);
    final AirbyteMessage actualDelete = new MongoDbDebeziumEventConverter(
        cdcMetadataInjector, buildFromAirbyteMessage(expectedDelete), emittedAt, noSchemaConfig)
            .toAirbyteMessage(deleteChangeEvent);
    final AirbyteMessage actualDeleteNoBefore = new MongoDbDebeziumEventConverter(
        cdcMetadataInjector, buildFromAirbyteMessage(expectedDeleteNoBefore), emittedAt, noSchemaConfig)
            .toAirbyteMessage(deleteChangeEventNoBefore);

    deepCompare(expectedInsert, actualInsert);
    deepCompare(expectedUpdate, actualUpdate);
    deepCompare(expectedDelete, actualDelete);
    deepCompare(expectedDeleteNoBefore, actualDeleteNoBefore);
  }

  @Test
  void testConvertMongoDbChangeEventUnsupportedOperation() throws IOException {
    final Instant emittedAt = Instant.now();
    final CdcMetadataInjector<Long> cdcMetadataInjector = new DummyMetadataInjector();
    final ChangeEventWithMetadata unsupportedOperationEvent = mockChangeEvent("mongodb/change_event_unsupported.json", "");
    final ConfiguredAirbyteCatalog configuredAirbyteCatalog = mock(ConfiguredAirbyteCatalog.class);
    final var eventConverter = new MongoDbDebeziumEventConverter(cdcMetadataInjector, configuredAirbyteCatalog, emittedAt, Jsons.emptyObject());

    assertThrows(IllegalArgumentException.class, () -> eventConverter.toAirbyteMessage(unsupportedOperationEvent));
  }

  private ConfiguredAirbyteCatalog buildFromAirbyteMessage(final AirbyteMessage airbyteMessage) {
    final ConfiguredAirbyteCatalog configuredAirbyteCatalog = new ConfiguredAirbyteCatalog();
    final ConfiguredAirbyteStream configuredAirbyteStream = new ConfiguredAirbyteStream();
    final AirbyteStream airbyteStream = new AirbyteStream();
    airbyteStream.setName(airbyteMessage.getRecord().getStream());
    airbyteStream.setNamespace(airbyteMessage.getRecord().getNamespace());
    airbyteStream.setJsonSchema(Jsons.jsonNode(Map.of("properties", airbyteMessage.getRecord().getData())));
    configuredAirbyteStream.setStream(airbyteStream);
    configuredAirbyteCatalog.setStreams(List.of(configuredAirbyteStream));
    return configuredAirbyteCatalog;
  }

  private static ChangeEventWithMetadata mockChangeEvent(final String resourceName, final String idValue) throws IOException {
    final ChangeEvent<String, String> mocked = mock(ChangeEvent.class);
    final String resource = MoreResources.readResource(resourceName);
    final String key = "{\"" + ID_FIELD + "\":\"" + idValue + "\"}";
    when(mocked.key()).thenReturn(key);
    when(mocked.value()).thenReturn(resource);

    return new ChangeEventWithMetadata(mocked);
  }

  private static AirbyteMessage createAirbyteMessage(final String stream, final Instant emittedAt, final String resourceName) throws IOException {
    final String data = MoreResources.readResource(resourceName);

    final AirbyteRecordMessage recordMessage = new AirbyteRecordMessage()
        .withStream(stream)
        .withNamespace("public")
        .withData(Jsons.deserialize(data))
        .withEmittedAt(emittedAt.toEpochMilli());

    return new AirbyteMessage()
        .withType(AirbyteMessage.Type.RECORD)
        .withRecord(recordMessage);
  }

  private static void deepCompare(final Object expected, final Object actual) {
    assertEquals(Jsons.deserialize(Jsons.serialize(expected)), Jsons.deserialize(Jsons.serialize(actual)));
  }

  public static class DummyMetadataInjector implements CdcMetadataInjector<Long> {

    @Override
    public void addMetaData(final ObjectNode event, final JsonNode source) {
      if (source.has("lsn")) {
        final long lsn = source.get("lsn").asLong();
        event.put("_ab_cdc_lsn", lsn);
      }
    }

    @Override
    public String namespace(final JsonNode source) {
      return source.has("schema") ? source.get("schema").asText() : source.get("db").asText();
    }

    @Override
    public String name(final JsonNode source) {
      return source.has("table") ? source.get("table").asText() : source.get("collection").asText();
    }

  }

}
