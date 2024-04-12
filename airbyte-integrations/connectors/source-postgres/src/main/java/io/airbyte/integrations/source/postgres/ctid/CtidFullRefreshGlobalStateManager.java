/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.ctid;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.integrations.source.relationaldb.models.CdcState;
import io.airbyte.integrations.source.postgres.cdc.PostgresCdcCtidUtils.CtidStreams;
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.Jsons;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.v0.AirbyteStreamState;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.util.ArrayList;
import java.util.List;

public class CtidFullRefreshGlobalStateManager extends CtidGlobalStateManager {

  public CtidFullRefreshGlobalStateManager(CtidStreams ctidStreams,
                                           FileNodeHandler fileNodeHandler,
                                           CdcState cdcState,
                                           ConfiguredAirbyteCatalog catalog) {
    super(ctidStreams, fileNodeHandler, cdcState, catalog);

  }

  // For full refresh we still want to return the latest cursor.
  @Override
  public AirbyteStateMessage createFinalStateMessage(final AirbyteStreamNameNamespacePair pair, final JsonNode streamStateForIncrementalRun) {

    var ctidStatus = pairToCtidStatus.get(pair);
    final List<AirbyteStreamState> streamStates = new ArrayList<>();
    streamStates.add(getAirbyteStreamState(pair, (Jsons.jsonNode(ctidStatus))));

    final AirbyteStreamState airbyteStreamState =
        new AirbyteStreamState()
            .withStreamDescriptor(
                new StreamDescriptor()
                    .withName(pair.getName())
                    .withNamespace(pair.getNamespace()))
            .withStreamState(Jsons.jsonNode(generateCtidStatusForState(pair)));
    return new AirbyteStateMessage()
        .withType(AirbyteStateType.GLOBAL)
        .withStream(airbyteStreamState);
  }

}
