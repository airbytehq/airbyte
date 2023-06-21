/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.ctid;

import io.airbyte.commons.exceptions.ConfigErrorException;
import io.airbyte.integrations.source.postgres.internal.models.CtidStatus;
import io.airbyte.integrations.source.postgres.internal.models.InternalModels.StateType;
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.Jsons;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.v0.AirbyteStreamState;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class CtidStateManager {

  private static final Logger LOGGER = LoggerFactory.getLogger(CtidStateManager.class);
  public static final long CTID_STATUS_VERSION = 2;
  private final Map<AirbyteStreamNameNamespacePair, CtidStatus> pairToCtidStatus;
  private final static AirbyteStateMessage EMPTY_STATE = new AirbyteStateMessage()
      .withType(AirbyteStateType.STREAM)
      .withStream(new AirbyteStreamState());

  public CtidStateManager(final List<AirbyteStateMessage> stateMessages, final Map<AirbyteStreamNameNamespacePair, Long> fileNodes) {
    this.pairToCtidStatus = createPairToCtidStatusMap(stateMessages, fileNodes);
  }

  private static Map<AirbyteStreamNameNamespacePair, CtidStatus> createPairToCtidStatusMap(final List<AirbyteStateMessage> stateMessages,
                                                                                           final Map<AirbyteStreamNameNamespacePair, Long> fileNodes) {
    final Map<AirbyteStreamNameNamespacePair, CtidStatus> localMap = new HashMap<>();
    if (stateMessages != null) {
      for (final AirbyteStateMessage stateMessage : stateMessages) {
        if (stateMessage.getType() == AirbyteStateType.STREAM && !stateMessage.equals(EMPTY_STATE)) {
          LOGGER.info("State message: " + stateMessage);
          final StreamDescriptor streamDescriptor = stateMessage.getStream().getStreamDescriptor();
          final AirbyteStreamNameNamespacePair pair = new AirbyteStreamNameNamespacePair(streamDescriptor.getName(), streamDescriptor.getNamespace());
          final CtidStatus ctidStatus;
          try {
            ctidStatus = Jsons.object(stateMessage.getStream().getStreamState(), CtidStatus.class);
            assert (ctidStatus.getVersion() == CTID_STATUS_VERSION);
            assert (ctidStatus.getStateType().equals(StateType.CTID));
          } catch (final IllegalArgumentException e) {
            throw new ConfigErrorException("Invalid per-stream state");
          }
          if (validateRelationFileNode(ctidStatus, pair, fileNodes)) {
            localMap.put(pair, ctidStatus);
          } else {
            LOGGER.warn(
                "The relation file node for table in source db {} is not equal to the saved ctid state, a full sync from scratch will be triggered.",
                pair);
          }
        }
      }
    }
    return localMap;
  }

  private static boolean validateRelationFileNode(final CtidStatus ctidstatus,
                                                  final AirbyteStreamNameNamespacePair pair,
                                                  final Map<AirbyteStreamNameNamespacePair, Long> fileNodes) {
    if (fileNodes.containsKey(pair)) {
      final Long fileNode = fileNodes.get(pair);
      return Objects.equals(ctidstatus.getRelationFilenode(), fileNode);
    }
    return true;
  }

  public CtidStatus getCtidStatus(final AirbyteStreamNameNamespacePair pair) {
    return pairToCtidStatus.get(pair);
  }

  // TODO : We will need a similar method to generate a GLOBAL state message for CDC
  public static AirbyteMessage createPerStreamStateMessage(final AirbyteStreamNameNamespacePair pair, final CtidStatus ctidStatus) {
    final AirbyteStreamState airbyteStreamState =
        new AirbyteStreamState()
            .withStreamDescriptor(
                new StreamDescriptor()
                    .withName(pair.getName())
                    .withNamespace(pair.getNamespace()))
            .withStreamState(Jsons.jsonNode(ctidStatus));

    final AirbyteStateMessage stateMessage =
        new AirbyteStateMessage()
            .withType(AirbyteStateType.STREAM)
            .withStream(airbyteStreamState);

    return new AirbyteMessage()
        .withType(Type.STATE)
        .withState(stateMessage);
  }

}
