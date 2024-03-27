/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.debezium.internals;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.cdk.integrations.debezium.CdcMetadataInjector;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import java.time.Instant;

public class RelationalDbDebeziumEventConverter implements DebeziumEventConverter {

  private final CdcMetadataInjector cdcMetadataInjector;
  private final Instant emittedAt;

  public RelationalDbDebeziumEventConverter(CdcMetadataInjector cdcMetadataInjector, Instant emittedAt) {
    this.cdcMetadataInjector = cdcMetadataInjector;
    this.emittedAt = emittedAt;
  }

  @Override
  public AirbyteMessage toAirbyteMessage(ChangeEventWithMetadata event) {
    final JsonNode debeziumEvent = event.eventValueAsJson();
    final JsonNode before = debeziumEvent.get(DebeziumEventConverter.BEFORE_EVENT);
    final JsonNode after = debeziumEvent.get(DebeziumEventConverter.AFTER_EVENT);
    final JsonNode source = debeziumEvent.get(DebeziumEventConverter.SOURCE_EVENT);

    final ObjectNode baseNode = (ObjectNode) (after.isNull() ? before : after);
    final JsonNode data = DebeziumEventConverter.addCdcMetadata(baseNode, source, cdcMetadataInjector, after.isNull());
    return DebeziumEventConverter.buildAirbyteMessage(source, cdcMetadataInjector, emittedAt, data);
  }

}
