/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.debezium.internals;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.debezium.CdcMetadataInjector;
import io.airbyte.integrations.debezium.internals.mongodb.MongoDbCdcEventUtils;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import java.time.Instant;

public class DebeziumEventUtils {

  public static final String CDC_LSN = "_ab_cdc_lsn";
  public static final String CDC_UPDATED_AT = "_ab_cdc_updated_at";
  public static final String CDC_DELETED_AT = "_ab_cdc_deleted_at";

  @VisibleForTesting
  static final String AFTER_EVENT = "after";
  @VisibleForTesting
  static final String BEFORE_EVENT = "before";
  @VisibleForTesting
  static final String OPERATION_FIELD = "op";
  @VisibleForTesting
  static final String SOURCE_EVENT = "source";

  public static AirbyteMessage toAirbyteMessage(final ChangeEventWithMetadata event,
                                                final CdcMetadataInjector cdcMetadataInjector,
                                                final Instant emittedAt,
                                                final DebeziumPropertiesManager.DebeziumConnectorType debeziumConnectorType) {
    return switch (debeziumConnectorType) {
      case MONGODB -> formatMongoDbEvent(event, cdcMetadataInjector, emittedAt);
      case RELATIONALDB -> formatRelationalDbEvent(event, cdcMetadataInjector, emittedAt);
    };
  }

  private static AirbyteMessage buildAirbyteMessage(final JsonNode source,
                                                    final CdcMetadataInjector cdcMetadataInjector,
                                                    final Instant emittedAt,
                                                    final JsonNode data) {
    final String streamNamespace = cdcMetadataInjector.namespace(source);
    final String streamName = cdcMetadataInjector.name(source);

    final AirbyteRecordMessage airbyteRecordMessage = new AirbyteRecordMessage()
        .withStream(streamName)
        .withNamespace(streamNamespace)
        .withEmittedAt(emittedAt.toEpochMilli())
        .withData(data);

    return new AirbyteMessage()
        .withType(AirbyteMessage.Type.RECORD)
        .withRecord(airbyteRecordMessage);
  }

  private static AirbyteMessage formatMongoDbEvent(final ChangeEventWithMetadata event,
                                                   final CdcMetadataInjector cdcMetadataInjector,
                                                   final Instant emittedAt) {
    final JsonNode debeziumEventKey = event.eventKeyAsJson();
    final JsonNode debeziumEvent = event.eventValueAsJson();
    final JsonNode before = debeziumEvent.get(BEFORE_EVENT);
    final JsonNode after = debeziumEvent.get(AFTER_EVENT);
    final JsonNode source = debeziumEvent.get(SOURCE_EVENT);
    final String operation = debeziumEvent.get(OPERATION_FIELD).asText();

    /*
     * Delete events need to be handled separately from other CrUD events, as depending on the version
     * of the MongoDB server, the contents Debezium event data will be different. See
     * #formatMongoDbDeleteDebeziumData() for more details.
     */
    final JsonNode data = switch (operation) {
      case "c", "i", "u" -> formatMongoDbDebeziumData(before, after, source, cdcMetadataInjector);
      case "d" -> formatMongoDbDeleteDebeziumData(before, debeziumEventKey, source, cdcMetadataInjector);
      default -> throw new IllegalArgumentException("Unsupported MongoDB change event operation '" + operation + "'.");
    };

    return buildAirbyteMessage(source, cdcMetadataInjector, emittedAt, data);
  }

  private static AirbyteMessage formatRelationalDbEvent(final ChangeEventWithMetadata event,
                                                        final CdcMetadataInjector cdcMetadataInjector,
                                                        final Instant emittedAt) {
    final JsonNode debeziumEvent = event.eventValueAsJson();
    final JsonNode before = debeziumEvent.get(BEFORE_EVENT);
    final JsonNode after = debeziumEvent.get(AFTER_EVENT);
    final JsonNode source = debeziumEvent.get(SOURCE_EVENT);

    final JsonNode data = formatRelationalDbDebeziumData(before, after, source, cdcMetadataInjector);
    return buildAirbyteMessage(source, cdcMetadataInjector, emittedAt, data);
  }

  private static JsonNode formatMongoDbDebeziumData(final JsonNode before,
                                                    final JsonNode after,
                                                    final JsonNode source,
                                                    final CdcMetadataInjector cdcMetadataInjector) {
    final String eventJson = (after.isNull() ? before : after).asText();
    return addCdcMetadata(MongoDbCdcEventUtils.transformDataTypes(eventJson), source, cdcMetadataInjector, false);
  }

  private static JsonNode formatMongoDbDeleteDebeziumData(final JsonNode before,
                                                          final JsonNode debeziumEventKey,
                                                          final JsonNode source,
                                                          final CdcMetadataInjector cdcMetadataInjector) {
    String eventJson;

    /*
     * The change events produced by MongoDB differ based on the server version. For version BEFORE 6.x,
     * the event does not contain the before document. Therefore, the only data that can be extracted is
     * the object ID of the deleted document, which is stored in the event key. Otherwise, if the server
     * is version 6.+ AND the pre-image support has been enabled on the collection, we can use the
     * "before" document from the event to represent the deleted document.
     *
     * See
     * https://www.mongodb.com/docs/manual/reference/change-events/delete/#document-pre--and-post-images
     * for more details.
     */
    if (!before.isNull()) {
      eventJson = before.asText();
    } else {
      eventJson = MongoDbCdcEventUtils.generateObjectIdDocument(debeziumEventKey);
    }

    return addCdcMetadata(MongoDbCdcEventUtils.transformDataTypes(eventJson), source, cdcMetadataInjector, true);
  }

  private static JsonNode formatRelationalDbDebeziumData(final JsonNode before,
                                                         final JsonNode after,
                                                         final JsonNode source,
                                                         final CdcMetadataInjector cdcMetadataInjector) {
    final ObjectNode baseNode = (ObjectNode) (after.isNull() ? before : after);
    return addCdcMetadata(baseNode, source, cdcMetadataInjector, after.isNull());

  }

  private static JsonNode addCdcMetadata(final ObjectNode baseNode,
                                         final JsonNode source,
                                         final CdcMetadataInjector cdcMetadataInjector,
                                         boolean isDelete) {

    final long transactionMillis = source.get("ts_ms").asLong();
    final String transactionTimestamp = Instant.ofEpochMilli(transactionMillis).toString();

    baseNode.put(CDC_UPDATED_AT, transactionTimestamp);
    cdcMetadataInjector.addMetaData(baseNode, source);

    if (isDelete) {
      baseNode.put(CDC_DELETED_AT, transactionTimestamp);
    } else {
      baseNode.put(CDC_DELETED_AT, (String) null);
    }

    return baseNode;
  }

}
