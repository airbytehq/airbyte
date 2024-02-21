/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql.initialsync;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.integrations.source.relationaldb.state.SourceStateIteratorManager;
import io.airbyte.integrations.source.mysql.initialsync.MySqlInitialReadUtil.PrimaryKeyInfo;
import io.airbyte.integrations.source.mysql.internal.models.InternalModels.StateType;
import io.airbyte.integrations.source.mysql.internal.models.PrimaryKeyLoadStatus;
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import java.time.Duration;
import java.time.Instant;
import java.time.OffsetDateTime;
import java.util.HashMap;
import java.util.Map;
import java.util.Objects;

public abstract class MySqlInitialLoadStateManager implements SourceStateIteratorManager<AirbyteMessage> {

  public static long MYSQL_STATUS_VERSION = 2;
  public static String STATE_TYPE_KEY = "state_type";
  public static String PRIMARY_KEY_STATE_TYPE = "primary_key";

  protected AirbyteStreamNameNamespacePair pair;
  protected PrimaryKeyLoadStatus pkStatus;
  protected JsonNode streamStateForIncrementalRun;
  protected Duration syncCheckpointDuration;
  protected Long syncCheckpointRecords;
  protected String pkFieldName;

  void setStreamNameNamespacePair(final AirbyteStreamNameNamespacePair pair) {
    this.pair = pair;
    this.pkStatus = this.getPrimaryKeyLoadStatus(pair);
    this.pkFieldName = this.getPrimaryKeyInfo(pair).pkFieldName();
  }

  void setStreamStateForIncrementalRun(final JsonNode streamStateForIncrementalRun) {
    this.streamStateForIncrementalRun = streamStateForIncrementalRun;
  }

  void setSyncCheckpointDuration(final Duration syncCheckpointDuration) {
    this.syncCheckpointDuration = syncCheckpointDuration;
  }

  void setSyncCheckpointRecords(final Long syncCheckpointRecords) {
    this.syncCheckpointRecords = syncCheckpointRecords;
  }


  // Updates the {@link PrimaryKeyLoadStatus} for the state associated with the given pair
  public abstract void updatePrimaryKeyLoadState(final AirbyteStreamNameNamespacePair pair, final PrimaryKeyLoadStatus pkLoadStatus);

  // Returns the previous state emitted, represented as a {@link PrimaryKeyLoadStatus} associated with
  // the stream.
  public abstract PrimaryKeyLoadStatus getPrimaryKeyLoadStatus(final AirbyteStreamNameNamespacePair pair);

  // Returns the current {@PrimaryKeyInfo}, associated with the stream. This includes the data type &
  // the column name associated with the stream.
  public abstract PrimaryKeyInfo getPrimaryKeyInfo(final AirbyteStreamNameNamespacePair pair);


  @Override
  public AirbyteMessage processRecordMessage(final AirbyteMessage message) {
    if (Objects.nonNull(message)) {
      final String lastPk = message.getRecord().getData().get(pkFieldName).asText();
      pkStatus = new PrimaryKeyLoadStatus()
          .withVersion(MYSQL_STATUS_VERSION)
          .withStateType(StateType.PRIMARY_KEY)
          .withPkName(pkFieldName)
          .withPkVal(lastPk)
          .withIncrementalState(streamStateForIncrementalRun);
      this.updatePrimaryKeyLoadState(pair, pkStatus);
    }
    return message;
  }

  @Override
  public boolean shouldEmitStateMessage(long recordCount, Instant lastCheckpoint) {
    return (recordCount >= syncCheckpointRecords || Duration.between(lastCheckpoint, OffsetDateTime.now()).compareTo(syncCheckpointDuration) > 0)
        && Objects.nonNull(pkStatus);
  }


  public static Map<AirbyteStreamNameNamespacePair, PrimaryKeyLoadStatus> initPairToPrimaryKeyLoadStatusMap(
                                                                                                     final Map<io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair, PrimaryKeyLoadStatus> pairToPkStatus) {
    final Map<AirbyteStreamNameNamespacePair, PrimaryKeyLoadStatus> map = new HashMap<>();
    pairToPkStatus.forEach((pair, pkStatus) -> {
      final AirbyteStreamNameNamespacePair updatedPair = new AirbyteStreamNameNamespacePair(pair.getName(), pair.getNamespace());
      map.put(updatedPair, pkStatus);
    });
    return map;
  }

}
