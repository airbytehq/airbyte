/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql.initialsync;

import static io.airbyte.integrations.source.mssql.initialsync.MssqlInitialLoadStateManager.MSSQL_STATE_VERSION;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.AbstractIterator;
import io.airbyte.cdk.integrations.debezium.DebeziumIteratorConstants;
import io.airbyte.cdk.integrations.source.relationaldb.models.InternalModels.StateType;
import io.airbyte.cdk.integrations.source.relationaldb.models.OrderedColumnLoadStatus;
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

public class MssqlInitialSyncStateIterator extends AbstractIterator<AirbyteMessage> implements Iterator<AirbyteMessage> {

  private static final Logger LOGGER = LoggerFactory.getLogger(MssqlInitialSyncStateIterator.class);
  public static final Duration SYNC_CHECKPOINT_DURATION = DebeziumIteratorConstants.SYNC_CHECKPOINT_DURATION;
  public static final Integer SYNC_CHECKPOINT_RECORDS = DebeziumIteratorConstants.SYNC_CHECKPOINT_RECORDS;

  private final Iterator<AirbyteMessage> messageIterator;
  private final AirbyteStreamNameNamespacePair pair;
  private boolean hasEmittedFinalState = false;
  private OrderedColumnLoadStatus ocStatus;
  private final JsonNode streamStateForIncrementalRun;
  private final MssqlInitialLoadStateManager stateManager;
  private long recordCount = 0L;
  private Instant lastCheckpoint = Instant.now();
  private final Duration syncCheckpointDuration;
  private final Long syncCheckpointRecords;
  private final String ocFieldName;

  public MssqlInitialSyncStateIterator(final Iterator<AirbyteMessage> messageIterator,
                                       final AirbyteStreamNameNamespacePair pair,
                                       final MssqlInitialLoadStateManager stateManager,
                                       final JsonNode streamStateForIncrementalRun,
                                       final Duration checkpointDuration,
                                       final Long checkpointRecords) {
    this.messageIterator = messageIterator;
    this.pair = pair;
    this.stateManager = stateManager;
    this.streamStateForIncrementalRun = streamStateForIncrementalRun;
    this.syncCheckpointDuration = checkpointDuration;
    this.syncCheckpointRecords = checkpointRecords;
    this.ocFieldName = stateManager.getOrderedColumnInfo(pair).ocFieldName();
    this.ocStatus = stateManager.getOrderedColumnLoadStatus(pair);
  }

  @CheckForNull
  @Override
  protected AirbyteMessage computeNext() {
    if (messageIterator.hasNext()) {
      if ((recordCount >= syncCheckpointRecords || Duration.between(lastCheckpoint, OffsetDateTime.now()).compareTo(syncCheckpointDuration) > 0)
          && Objects.nonNull(ocStatus)) {
        LOGGER.info("Emitting initial sync ordered col state for stream {}, state is {}", pair, ocStatus);
        recordCount = 0L;
        lastCheckpoint = Instant.now();
        return new AirbyteMessage()
            .withType(Type.STATE)
            .withState(stateManager.createIntermediateStateMessage(pair, ocStatus));
      }
      // Use try-catch to catch Exception that could occur when connection to the database fails
      try {
        final AirbyteMessage message = messageIterator.next();
        if (Objects.nonNull(message)) {
          final String lastOcVal = message.getRecord().getData().get(ocFieldName).asText();
          ocStatus = new OrderedColumnLoadStatus()
              .withVersion(MSSQL_STATE_VERSION)
              .withStateType(StateType.ORDERED_COLUMN)
              .withOrderedCol(ocFieldName)
              .withOrderedColVal(lastOcVal)
              .withIncrementalState(streamStateForIncrementalRun);
          stateManager.updateOrderedColumnLoadState(pair, ocStatus);
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
