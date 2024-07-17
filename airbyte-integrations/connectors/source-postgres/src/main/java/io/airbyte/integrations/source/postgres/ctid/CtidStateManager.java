/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.ctid;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.integrations.source.relationaldb.state.SourceStateMessageProducer;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.postgres.internal.models.CtidStatus;
import io.airbyte.integrations.source.postgres.internal.models.InternalModels.StateType;
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.util.HashMap;
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
  protected Function<AirbyteStreamNameNamespacePair, JsonNode> streamStateForIncrementalRunSupplier;

  protected Map<AirbyteStreamNameNamespacePair, String> pairToLastCtid;
  protected FileNodeHandler fileNodeHandler;

  protected CtidStateManager(final Map<AirbyteStreamNameNamespacePair, CtidStatus> pairToCtidStatus) {
    this.pairToCtidStatus = pairToCtidStatus;
    this.streamStateForIncrementalRunSupplier = namespacePair -> Jsons.emptyObject();
    this.pairToLastCtid = new HashMap<>();
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

  public void setStreamStateIteratorFields(Function<AirbyteStreamNameNamespacePair, JsonNode> streamStateForIncrementalRunSupplier) {
    this.streamStateForIncrementalRunSupplier = streamStateForIncrementalRunSupplier;
  }

  public void setFileNodeHandler(final FileNodeHandler fileNodeHandler) {
    this.fileNodeHandler = fileNodeHandler;
  }

  public FileNodeHandler getFileNodeHandler() {
    return fileNodeHandler;
  }

  @Override
  public AirbyteStateMessage generateStateMessageAtCheckpoint(final ConfiguredAirbyteStream stream) {
    final AirbyteStreamNameNamespacePair pair = new AirbyteStreamNameNamespacePair(stream.getStream().getName(),
        stream.getStream().getNamespace());
    final CtidStatus ctidStatus = generateCtidStatusForState(pair);
    LOGGER.info("Emitting ctid state for stream {}, state is {}", pair, ctidStatus);
    return createCtidStateMessage(pair, ctidStatus);
  }

  protected CtidStatus generateCtidStatusForState(final AirbyteStreamNameNamespacePair pair) {
    final Long fileNode = fileNodeHandler.getFileNode(pair);
    assert fileNode != null;
    final String lastCtid = pairToLastCtid.get(pair);
    // If the table is empty, lastCtid will be set to zero for the final state message.
    final String lastCtidInState = (Objects.nonNull(lastCtid)
        && StringUtils.isNotBlank(lastCtid)) ? lastCtid : Ctid.ZERO.toString();
    return new CtidStatus()
        .withVersion(CTID_STATUS_VERSION)
        .withStateType(StateType.CTID)
        .withCtid(lastCtidInState)
        .withIncrementalState(getStreamState(pair))
        .withRelationFilenode(fileNode);
  }

  /**
   * Stores the latest CTID.
   */
  @Override
  public AirbyteMessage processRecordMessage(final ConfiguredAirbyteStream stream, AirbyteMessageWithCtid message) {
    if (Objects.nonNull(message.ctid())) {
      final AirbyteStreamNameNamespacePair pair = new AirbyteStreamNameNamespacePair(stream.getStream().getName(),
          stream.getStream().getNamespace());
      pairToLastCtid.put(pair, message.ctid());
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
    final AirbyteStreamNameNamespacePair pair = new AirbyteStreamNameNamespacePair(stream.getStream().getName(),
        stream.getStream().getNamespace());
    final String lastCtid = pairToLastCtid.get(pair);
    return Objects.nonNull(lastCtid)
        && StringUtils.isNotBlank(lastCtid);
  }

  private JsonNode getStreamState(final AirbyteStreamNameNamespacePair pair) {
    final CtidStatus currentCtidStatus = getCtidStatus(pair);

    return (currentCtidStatus == null || currentCtidStatus.getIncrementalState() == null) ? streamStateForIncrementalRunSupplier.apply(pair)
        : currentCtidStatus.getIncrementalState();
  }

}
