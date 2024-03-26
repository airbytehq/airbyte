/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.ctid;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.integrations.source.relationaldb.state.SourceStateMessageProducer;
import io.airbyte.integrations.source.postgres.internal.models.CtidStatus;
import io.airbyte.integrations.source.postgres.internal.models.InternalModels.StateType;
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.util.Map;
import java.util.Objects;
import java.util.function.Function;
import org.apache.commons.lang3.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public abstract class CtidStateManager implements SourceStateMessageProducer<AirbyteMessageWithCtid> {

  private static final Logger LOGGER = LoggerFactory.getLogger(CtidStateManager.class);

  public static final long CTID_STATUS_VERSION = 2;
  public static final String STATE_TYPE_KEY = "state_type";

  protected final Map<AirbyteStreamNameNamespacePair, CtidStatus> pairToCtidStatus;
  private Function<AirbyteStreamNameNamespacePair, JsonNode> streamStateForIncrementalRunSupplier;

  private String lastCtid;
  private FileNodeHandler fileNodeHandler;

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

  public void setStreamStateIteratorFields(Function<AirbyteStreamNameNamespacePair, JsonNode> streamStateForIncrementalRunSupplier,
                                           FileNodeHandler fileNodeHandler) {
    this.streamStateForIncrementalRunSupplier = streamStateForIncrementalRunSupplier;
    this.fileNodeHandler = fileNodeHandler;
  }

  @Override
  public AirbyteStateMessage generateStateMessageAtCheckpoint(final ConfiguredAirbyteStream stream) {
    final AirbyteStreamNameNamespacePair pair = new AirbyteStreamNameNamespacePair(stream.getStream().getName(),
        stream.getStream().getNamespace());
    final Long fileNode = fileNodeHandler.getFileNode(pair);
    assert fileNode != null;
    final CtidStatus ctidStatus = new CtidStatus()
        .withVersion(CTID_STATUS_VERSION)
        .withStateType(StateType.CTID)
        .withCtid(lastCtid)
        .withIncrementalState(getStreamState(pair))
        .withRelationFilenode(fileNode);
    LOGGER.info("Emitting ctid state for stream {}, state is {}", pair, ctidStatus);
    return createCtidStateMessage(pair, ctidStatus);
  }

  /**
   * Stores the latest CTID.
   */
  @Override
  public AirbyteMessage processRecordMessage(final ConfiguredAirbyteStream stream, AirbyteMessageWithCtid message) {
    if (Objects.nonNull(message.ctid())) {
      this.lastCtid = message.ctid();
    }
    return message.recordMessage();
  }

  /**
   * Creates a final state message for the stream.
   */
  @Override
  public AirbyteStateMessage createFinalStateMessage(final ConfiguredAirbyteStream stream) {
    final AirbyteStreamNameNamespacePair pair = new AirbyteStreamNameNamespacePair(stream.getStream().getName(),
        stream.getStream().getNamespace());

    final AirbyteStateMessage finalStateMessage = createFinalStateMessage(pair, getStreamState(pair));
    LOGGER.info("Finished initial sync of stream {}, Emitting final state, state is {}", pair, finalStateMessage);
    return finalStateMessage;
  }

  /**
   * Extra criteria(besides checking frequency) to check if we should emit state message.
   */
  @Override
  public boolean shouldEmitStateMessage(final ConfiguredAirbyteStream stream) {
    return Objects.nonNull(lastCtid)
        && StringUtils.isNotBlank(lastCtid);
  }

  private JsonNode getStreamState(final AirbyteStreamNameNamespacePair pair) {
    final CtidStatus currentCtidStatus = getCtidStatus(pair);
    return (currentCtidStatus == null || currentCtidStatus.getIncrementalState() == null) ? streamStateForIncrementalRunSupplier.apply(pair)
        : currentCtidStatus.getIncrementalState();
  }

}
