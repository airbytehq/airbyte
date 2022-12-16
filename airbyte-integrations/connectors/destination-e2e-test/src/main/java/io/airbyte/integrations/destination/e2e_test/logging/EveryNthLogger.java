/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.e2e_test.logging;

import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class EveryNthLogger extends BaseLogger implements TestingLogger {

  private static final Logger LOGGER = LoggerFactory.getLogger(EveryNthLogger.class);

  private final int nthEntryToLog;
  private int currentEntry = 0;

  public EveryNthLogger(final AirbyteStreamNameNamespacePair streamNamePair, final int nthEntryToLog, final int maxEntryCount) {
    super(streamNamePair, maxEntryCount);
    this.nthEntryToLog = nthEntryToLog;
  }

  @Override
  public void log(final AirbyteRecordMessage recordMessage) {
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
