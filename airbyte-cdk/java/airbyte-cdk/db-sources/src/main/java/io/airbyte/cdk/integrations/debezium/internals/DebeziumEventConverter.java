/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.debezium.internals;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.cdk.integrations.debezium.CdcMetadataInjector;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import java.time.Instant;

public interface DebeziumEventConverter {

  String CDC_LSN = "_ab_cdc_lsn";
  String CDC_UPDATED_AT = "_ab_cdc_updated_at";
  String CDC_DELETED_AT = "_ab_cdc_deleted_at";
  String AFTER_EVENT = "after";
  String BEFORE_EVENT = "before";
  String OPERATION_FIELD = "op";
  String SOURCE_EVENT = "source";

  static AirbyteMessage buildAirbyteMessage(
                                            final JsonNode source,
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

  static JsonNode addCdcMetadata(
                                 final ObjectNode baseNode,
                                 final JsonNode source,
                                 final CdcMetadataInjector cdcMetadataInjector,
                                 final boolean isDelete) {

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

  AirbyteMessage toAirbyteMessage(final ChangeEventWithMetadata event);

}
