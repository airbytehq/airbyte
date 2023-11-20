/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql.initialsync;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.source.mysql.initialsync.MySqlInitialReadUtil.PrimaryKeyInfo;
import io.airbyte.integrations.source.mysql.internal.models.PrimaryKeyLoadStatus;
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import java.util.HashMap;
import java.util.Map;

public interface MySqlInitialLoadStateManager {

  long MYSQL_STATUS_VERSION = 2;
  String STATE_TYPE_KEY = "state_type";
  String PRIMARY_KEY_STATE_TYPE = "primary_key";

  // Returns an intermediate state message for the initial sync.
  AirbyteStateMessage createIntermediateStateMessage(final AirbyteStreamNameNamespacePair pair, final PrimaryKeyLoadStatus pkLoadStatus);

  // Updates the {@link PrimaryKeyLoadStatus} for the state associated with the given pair
  void updatePrimaryKeyLoadState(final AirbyteStreamNameNamespacePair pair, final PrimaryKeyLoadStatus pkLoadStatus);

  // Returns the final state message for the initial sync.
  AirbyteStateMessage createFinalStateMessage(final AirbyteStreamNameNamespacePair pair, final JsonNode streamStateForIncrementalRun);

  // Returns the previous state emitted, represented as a {@link PrimaryKeyLoadStatus} associated with
  // the stream.
  PrimaryKeyLoadStatus getPrimaryKeyLoadStatus(final AirbyteStreamNameNamespacePair pair);

  // Returns the current {@PrimaryKeyInfo}, associated with the stream. This includes the data type &
  // the column name associated with the stream.
  PrimaryKeyInfo getPrimaryKeyInfo(final AirbyteStreamNameNamespacePair pair);

  static Map<AirbyteStreamNameNamespacePair, PrimaryKeyLoadStatus> initPairToPrimaryKeyLoadStatusMap(
                                                                                                     final Map<io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair, PrimaryKeyLoadStatus> pairToPkStatus) {
    final Map<AirbyteStreamNameNamespacePair, PrimaryKeyLoadStatus> map = new HashMap<>();
    pairToPkStatus.forEach((pair, pkStatus) -> {
      final AirbyteStreamNameNamespacePair updatedPair = new AirbyteStreamNameNamespacePair(pair.getName(), pair.getNamespace());
      map.put(updatedPair, pkStatus);
    });
    return map;
  }

}
