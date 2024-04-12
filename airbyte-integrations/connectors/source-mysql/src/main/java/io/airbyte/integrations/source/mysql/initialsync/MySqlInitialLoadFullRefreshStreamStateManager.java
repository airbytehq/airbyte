/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql.initialsync;

import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.mysql.initialsync.MySqlInitialReadUtil.InitialLoadStreams;
import io.airbyte.integrations.source.mysql.initialsync.MySqlInitialReadUtil.PrimaryKeyInfo;
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.util.Map;

public class MySqlInitialLoadFullRefreshStreamStateManager extends MySqlInitialLoadStreamStateManager {

  public MySqlInitialLoadFullRefreshStreamStateManager(ConfiguredAirbyteCatalog catalog,
                                                       InitialLoadStreams initialLoadStreams,
                                                       Map<AirbyteStreamNameNamespacePair, PrimaryKeyInfo> pairToPrimaryKeyInfo) {
    super(catalog, initialLoadStreams, pairToPrimaryKeyInfo);
  }

  @Override
  public AirbyteStateMessage createFinalStateMessage(final ConfiguredAirbyteStream stream) {
    AirbyteStreamNameNamespacePair pair = new AirbyteStreamNameNamespacePair(stream.getStream().getName(), stream.getStream().getNamespace());
    var pkStatus = getPrimaryKeyLoadStatus(pair);
    return new AirbyteStateMessage()
        .withType(AirbyteStateType.STREAM)
        .withStream(getAirbyteStreamState(pair, Jsons.jsonNode(pkStatus)));
  }

}
