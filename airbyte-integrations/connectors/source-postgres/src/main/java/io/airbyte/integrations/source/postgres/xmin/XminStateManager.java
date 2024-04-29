/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.xmin;

import io.airbyte.cdk.integrations.source.relationaldb.state.SourceStateMessageProducer;
import io.airbyte.commons.exceptions.ConfigErrorException;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.postgres.internal.models.XminStatus;
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.v0.AirbyteStreamState;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import org.apache.commons.lang3.NotImplementedException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Utility class to manage xmin state.
 */
public class XminStateManager implements SourceStateMessageProducer<AirbyteMessage> {

  private static final Logger LOGGER = LoggerFactory.getLogger(XminStateManager.class);
  public static final long XMIN_STATE_VERSION = 2L;

  private XminStatus currentXminStatus;

  private final Map<AirbyteStreamNameNamespacePair, XminStatus> pairToXminStatus;

  private final static AirbyteStateMessage EMPTY_STATE = new AirbyteStateMessage()
      .withType(AirbyteStateType.STREAM)
      .withStream(new AirbyteStreamState());

  public XminStateManager(final List<AirbyteStateMessage> stateMessages) {
    pairToXminStatus = createPairToXminStatusMap(stateMessages);
  }

  private static Map<AirbyteStreamNameNamespacePair, XminStatus> createPairToXminStatusMap(final List<AirbyteStateMessage> stateMessages) {
    final Map<AirbyteStreamNameNamespacePair, XminStatus> localMap = new HashMap<>();
    if (stateMessages != null) {
      for (final AirbyteStateMessage stateMessage : stateMessages) {
        // A reset causes the default state to be an empty legacy state, so we have to ignore those
        // messages.
        if (stateMessage.getType() == AirbyteStateType.STREAM && !stateMessage.equals(EMPTY_STATE)) {
          LOGGER.info("State message: " + stateMessage);
          final StreamDescriptor streamDescriptor = stateMessage.getStream().getStreamDescriptor();
          final AirbyteStreamNameNamespacePair pair = new AirbyteStreamNameNamespacePair(streamDescriptor.getName(), streamDescriptor.getNamespace());
          final XminStatus xminStatus;
          try {
            xminStatus = Jsons.object(stateMessage.getStream().getStreamState(), XminStatus.class);
          } catch (final IllegalArgumentException e) {
            throw new ConfigErrorException(
                "Invalid per-stream state. If this connection was migrated to a Xmin incremental mode from a cursor-based or CDC incremental mode, "
                    + "please reset your connection and re-sync.");
          }
          localMap.put(pair, xminStatus);
        }
      }
    }
    return localMap;
  }

  public XminStatus getXminStatus(final AirbyteStreamNameNamespacePair pair) {
    return pairToXminStatus.get(pair);
  }

  /**
   * Creates AirbyteStateMessage associated with the given {@link XminStatus}.
   *
   * @return AirbyteMessage which includes information on state of records read so far
   */
  public static AirbyteMessage createStateMessage(final AirbyteStreamNameNamespacePair pair, final XminStatus xminStatus) {
    final AirbyteStateMessage stateMessage = getAirbyteStateMessage(pair, xminStatus);

    return new AirbyteMessage()
        .withType(Type.STATE)
        .withState(stateMessage);
  }

  public static AirbyteStateMessage getAirbyteStateMessage(final AirbyteStreamNameNamespacePair pair, final XminStatus xminStatus) {
    final AirbyteStreamState airbyteStreamState =
        new AirbyteStreamState()
            .withStreamDescriptor(
                new StreamDescriptor()
                    .withName(pair.getName())
                    .withNamespace(pair.getNamespace()))
            .withStreamState(Jsons.jsonNode(xminStatus));

    // Set state
    return new AirbyteStateMessage()
        .withType(AirbyteStateType.STREAM)
        .withStream(airbyteStreamState);
  }

  public void setCurrentXminStatus(final XminStatus currentXminStatus) {
    this.currentXminStatus = currentXminStatus;
  }

  @Override
  public AirbyteStateMessage generateStateMessageAtCheckpoint(final ConfiguredAirbyteStream stream) {
    // This is not expected to be called.
    throw new NotImplementedException();
  }

  @Override
  public AirbyteMessage processRecordMessage(final ConfiguredAirbyteStream stream, AirbyteMessage message) {
    return message;
  }

  @Override
  public AirbyteStateMessage createFinalStateMessage(final ConfiguredAirbyteStream stream) {
    final AirbyteStreamNameNamespacePair pair = new AirbyteStreamNameNamespacePair(stream.getStream().getName(), stream.getStream().getNamespace());
    return XminStateManager.createStateMessage(pair, currentXminStatus).getState();
  }

  // We do not send state message for xmin for checkpointing purpose.
  @Override
  public boolean shouldEmitStateMessage(final ConfiguredAirbyteStream stream) {
    return false;
  }

}
