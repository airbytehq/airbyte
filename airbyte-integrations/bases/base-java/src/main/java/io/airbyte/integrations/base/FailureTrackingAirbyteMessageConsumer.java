/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base;

import io.airbyte.integrations.base.sentry.AirbyteSentry;
import io.airbyte.protocol.models.AirbyteMessage;
import java.util.Map;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Minimal abstract class intended to provide a consistent structure to classes seeking to implement
 * the {@link AirbyteMessageConsumer} interface. The original interface methods are wrapped in
 * generic exception handlers - any exception is caught and logged.
 *
 * Two methods are intended for extension: - startTracked: Wraps set up of necessary
 * infrastructure/configuration before message consumption. - acceptTracked: Wraps actual processing
 * of each {@link io.airbyte.protocol.models.AirbyteMessage}.
 *
 * Though not necessary, we highly encourage using this class when implementing destinations. See
 * child classes for examples.
 */
public abstract class FailureTrackingAirbyteMessageConsumer implements AirbyteMessageConsumer {

  private static final Logger LOGGER = LoggerFactory.getLogger(FailureTrackingAirbyteMessageConsumer.class);

  private boolean hasFailed = false;

  protected abstract void startTracked() throws Exception;

  @Override
  public void start() throws Exception {
    try {
      AirbyteSentry.executeWithTracing("StartConsumer", this::startTracked,
          Map.of("consumerImpl", FailureTrackingAirbyteMessageConsumer.class.getSimpleName()));
    } catch (final Exception e) {
      hasFailed = true;
      throw e;
    }
  }

  protected abstract void acceptTracked(AirbyteMessage msg) throws Exception;

  @Override
  public void accept(final AirbyteMessage msg) throws Exception {
    try {
      acceptTracked(msg);
    } catch (final Exception e) {
      hasFailed = true;
      throw e;
    }
  }

  protected abstract void close(boolean hasFailed) throws Exception;

  @Override
  public void close() throws Exception {
    if (hasFailed) {
      LOGGER.warn("Airbyte message consumer: failed.");
    } else {
      LOGGER.info("Airbyte message consumer: succeeded.");
    }
    AirbyteSentry.executeWithTracing("CloseConsumer", () -> close(hasFailed),
        Map.of("consumerImpl", FailureTrackingAirbyteMessageConsumer.class.getSimpleName()));
  }

}
