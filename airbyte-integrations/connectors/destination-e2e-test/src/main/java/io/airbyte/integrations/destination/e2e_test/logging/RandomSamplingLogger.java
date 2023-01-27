/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.e2e_test.logging;

import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import java.util.Random;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class RandomSamplingLogger extends BaseLogger implements TestingLogger {

  private static final Logger LOGGER = LoggerFactory.getLogger(RandomSamplingLogger.class);

  private final double samplingRatio;
  private final Random random;

  public RandomSamplingLogger(final AirbyteStreamNameNamespacePair streamNamePair,
                              final double samplingRatio,
                              final long seed,
                              final int maxEntryCount) {
    super(streamNamePair, maxEntryCount);
    this.samplingRatio = samplingRatio;
    this.random = new Random(seed);
  }

  @Override
  public void log(final AirbyteRecordMessage recordMessage) {
    if (loggedEntryCount >= maxEntryCount) {
      return;
    }

    if (random.nextDouble() < samplingRatio) {
      loggedEntryCount += 1;
      LOGGER.info(entryMessage(recordMessage));
    }
  }

}
