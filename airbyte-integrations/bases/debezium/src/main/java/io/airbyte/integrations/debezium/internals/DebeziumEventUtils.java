/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.debezium.internals;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.debezium.CdcMetadataInjector;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import java.sql.Timestamp;
import java.time.Instant;
import java.util.Map;

public class DebeziumEventUtils {

  public static final String CDC_LSN = "_ab_cdc_lsn";
  public static final String CDC_UPDATED_AT = "_ab_cdc_updated_at";
  public static final String CDC_DELETED_AT = "_ab_cdc_deleted_at";

  @VisibleForTesting
  static final String AFTER_EVENT = "after";
  @VisibleForTesting
  static final String BEFORE_EVENT = "before";
  @VisibleForTesting
  static final String DOCUMENT_OBJECT_ID_FIELD = "_id";
  @VisibleForTesting
  static final String ID_FIELD = "id";
  @VisibleForTesting
  static final String OBJECT_ID_FIELD = "$oid";
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
    /*
     * Debezium MongoDB change events contain the document as an escaped JSON string. Therefore, it
     * needs to be turned back into a JSON object for inclusion in the Airybte message.
     */
    final ObjectNode baseNode = (ObjectNode) Jsons.deserialize((after.isNull() ? before : after).asText());
    return addCdcMetadata(normalizeObjectId(baseNode), source, cdcMetadataInjector, false);
  }

  private static JsonNode formatMongoDbDeleteDebeziumData(final JsonNode before,
                                                          final JsonNode debeziumEventKey,
                                                          final JsonNode source,
                                                          final CdcMetadataInjector cdcMetadataInjector) {
    ObjectNode baseNode;

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
      baseNode = normalizeObjectId((ObjectNode) Jsons.deserialize(before.asText()));
    } else {
      final String objectId = Jsons.deserialize(debeziumEventKey.get(ID_FIELD).asText()).get(OBJECT_ID_FIELD).asText();
      baseNode = (ObjectNode) Jsons.jsonNode(Map.of(DOCUMENT_OBJECT_ID_FIELD, objectId));
    }

    return addCdcMetadata(baseNode, source, cdcMetadataInjector, true);
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

  /**
   * Normalizes the document's object ID value stored in the change event to match the raw data
   * produced by the initial snapshot.
   * <p/>
   * <p/>
   * We need to unpack the object ID from the event data in order for it to match up with the data
   * produced by the initial snapshot. The event contains the object ID in a nested object:
   * <p/>
   * <p/>
   * <code>
   * {\"_id\": {\"$oid\": \"64f24244f95155351c4185b1\"}, ...}
   * </code>
   * <p/>
   * <p/>
   * In order to match the data produced by the initial snapshot, this must be translated into:
   * <p/>
   * <p/>
   * <code>
   * {\"_id\": \"64f24244f95155351c4185b1\", ...}
   * </code>
   *
   * @param data The {@link ObjectNode} that contains the record data extracted from the change event.
   * @return The updated record data with the document object ID normalized.
   */
  private static ObjectNode normalizeObjectId(final ObjectNode data) {
    if (data.has(DOCUMENT_OBJECT_ID_FIELD) && data.get(DOCUMENT_OBJECT_ID_FIELD).has(OBJECT_ID_FIELD)) {
      final String objectId = data.get(DOCUMENT_OBJECT_ID_FIELD).get(OBJECT_ID_FIELD).asText();
      data.put(DOCUMENT_OBJECT_ID_FIELD, objectId);
    }
    return data;
  }

}
