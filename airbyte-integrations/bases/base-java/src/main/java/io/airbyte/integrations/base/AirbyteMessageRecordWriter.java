package io.airbyte.integrations.base;

import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class AirbyteMessageRecordWriter extends RecordWriter<AirbyteMessage> {
  private static final Logger LOGGER = LoggerFactory.getLogger(AirbyteMessageRecordWriter.class);
  AirbyteMessageRecordWriter() {
    super();
  }

  @Override
  public void outputRecord(final AirbyteMessage message) {
    if (message.getType() == Type.RECORD) {
      super.outputRecord(message);
    } else {
      LOGGER.debug("*** non record message: {}", Jsons.serialize(message));
      super.drainQueueAndOutputRecord(message);
    }

  }
}
