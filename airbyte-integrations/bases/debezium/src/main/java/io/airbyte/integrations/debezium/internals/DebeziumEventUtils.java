/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.debezium.internals;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.fasterxml.jackson.databind.node.TextNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.debezium.CdcMetadataInjector;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import java.sql.Timestamp;
import java.time.Instant;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DebeziumEventUtils {

  private static final Logger LOGGER = LoggerFactory.getLogger(DebeziumEventUtils.class);

  public static final String CDC_LSN = "_ab_cdc_lsn";
  public static final String CDC_UPDATED_AT = "_ab_cdc_updated_at";
  public static final String CDC_DELETED_AT = "_ab_cdc_deleted_at";

  public static AirbyteMessage toAirbyteMessage(final ChangeEventWithMetadata event,
                                                final CdcMetadataInjector cdcMetadataInjector,
                                                final Instant emittedAt) {
    final JsonNode debeziumRecord = event.eventValueAsJson();
    final JsonNode before = debeziumRecord.get("before");
    final JsonNode after = debeziumRecord.get("after");
    final JsonNode source = debeziumRecord.get("source");

    final JsonNode data = formatDebeziumData(before, after, source, cdcMetadataInjector);
    final String schemaName = cdcMetadataInjector.namespace(source);
    final String streamName = cdcMetadataInjector.name(source);

    final AirbyteRecordMessage airbyteRecordMessage = new AirbyteRecordMessage()
        .withStream(streamName)
        .withNamespace(schemaName)
        .withEmittedAt(emittedAt.toEpochMilli())
        .withData(data);

    return new AirbyteMessage()
        .withType(AirbyteMessage.Type.RECORD)
        .withRecord(airbyteRecordMessage);
  }

  // warning mutates input args.
  private static JsonNode formatDebeziumData(final JsonNode before,
                                             final JsonNode after,
                                             final JsonNode source,
                                             final CdcMetadataInjector cdcMetadataInjector) {
    final ObjectNode base = getBaseNode(after, before);

    final long transactionMillis = source.get("ts_ms").asLong();
    final String transactionTimestamp = new Timestamp(transactionMillis).toInstant().toString();

    base.put(CDC_UPDATED_AT, transactionTimestamp);
    cdcMetadataInjector.addMetaData(base, source);

    if (after.isNull()) {
      base.put(CDC_DELETED_AT, transactionTimestamp);
    } else {
      base.put(CDC_DELETED_AT, (String) null);
    }

    return base;
  }

  /**
   * Selects the proper node from the Debezium change event that represents the modified document.
   * <p />
   * <p />
   * Some data sources actually store their record data as JSON. This method handles nested JSON
   * documents in the change event to ensure that the changed document can be added to the
   * {@link AirbyteMessage} as a JSON document.
   *
   * @param after The state of the record after the change.
   * @param before The state of the record before the change.
   * @return The record that represents the change.
   */
  private static ObjectNode getBaseNode(final JsonNode after, final JsonNode before) {
    final JsonNode baseNode = after.isNull() ? before : after;
    return (ObjectNode) (baseNode instanceof TextNode ? Jsons.deserialize(baseNode.asText()) : baseNode);
  }

}
