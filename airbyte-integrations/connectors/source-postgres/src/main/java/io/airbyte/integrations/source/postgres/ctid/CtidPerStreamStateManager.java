/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.ctid;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.exceptions.ConfigErrorException;
import io.airbyte.integrations.source.postgres.internal.models.CtidStatus;
import io.airbyte.integrations.source.postgres.internal.models.InternalModels.StateType;
import io.airbyte.integrations.source.postgres.internal.models.XminStatus;
import io.airbyte.integrations.source.postgres.xmin.XminStateManager;
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.Jsons;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.v0.AirbyteStreamState;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class CtidPerStreamStateManager extends CtidStateManager {

  private static final Logger LOGGER = LoggerFactory.getLogger(CtidPerStreamStateManager.class);
  private final static AirbyteStateMessage EMPTY_STATE = new AirbyteStateMessage()
      .withType(AirbyteStateType.STREAM)
      .withStream(new AirbyteStreamState());

  public CtidPerStreamStateManager(final List<AirbyteStateMessage> stateMessages, final FileNodeHandler fileNodeHandler) {
    super(createPairToCtidStatusMap(stateMessages, fileNodeHandler));
  }

  private static Map<AirbyteStreamNameNamespacePair, CtidStatus> createPairToCtidStatusMap(final List<AirbyteStateMessage> stateMessages,
                                                                                           final FileNodeHandler fileNodeHandler) {
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
          if (validateRelationFileNode(ctidStatus, pair, fileNodeHandler)) {
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

  @Override
  public AirbyteStateMessage createCtidStateMessage(final AirbyteStreamNameNamespacePair pair, final CtidStatus ctidStatus) {
    pairToCtidStatus.put(pair, ctidStatus);
    final AirbyteStreamState airbyteStreamState =
        new AirbyteStreamState()
            .withStreamDescriptor(
                new StreamDescriptor()
                    .withName(pair.getName())
                    .withNamespace(pair.getNamespace()))
            .withStreamState(Jsons.jsonNode(ctidStatus));

    return new AirbyteStateMessage()
        .withType(AirbyteStateType.STREAM)
        .withStream(airbyteStreamState);
  }

  @Override
  public AirbyteStateMessage createFinalStateMessage(final AirbyteStreamNameNamespacePair pair, final JsonNode streamStateForIncrementalRun) {
    if (streamStateForIncrementalRun == null || streamStateForIncrementalRun.isEmpty()) {
      // resumeable full refresh for cursor based stream.
      var ctidStatus = generateCtidStatusForState(pair);
      return createCtidStateMessage(pair, ctidStatus);
    }
    return XminStateManager.getAirbyteStateMessage(pair, Jsons.object(streamStateForIncrementalRun, XminStatus.class));
  }

}
