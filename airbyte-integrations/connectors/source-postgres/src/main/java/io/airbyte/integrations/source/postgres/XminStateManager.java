/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres;

import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.v0.AirbyteStreamState;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class XminStateManager {

  private final Map<AirbyteStreamNameNamespacePair, XminStatus> pairToXminStatus;

  private final static AirbyteStateMessage EMPTY_STATE = new AirbyteStateMessage()
      .withType(AirbyteStateType.STREAM)
      .withStream(new AirbyteStreamState());

  XminStateManager(final List<AirbyteStateMessage> stateMessages) {
    pairToXminStatus = createPairToXminStatusMap(stateMessages);
  }

  private static Map<AirbyteStreamNameNamespacePair, XminStatus> createPairToXminStatusMap(final List<AirbyteStateMessage> stateMessages) {
    final Map<AirbyteStreamNameNamespacePair, XminStatus> localMap = new HashMap<>();
    if (stateMessages != null) {
      for (final AirbyteStateMessage stateMessage : stateMessages) {
        if (!stateMessage.equals(EMPTY_STATE)) {
          final StreamDescriptor streamDescriptor = stateMessage.getStream().getStreamDescriptor();
          final AirbyteStreamNameNamespacePair pair = new AirbyteStreamNameNamespacePair(streamDescriptor.getName(), streamDescriptor.getNamespace());
          final XminStatus xminStatus = Jsons.object(stateMessage.getStream().getStreamState(), XminStatus.class);
          localMap.put(pair, xminStatus);
        }
      }
    }
    return localMap;
  }

  public XminStatus getXminStatus(final AirbyteStreamNameNamespacePair pair) {
    return pairToXminStatus.get(pair);
  }

}
