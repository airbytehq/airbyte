/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql.initialsync;

import static io.airbyte.integrations.source.mysql.initialsync.MySqlInitialLoadStateManager.MYSQL_STATUS_VERSION;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.AbstractIterator;
import io.airbyte.cdk.integrations.debezium.DebeziumIteratorConstants;
import io.airbyte.integrations.source.mysql.internal.models.InternalModels.StateType;
import io.airbyte.integrations.source.mysql.internal.models.PrimaryKeyLoadStatus;
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import java.time.Duration;
import java.time.Instant;
import java.time.OffsetDateTime;
import java.util.Iterator;
import java.util.Objects;
import javax.annotation.CheckForNull;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MySqlInitialSyncStateIterator extends AbstractIterator<AirbyteMessage> implements Iterator<AirbyteMessage> {

  private static final Logger LOGGER = LoggerFactory.getLogger(MySqlInitialSyncStateIterator.class);
  public static final Duration SYNC_CHECKPOINT_DURATION = DebeziumIteratorConstants.SYNC_CHECKPOINT_DURATION;
  public static final Integer SYNC_CHECKPOINT_RECORDS = DebeziumIteratorConstants.SYNC_CHECKPOINT_RECORDS;

  private final Iterator<AirbyteMessage> messageIterator;
  private final AirbyteStreamNameNamespacePair pair;
  private boolean hasEmittedFinalState = false;
  private PrimaryKeyLoadStatus pkStatus;
  private final JsonNode streamStateForIncrementalRun;
  private final MySqlInitialLoadStateManager stateManager;
  private long recordCount = 0L;
  private Instant lastCheckpoint = Instant.now();
  private final Duration syncCheckpointDuration;
  private final Long syncCheckpointRecords;
  private final String pkFieldName;

  public MySqlInitialSyncStateIterator(final Iterator<AirbyteMessage> messageIterator,
                                       final AirbyteStreamNameNamespacePair pair,
                                       final MySqlInitialLoadStateManager stateManager,
                                       final JsonNode streamStateForIncrementalRun,
                                       final Duration checkpointDuration,
                                       final Long checkpointRecords) {
    this.messageIterator = messageIterator;
    this.pair = pair;
    this.stateManager = stateManager;
    this.streamStateForIncrementalRun = streamStateForIncrementalRun;
    this.syncCheckpointDuration = checkpointDuration;
    this.syncCheckpointRecords = checkpointRecords;
    this.pkFieldName = stateManager.getPrimaryKeyInfo(pair).pkFieldName();
    this.pkStatus = stateManager.getPrimaryKeyLoadStatus(pair);
  }

  @CheckForNull
  @Override
  protected AirbyteMessage computeNext() {
    if (messageIterator.hasNext()) {
      if ((recordCount >= syncCheckpointRecords || Duration.between(lastCheckpoint, OffsetDateTime.now()).compareTo(syncCheckpointDuration) > 0)
          && Objects.nonNull(pkStatus)) {
        LOGGER.info("Emitting initial sync pk state for stream {}, state is {}", pair, pkStatus);
        recordCount = 0L;
        lastCheckpoint = Instant.now();
        return new AirbyteMessage()
            .withType(Type.STATE)
            .withState(stateManager.createIntermediateStateMessage(pair, pkStatus));
      }
      // Use try-catch to catch Exception that could occur when connection to the database fails
      try {
        final AirbyteMessage message = messageIterator.next();
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
        recordCount++;
        return message;
      } catch (final Exception e) {
        throw new RuntimeException(e);
      }
    } else if (!hasEmittedFinalState) {
      hasEmittedFinalState = true;
      final AirbyteStateMessage finalStateMessage = stateManager.createFinalStateMessage(pair, streamStateForIncrementalRun);
      LOGGER.info("Finished initial sync of stream {}, Emitting final state, state is {}", pair, finalStateMessage);
      return new AirbyteMessage()
          .withType(Type.STATE)
          .withState(finalStateMessage);
    } else {
      return endOfData();
    }
  }

}
