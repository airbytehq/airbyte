package io.airbyte.integrations.source.postgres.ctid;

import static io.airbyte.integrations.source.postgres.ctid.CtidStateManager.CTID_STATUS_VERSION;

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
import java.util.Objects;
import org.apache.commons.lang3.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class CtidStateIteratorManager implements SourceStateIteratorManager<AirbyteMessageWithCtid> {

  private static final Logger LOGGER = LoggerFactory.getLogger(CtidStateIteratorManager.class);
  private final AirbyteStreamNameNamespacePair pair;
  private String lastCtid;
  private final JsonNode streamStateForIncrementalRun;
  private final FileNodeHandler fileNodeHandler;
  private final CtidStateManager stateManager;
  private final Duration syncCheckpointDuration;
  private final Long syncCheckpointRecords;

  public CtidStateIteratorManager(final AirbyteStreamNameNamespacePair pair,
                                    final FileNodeHandler fileNodeHandler,
                                    final CtidStateManager stateManager,
                                    final JsonNode streamStateForIncrementalRun,
                                    final Duration checkpointDuration,
                                    final Long checkpointRecords) {
    this.pair = pair;
    this.fileNodeHandler = fileNodeHandler;
    this.stateManager = stateManager;
    this.streamStateForIncrementalRun = streamStateForIncrementalRun;
    this.syncCheckpointDuration = checkpointDuration;
    this.syncCheckpointRecords = checkpointRecords;
  }

  /**
   * @return
   */
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
    return stateManager.createCtidStateMessage(pair, ctidStatus);
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
    final AirbyteStateMessage finalStateMessage = stateManager.createFinalStateMessage(pair, streamStateForIncrementalRun);
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
