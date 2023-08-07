package io.airbyte.integrations.source.mysql.initialsync;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.source.mysql.initialsync.MySqlInitialReadUtil.PrimaryKeyInfo;
import io.airbyte.integrations.source.mysql.internal.models.PrimaryKeyLoadStatus;
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;

public interface MySqlInitialLoadStateManager {
  long MYSQL_STATUS_VERSION = 2;
  String STATE_TYPE_KEY = "state_type";
  String PRIMARY_KEY_STATE_TYPE = "primary_key";

  // Returns an intermediate state message for the initial sync.
  AirbyteStateMessage createIntermediateStateMessage(final AirbyteStreamNameNamespacePair pair, final PrimaryKeyLoadStatus pkLoadStatus);

  // Returns the final state message for the initial sync.
  AirbyteStateMessage createFinalStateMessage(final AirbyteStreamNameNamespacePair pair, final JsonNode streamStateForIncrementalRun);

  // Returns the previous state, represented as a {@link PrimaryKeyLoadStatus} associated with the stream.
  PrimaryKeyLoadStatus getPrimaryKeyLoadStatus(final AirbyteStreamNameNamespacePair pair);

  // Returns the current {@PrimaryKeyInfo}, associated with the stream. This includes the data type & the column name associated with the stream.
  PrimaryKeyInfo getPrimaryKeyInfo(final AirbyteStreamNameNamespacePair pair);
}
