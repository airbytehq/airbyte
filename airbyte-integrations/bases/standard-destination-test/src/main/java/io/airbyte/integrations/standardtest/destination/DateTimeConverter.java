package io.airbyte.integrations.standardtest.destination;

import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import java.util.List;
import java.util.Map;

public interface DateTimeConverter {

  default void convertDateTimeFields(List<AirbyteMessage> messages, Map<String, String> dateTimeFieldNames) {
    for (AirbyteMessage message : messages) {
      if (message.getType() == Type.RECORD) {
        convertDateTime((ObjectNode) message.getRecord().getData(), dateTimeFieldNames);
      }
    }
  }

  default void convertDateTime(ObjectNode data, Map<String, String> dateTimeFieldNames) {
  }

  default boolean requiresDateTimeConversionForNormalizedSync() {
    return false;
  }

  default boolean requiresDateTimeConversionForSync() {
    return false;
  }

}
