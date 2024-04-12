/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.ctid;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.Jsons;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.v0.AirbyteStreamState;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.util.List;

public class CtidFullRefreshPerStreamStateManager extends CtidPerStreamStateManager {

  public CtidFullRefreshPerStreamStateManager(List<AirbyteStateMessage> stateMessages,
                                              FileNodeHandler fileNodeHandler) {
    super(stateMessages, fileNodeHandler);
  }

  // For full refresh we still want to return the latest cursor.
  @Override
  public AirbyteStateMessage createFinalStateMessage(final AirbyteStreamNameNamespacePair pair, final JsonNode streamStateForIncrementalRun) {
    final AirbyteStreamState airbyteStreamState =
        new AirbyteStreamState()
            .withStreamDescriptor(
                new StreamDescriptor()
                    .withName(pair.getName())
                    .withNamespace(pair.getNamespace()))
            .withStreamState(Jsons.jsonNode(generateCtidStatusForState(pair)));
    return new AirbyteStateMessage()
        .withType(AirbyteStateType.STREAM)
        .withStream(airbyteStreamState);
  }

}
