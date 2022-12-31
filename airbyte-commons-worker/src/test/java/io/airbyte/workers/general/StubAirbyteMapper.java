package io.airbyte.workers.general;

import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.workers.internal.AirbyteMapper;

public class StubAirbyteMapper implements AirbyteMapper {

  @Override
  public ConfiguredAirbyteCatalog mapCatalog(ConfiguredAirbyteCatalog catalog) {
    return null;
  }

  @Override
  public AirbyteMessage mapMessage(AirbyteMessage message) {
    return message;
  }
}
