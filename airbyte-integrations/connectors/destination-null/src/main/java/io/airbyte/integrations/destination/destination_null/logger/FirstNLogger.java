package io.airbyte.integrations.destination.destination_null.logger;

import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class FirstNLogger extends BaseLogger implements NullDestinationLogger {

  private static final Logger LOGGER = LoggerFactory.getLogger(FirstNLogger.class);

  public FirstNLogger(AirbyteStreamNameNamespacePair streamNamePair, int maxEntryCount) {
    super(streamNamePair, maxEntryCount);
  }

  @Override
  public void log(AirbyteRecordMessage recordMessage) {
    if (loggedEntryCount >= maxEntryCount) {
      return;
    }

    loggedEntryCount += 1;
    LOGGER.info(entryMessage(recordMessage));
  }

}
