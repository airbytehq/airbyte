package io.airbyte.integrations.source.postgres.ctid;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.source.postgres.internal.models.CtidStatus;
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import java.util.Map;
import java.util.Objects;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;

public abstract class CtidStateManager {

  public static final long CTID_STATUS_VERSION = 2;
  public static final String STATE_TYPE_KEY = "state_type";
  public static final String STATE_VER_KEY = "version";

  private final Map<AirbyteStreamNameNamespacePair, CtidStatus> pairToCtidStatus;

  protected CtidStateManager(final Map<AirbyteStreamNameNamespacePair, CtidStatus> pairToCtidStatus) {
    this.pairToCtidStatus = pairToCtidStatus;
  }

  public CtidStatus getCtidStatus(final AirbyteStreamNameNamespacePair pair) {
    return pairToCtidStatus.get(pair);
  }

  public static boolean validateRelationFileNode(final CtidStatus ctidstatus,
      final AirbyteStreamNameNamespacePair pair,
      final Map<AirbyteStreamNameNamespacePair, Long> fileNodes) {

    if (fileNodes.containsKey(pair)) {
      final Long fileNode = fileNodes.get(pair);
      return Objects.equals(ctidstatus.getRelationFilenode(), fileNode);
    }
    return true;
  }

  public abstract AirbyteStateMessage createCtidStateMessage(final AirbyteStreamNameNamespacePair pair, final CtidStatus ctidStatus);

  public abstract AirbyteStateMessage createFinalStateMessage(final AirbyteStreamNameNamespacePair pair, final JsonNode streamStateForIncrementalRun);

}
