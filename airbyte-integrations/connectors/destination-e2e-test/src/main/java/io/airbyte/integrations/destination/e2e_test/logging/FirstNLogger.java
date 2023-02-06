/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.e2e_test.logging;

import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class FirstNLogger extends BaseLogger implements TestingLogger {

  private static final Logger LOGGER = LoggerFactory.getLogger(FirstNLogger.class);

  public FirstNLogger(final AirbyteStreamNameNamespacePair streamNamePair, final int maxEntryCount) {
    super(streamNamePair, maxEntryCount);
  }

  @Override
  public void log(final AirbyteRecordMessage recordMessage) {
    if (loggedEntryCount >= maxEntryCount) {
      return;
    }

    loggedEntryCount += 1;
    LOGGER.info(entryMessage(recordMessage));
  }

}
