package io.airbyte.integrations.destination.destination_null.logger;

import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class EveryNthLogger extends BaseLogger implements NullDestinationLogger {

  private static final Logger LOGGER = LoggerFactory.getLogger(EveryNthLogger.class);

  private final int nthEntryToLog;
  private int currentEntry = 0;

  public EveryNthLogger(AirbyteStreamNameNamespacePair streamNamePair, int nthEntryToLog, int maxEntryCount) {
    super(streamNamePair, maxEntryCount);
    this.nthEntryToLog = nthEntryToLog;
  }

  @Override
  public void log(AirbyteRecordMessage recordMessage) {
    if (loggedEntryCount >= maxEntryCount) {
      return;
    }

    currentEntry += 1;
    if (currentEntry % nthEntryToLog == 0) {
      loggedEntryCount += 1;
      LOGGER.info(entryMessage(recordMessage));
    }
  }

}
