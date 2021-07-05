package io.airbyte.integrations.source.debezium.interfaces;

import io.airbyte.protocol.models.AirbyteMessage;
import java.util.Map;

@FunctionalInterface
public interface CdcStateHandler {
  AirbyteMessage state(Map<String, String> offset, String dbHistory);
}
