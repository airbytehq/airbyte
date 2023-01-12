/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.debezium.internals;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.debezium.CdcMetadataInjector;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.debezium.engine.ChangeEvent;
import java.sql.Timestamp;
import java.time.Instant;

public class DebeziumEventUtils {

  public static final String CDC_LSN = "_ab_cdc_lsn";
  public static final String CDC_UPDATED_AT = "_ab_cdc_updated_at";
  public static final String CDC_DELETED_AT = "_ab_cdc_deleted_at";

  public static AirbyteMessage toAirbyteMessage(final ChangeEvent<String, String> event,
                                                final CdcMetadataInjector cdcMetadataInjector,
                                                final Instant emittedAt) {
    final JsonNode debeziumRecord = Jsons.deserialize(event.value());
    final JsonNode before = debeziumRecord.get("before");
    final JsonNode after = debeziumRecord.get("after");
    final JsonNode source = debeziumRecord.get("source");

    final JsonNode data = formatDebeziumData(before, after, source, cdcMetadataInjector);
    final String schemaName = cdcMetadataInjector.namespace(source);
    final String streamName = source.get("table").asText();

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
    final ObjectNode base = (ObjectNode) (after.isNull() ? before : after);

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

}
