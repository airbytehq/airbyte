/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.ctid;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.integrations.source.relationaldb.state.SourceStateIteratorManager;
import io.airbyte.integrations.source.postgres.internal.models.CtidStatus;
import io.airbyte.integrations.source.postgres.internal.models.InternalModels.StateType;
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import java.time.Duration;
import java.time.Instant;
import java.time.OffsetDateTime;
import java.util.Map;
import java.util.Objects;
import org.apache.commons.lang3.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public abstract class CtidStateManager implements SourceStateIteratorManager<AirbyteMessageWithCtid> {

  private static final Logger LOGGER = LoggerFactory.getLogger(CtidStateManager.class);

  public static final long CTID_STATUS_VERSION = 2;
  public static final String STATE_TYPE_KEY = "state_type";

  protected final Map<AirbyteStreamNameNamespacePair, CtidStatus> pairToCtidStatus;

  private AirbyteStreamNameNamespacePair pair;
  private String lastCtid;
  private JsonNode streamStateForIncrementalRun;
  private FileNodeHandler fileNodeHandler;
  private Duration syncCheckpointDuration;
  private Long syncCheckpointRecords;

  protected CtidStateManager(final Map<AirbyteStreamNameNamespacePair, CtidStatus> pairToCtidStatus) {
    this.pairToCtidStatus = pairToCtidStatus;
  }

  public CtidStatus getCtidStatus(final AirbyteStreamNameNamespacePair pair) {
    return pairToCtidStatus.get(pair);
  }

  public static boolean validateRelationFileNode(final CtidStatus ctidstatus,
                                                 final AirbyteStreamNameNamespacePair pair,
                                                 final FileNodeHandler fileNodeHandler) {

    if (fileNodeHandler.hasFileNode(pair)) {
      final Long fileNode = fileNodeHandler.getFileNode(pair);
      return Objects.equals(ctidstatus.getRelationFilenode(), fileNode);
    }
    return true;
  }

  public abstract AirbyteStateMessage createCtidStateMessage(final AirbyteStreamNameNamespacePair pair, final CtidStatus ctidStatus);

  public abstract AirbyteStateMessage createFinalStateMessage(final AirbyteStreamNameNamespacePair pair, final JsonNode streamStateForIncrementalRun);

  public void setStreamStateIteratorFields(AirbyteStreamNameNamespacePair pair,
                                           JsonNode streamStateForIncrementalRun,
                                           FileNodeHandler fileNodeHandler,
                                           Duration syncCheckpointDuration,
                                           Long syncCheckpointRecords) {
    this.pair = pair;
    this.streamStateForIncrementalRun = streamStateForIncrementalRun;
    this.fileNodeHandler = fileNodeHandler;
    this.syncCheckpointDuration = syncCheckpointDuration;
    this.syncCheckpointRecords = syncCheckpointRecords;
  }

  @Override
  public AirbyteStateMessage generateStateMessageAtCheckpoint() {
    final Long fileNode = fileNodeHandler.getFileNode(pair);
    assert fileNode != null;
    final CtidStatus ctidStatus = new CtidStatus()
        .withVersion(CTID_STATUS_VERSION)
        .withStateType(StateType.CTID)
        .withCtid(lastCtid)
        .withIncrementalState(streamStateForIncrementalRun)
        .withRelationFilenode(fileNode);
    LOGGER.info("Emitting ctid state for stream {}, state is {}", pair, ctidStatus);
    return createCtidStateMessage(pair, ctidStatus);
  }

  /**
   * @param message
   */
  @Override
  public AirbyteMessage processRecordMessage(AirbyteMessageWithCtid message) {
    if (Objects.nonNull(message.ctid())) {
      this.lastCtid = message.ctid();
    }
    return message.recordMessage();
  }

  /**
   * @return
   */
  @Override
  public AirbyteStateMessage createFinalStateMessage() {
    final AirbyteStateMessage finalStateMessage = createFinalStateMessage(pair, streamStateForIncrementalRun);
    LOGGER.info("Finished initial sync of stream {}, Emitting final state, state is {}", pair, finalStateMessage);
    return finalStateMessage;
  }

  /**
   * @param recordCount
   * @param lastCheckpoint
   * @return
   */
  @Override
  public boolean shouldEmitStateMessage(long recordCount, Instant lastCheckpoint) {
    return (recordCount >= syncCheckpointRecords || Duration.between(lastCheckpoint, OffsetDateTime.now()).compareTo(syncCheckpointDuration) > 0)
        && Objects.nonNull(lastCtid)
        && StringUtils.isNotBlank(lastCtid);
  }

}
