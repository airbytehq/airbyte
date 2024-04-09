/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql.initialsync;

import io.airbyte.cdk.integrations.source.relationaldb.models.CdcState;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.mysql.initialsync.MySqlInitialReadUtil.InitialLoadStreams;
import io.airbyte.integrations.source.mysql.initialsync.MySqlInitialReadUtil.PrimaryKeyInfo;
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.AirbyteGlobalState;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.v0.AirbyteStreamState;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public class MySqlInitialLoadFullRefreshGlobalStateManager extends MySqlInitialLoadGlobalStateManager {

  public MySqlInitialLoadFullRefreshGlobalStateManager(InitialLoadStreams initialLoadStreams,
                                                       Map<AirbyteStreamNameNamespacePair, PrimaryKeyInfo> pairToPrimaryKeyInfo,
                                                       CdcState cdcState,
                                                       ConfiguredAirbyteCatalog catalog) {
    super(initialLoadStreams, pairToPrimaryKeyInfo, cdcState, catalog);
  }

  @Override
  public AirbyteStateMessage createFinalStateMessage(final ConfiguredAirbyteStream airbyteStream) {
    AirbyteStreamNameNamespacePair pair =
        new AirbyteStreamNameNamespacePair(airbyteStream.getStream().getName(), airbyteStream.getStream().getNamespace());

    // Full refresh - do not reset status; platform will handle this.
    var pkStatus = getPrimaryKeyLoadStatus(pair);
    final List<AirbyteStreamState> streamStates = new ArrayList<>();
    streamStates.add(getAirbyteStreamState(pair, (Jsons.jsonNode(pkStatus))));

    final AirbyteGlobalState globalState = new AirbyteGlobalState();
    globalState.setSharedState(Jsons.jsonNode(cdcState));
    globalState.setStreamStates(streamStates);

    return new AirbyteStateMessage()
        .withType(AirbyteStateType.GLOBAL)
        .withGlobal(globalState);
  }

}
