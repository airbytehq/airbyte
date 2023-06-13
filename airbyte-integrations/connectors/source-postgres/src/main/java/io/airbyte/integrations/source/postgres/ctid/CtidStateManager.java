package io.airbyte.integrations.source.postgres.ctid;

import com.fasterxml.jackson.databind.ObjectMapper;
import io.airbyte.commons.exceptions.ConfigErrorException;
import io.airbyte.integrations.source.postgres.internal.models.CtidStatus;
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.Jsons;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteStreamState;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class CtidStateManager {
  private static final Logger LOGGER = LoggerFactory.getLogger(CtidStateManager.class);
  public static final long CTID_STATUS_VERSION = 2;
  public static final String CTID_STATUS_TYPE = "ctid";
  private final Map<AirbyteStreamNameNamespacePair, CtidStatus> pairToCtidStatus;
  private final static AirbyteStateMessage EMPTY_STATE = new AirbyteStateMessage()
      .withType(AirbyteStateType.STREAM)
      .withStream(new AirbyteStreamState());

  public CtidStateManager(final List<AirbyteStateMessage> stateMessages) {
    this.pairToCtidStatus = createPairToCtidStatusMap(stateMessages);
  }

  private static Map<AirbyteStreamNameNamespacePair, CtidStatus> createPairToCtidStatusMap(final List<AirbyteStateMessage> stateMessages) {
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
            assert (ctidStatus.getVer() == CTID_STATUS_VERSION);
            assert(ctidStatus.getType().equals(CTID_STATUS_TYPE)); // TODO: check here
          } catch (final IllegalArgumentException e) {
            throw new ConfigErrorException("Invalid per-stream state");
          }
          localMap.put(pair, ctidStatus);
        }
      }
    }
    return localMap;
  }

  public CtidStatus getCtidStatus(final AirbyteStreamNameNamespacePair pair) {
    return pairToCtidStatus.get(pair);
  }

  public static AirbyteMessage createStateMessage(final AirbyteStreamNameNamespacePair pair, final CtidStatus ctidStatus) {
    final AirbyteStreamState airbyteStreamState =
        new AirbyteStreamState()
            .withStreamDescriptor(
                new StreamDescriptor()
                    .withName(pair.getName())
                    .withNamespace(pair.getNamespace()))
            .withStreamState(new ObjectMapper().valueToTree(ctidStatus));

    final AirbyteStateMessage stateMessage =
        new AirbyteStateMessage()
            .withType(AirbyteStateType.STREAM)
            .withStream(airbyteStreamState);

    return new AirbyteMessage()
        .withType(Type.STATE)
        .withState(stateMessage);
  }
}
