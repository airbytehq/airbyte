/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.debezium.internals;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.integrations.debezium.CdcMetadataInjector;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.debezium.data.Envelope.Operation;
import java.sql.Timestamp;
import java.time.Instant;

public class DebeziumEventUtils {

  public static final String CDC_LSN = "_ab_cdc_lsn";
  public static final String CDC_UPDATED_AT = "_ab_cdc_updated_at";
  public static final String CDC_DELETED_AT = "_ab_cdc_deleted_at";
  public static final String CDC_OP = "_ab_cdc_op";

  public static AirbyteMessage toAirbyteMessage(final ChangeEventWithMetadata event,
                                                final CdcMetadataInjector cdcMetadataInjector,
                                                final Instant emittedAt) {
    final JsonNode debeziumRecord = event.eventValueAsJson();
    final JsonNode before = debeziumRecord.get("before");
    final JsonNode after = debeziumRecord.get("after");
    final JsonNode source = debeziumRecord.get("source");
    final JsonNode op = debeziumRecord.get("op");
    System.out.println("Debezium record " + debeziumRecord);

    final JsonNode data = formatDebeziumData(before, after, source, op, cdcMetadataInjector);
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
                                             final JsonNode op,
                                             final CdcMetadataInjector cdcMetadataInjector) {
    final ObjectNode base = (ObjectNode) (after.isNull() ? before : after);

    final long transactionMillis = source.get("ts_ms").asLong();
    final String transactionTimestamp = new Timestamp(transactionMillis).toInstant().toString();

    base.put(CDC_UPDATED_AT, transactionTimestamp);
    base.put(CDC_OP, getDebeziumOpReadable(op.asText()));
    cdcMetadataInjector.addMetaData(base, source);
  
    if (after.isNull()) {
      base.put(CDC_DELETED_AT, transactionTimestamp);
    } else {
      base.put(CDC_DELETED_AT, (String) null);
    }

    return base;
  }

  private static String getDebeziumOpReadable(final String debeziumOp) {
    Operation op = Operation.forCode(debeziumOp);
    return switch (op) {
      case CREATE -> "INSERT";
      case UPDATE -> "UPDATE";
      case DELETE -> "DELETE";
      case READ -> "READ";
      default -> throw new RuntimeException("Encountered unhandled change event operation " + op);
      //This should never happen as truncate and message events should be skipped by connectors. 
    };
  }

}
