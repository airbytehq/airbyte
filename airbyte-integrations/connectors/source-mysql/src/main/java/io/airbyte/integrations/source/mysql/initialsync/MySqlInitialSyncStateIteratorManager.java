/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql.initialsync;

import static io.airbyte.integrations.source.mysql.initialsync.MySqlInitialLoadStateManager.MYSQL_STATUS_VERSION;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.integrations.source.relationaldb.state.SourceStateIteratorManager;
import io.airbyte.integrations.source.mysql.internal.models.InternalModels.StateType;
import io.airbyte.integrations.source.mysql.internal.models.PrimaryKeyLoadStatus;
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import java.time.Duration;
import java.time.Instant;
import java.time.OffsetDateTime;
import java.util.Objects;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MySqlInitialSyncStateIteratorManager implements SourceStateIteratorManager<AirbyteMessage> {

  private static final Logger LOGGER = LoggerFactory.getLogger(MySqlInitialSyncStateIteratorManager.class);

  private final AirbyteStreamNameNamespacePair pair;
  private PrimaryKeyLoadStatus pkStatus;
  private final JsonNode streamStateForIncrementalRun;
  private final MySqlInitialLoadStateManager stateManager;
  private final Duration syncCheckpointDuration;
  private final Long syncCheckpointRecords;
  private final String pkFieldName;

  public MySqlInitialSyncStateIteratorManager(
                                              final AirbyteStreamNameNamespacePair pair,
                                              final MySqlInitialLoadStateManager stateManager,
                                              final JsonNode streamStateForIncrementalRun,
                                              final Duration checkpointDuration,
                                              final Long checkpointRecords) {
    this.pair = pair;
    this.stateManager = stateManager;
    this.streamStateForIncrementalRun = streamStateForIncrementalRun;
    this.syncCheckpointDuration = checkpointDuration;
    this.syncCheckpointRecords = checkpointRecords;
    this.pkFieldName = stateManager.getPrimaryKeyInfo(pair).pkFieldName();
    this.pkStatus = stateManager.getPrimaryKeyLoadStatus(pair);
  }

  @Override
  public AirbyteStateMessage generateStateMessageAtCheckpoint() {
    LOGGER.info("Emitting initial sync pk state for stream {}, state is {}", pair, pkStatus);
    return stateManager.createIntermediateStateMessage(pair, pkStatus);
  }

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
      stateManager.updatePrimaryKeyLoadState(pair, pkStatus);
    }
    return message;
  }

  @Override
  public AirbyteStateMessage createFinalStateMessage() {
    final AirbyteStateMessage finalStateMessage = stateManager.createFinalStateMessage(pair, streamStateForIncrementalRun);
    LOGGER.info("Finished initial sync of stream {}, Emitting final state, state is {}", pair, finalStateMessage);
    return finalStateMessage;
  }

  @Override
  public boolean shouldEmitStateMessage(long recordCount, Instant lastCheckpoint) {
    return (recordCount >= syncCheckpointRecords || Duration.between(lastCheckpoint, OffsetDateTime.now()).compareTo(syncCheckpointDuration) > 0)
        && Objects.nonNull(pkStatus);
  }

}
