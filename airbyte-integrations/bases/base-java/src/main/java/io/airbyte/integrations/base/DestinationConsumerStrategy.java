package io.airbyte.integrations.base;

import io.airbyte.protocol.models.AirbyteMessage;
import java.util.Map;

public interface DestinationConsumerStrategy extends DestinationConsumer<AirbyteMessage> {

  void setContext(Map<String, DestinationWriteContext> configs);
}
