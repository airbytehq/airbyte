/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base;

import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import java.util.function.Consumer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Minimal abstract class intended to handle the case where the destination can commit records every
 * time a state message appears. This class does that commit and then immediately emits the state
 * message. This should only be used in cases when the commit is relatively cheap. immediately.
 */
public abstract class CommitOnStateAirbyteMessageConsumer extends FailureTrackingAirbyteMessageConsumer implements AirbyteMessageConsumer {

  private static final Logger LOGGER = LoggerFactory.getLogger(CommitOnStateAirbyteMessageConsumer.class);

  private final Consumer<AirbyteMessage> outputRecordCollector;

  public CommitOnStateAirbyteMessageConsumer(final Consumer<AirbyteMessage> outputRecordCollector) {
    this.outputRecordCollector = outputRecordCollector;
  }

  @Override
  public void accept(final AirbyteMessage message) throws Exception {
    if (message.getType() == Type.STATE) {
      commit();
      outputRecordCollector.accept(message);
    }
    super.accept(message);
  }

  public abstract void commit() throws Exception;

}
