package io.airbyte.integrations.destination.destination_null.logger;

import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import java.util.Random;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class RandomSamplingLogger extends BaseLogger implements NullDestinationLogger {

  private static final Logger LOGGER = LoggerFactory.getLogger(RandomSamplingLogger.class);

  private final double samplingRatio;
  private final Random random;

  public RandomSamplingLogger(AirbyteStreamNameNamespacePair streamNamePair, double samplingRatio, long seed, int maxEntryCount) {
    super(streamNamePair, maxEntryCount);
    this.samplingRatio = samplingRatio;
    this.random = new Random(seed);
  }

  @Override
  public void log(AirbyteRecordMessage recordMessage) {
    if (loggedEntryCount >= maxEntryCount) {
      return;
    }

    if (random.nextDouble() < samplingRatio) {
      loggedEntryCount += 1;
      LOGGER.info(entryMessage(recordMessage));
    }
  }

}
