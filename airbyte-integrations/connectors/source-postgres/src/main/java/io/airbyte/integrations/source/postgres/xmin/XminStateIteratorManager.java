/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.xmin;

import io.airbyte.cdk.integrations.source.relationaldb.state.SourceStateIteratorManager;
import io.airbyte.integrations.source.postgres.internal.models.XminStatus;
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import java.time.Instant;
import org.apache.commons.lang3.NotImplementedException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class XminStateIteratorManager implements SourceStateIteratorManager<AirbyteMessage> {

  private static final Logger LOGGER = LoggerFactory.getLogger(XminStateIteratorManager.class);

  private final AirbyteStreamNameNamespacePair pair;
  private boolean hasEmittedFinalState;

  private boolean hasCaughtException = false;
  private final XminStatus xminStatus;

  /**
   * @param pair Stream Name and Namespace (e.g. public.users)
   */
  public XminStateIteratorManager(
                                  final AirbyteStreamNameNamespacePair pair,
                                  final XminStatus xminStatus) {
    this.pair = pair;
    this.xminStatus = xminStatus;
  }

  @Override
  public AirbyteStateMessage generateStateMessageAtCheckpoint() {
    // This is not expected to be called.
    throw new NotImplementedException();
  }

  @Override
  public AirbyteMessage processRecordMessage(AirbyteMessage message) {
    return message;
  }

  @Override
  public AirbyteStateMessage createFinalStateMessage() {
    return XminStateManager.createStateMessage(pair, xminStatus).getState();
  }

  @Override
  public boolean shouldEmitStateMessage(long recordCount, Instant lastCheckpoint) {
    return false;
  }

}
