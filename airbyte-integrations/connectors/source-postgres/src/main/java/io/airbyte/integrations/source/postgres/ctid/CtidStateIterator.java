/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.ctid;

import static io.airbyte.integrations.source.postgres.ctid.CtidStateManager.CTID_STATUS_VERSION;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.AbstractIterator;
import io.airbyte.integrations.source.postgres.internal.models.CtidStatus;
import io.airbyte.integrations.source.postgres.internal.models.InternalModels.StateType;
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
import org.apache.commons.lang3.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class CtidStateIterator extends AbstractIterator<AirbyteMessage> implements Iterator<AirbyteMessage> {

  private static final Logger LOGGER = LoggerFactory.getLogger(CtidStateIterator.class);
  public static final Duration SYNC_CHECKPOINT_DURATION = Duration.ofMinutes(15);
  public static final Integer SYNC_CHECKPOINT_RECORDS = 10_000;

  private final Iterator<AirbyteMessageWithCtid> messageIterator;
  private final AirbyteStreamNameNamespacePair pair;
  private boolean hasEmittedFinalState;
  private String lastCtid;
  private final JsonNode streamStateForIncrementalRun;
  private final long relationFileNode;
  private final CtidStateManager stateManager;
  private long recordCount = 0L;
  private Instant lastCheckpoint = Instant.now();
  private final Duration syncCheckpointDuration;
  private final Long syncCheckpointRecords;

  public CtidStateIterator(final Iterator<AirbyteMessageWithCtid> messageIterator,
                           final AirbyteStreamNameNamespacePair pair,
                           final long relationFileNode,
                           final CtidStateManager stateManager,
                           final JsonNode streamStateForIncrementalRun,
                           final Duration checkpointDuration,
                           final Long checkpointRecords) {
    this.messageIterator = messageIterator;
    this.pair = pair;
    this.relationFileNode = relationFileNode;
    this.stateManager = stateManager;
    this.streamStateForIncrementalRun = streamStateForIncrementalRun;
    this.syncCheckpointDuration = checkpointDuration;
    this.syncCheckpointRecords = checkpointRecords;
  }

  @CheckForNull
  @Override
  protected AirbyteMessage computeNext() {
    if (messageIterator.hasNext()) {
      if ((recordCount >= syncCheckpointRecords || Duration.between(lastCheckpoint, OffsetDateTime.now()).compareTo(syncCheckpointDuration) > 0)
          && Objects.nonNull(lastCtid)
          && StringUtils.isNotBlank(lastCtid)) {
        final CtidStatus ctidStatus = new CtidStatus()
            .withVersion(CTID_STATUS_VERSION)
            .withStateType(StateType.CTID)
            .withCtid(lastCtid)
            .withIncrementalState(streamStateForIncrementalRun)
            .withRelationFilenode(relationFileNode);
        LOGGER.info("Emitting ctid state for stream {}, state is {}", pair, ctidStatus);
        recordCount = 0L;
        lastCheckpoint = Instant.now();
        return new AirbyteMessage()
            .withType(Type.STATE)
            .withState(stateManager.createCtidStateMessage(pair, ctidStatus));
      }
      // Use try-catch to catch Exception that could occur when connection to the database fails
      try {
        final AirbyteMessageWithCtid message = messageIterator.next();
        if (Objects.nonNull(message.ctid())) {
          this.lastCtid = message.ctid();
        }
        recordCount++;
        return message.recordMessage();
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
