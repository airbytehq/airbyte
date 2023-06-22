package io.airbyte.integrations.source.postgres.ctid;

import io.airbyte.commons.exceptions.ConfigErrorException;
import io.airbyte.integrations.source.postgres.internal.models.CtidStatus;
import io.airbyte.integrations.source.postgres.internal.models.InternalModels.StateType;
import io.airbyte.integrations.source.relationaldb.CdcStateManager;
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.Jsons;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class CtidGlobalStateManager {

  private final CdcStateManager cdcStateManager;

  public CtidGlobalStateManager(final CdcStateManager cdcStateManager) {
    this.cdcStateManager = cdcStateManager;
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

}
