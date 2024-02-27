/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.state;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.cdk.integrations.debezium.CdcMetadataInjector;
import io.airbyte.cdk.integrations.source.relationaldb.state.SourceStateIteratorManager;
import io.airbyte.commons.exceptions.ConfigErrorException;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.mongodb.MongoConstants;
import io.airbyte.integrations.source.mongodb.cdc.MongoDbCdcEventUtils;
import io.airbyte.integrations.source.mongodb.cdc.MongoDbCdcState;
import io.airbyte.protocol.models.v0.AirbyteGlobalState;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.AirbyteStreamState;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.time.Duration;
import java.time.Instant;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;
import java.util.stream.Collectors;
import org.bson.Document;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * A state manager for MongoDB CDC syncs.
 */
public class MongoDbStateManager implements SourceStateIteratorManager<Document> {

  private static final Logger LOGGER = LoggerFactory.getLogger(MongoDbStateManager.class);

  /**
   * The global CDC state.
   */
  private MongoDbCdcState cdcState;
  private ConfiguredAirbyteStream stream;

  private Object lastId;
  private Set<String> fields;
  private Instant emittedAt;
  private Optional<CdcMetadataInjector<?>> cdcMetadataInjector;
  private long checkpointInterval;
  private Duration checkpointDuration;
  private boolean isEnforceSchema;

  /**
   * Map of streams (name/namespace tuple) to the current stream state information stored in the
   * state.
   */
  private final Map<AirbyteStreamNameNamespacePair, MongoDbStreamState> pairToStreamState = new HashMap<>();

  /**
   * Creates a new {@link MongoDbStateManager} primed with the provided initial state.
   *
   * @param initialState The initial state to be stored in the state manager.
   * @return A new {@link MongoDbStateManager}
   */
  public static MongoDbStateManager createStateManager(final JsonNode initialState) {
    final MongoDbStateManager stateManager = new MongoDbStateManager();

    if (initialState == null) {
      return stateManager;
    }

    LOGGER.info("Initial state {}", initialState);
    final List<AirbyteStateMessage> stateMessages = deserializeState(initialState);

    if (!stateMessages.isEmpty()) {
      if (stateMessages.size() == 1) {
        final AirbyteStateMessage stateMessage = stateMessages.get(0);
        stateManager.updateCdcState(Jsons.object(stateMessage.getGlobal().getSharedState(), MongoDbCdcState.class));
        stateMessage.getGlobal().getStreamStates()
            .forEach(s -> stateManager.updateStreamState(s.getStreamDescriptor().getName(), s.getStreamDescriptor().getNamespace(),
                Jsons.object(s.getStreamState(), MongoDbStreamState.class)));
      } else {
        throw new IllegalStateException("The state contains multiple message, but only 1 is expected.");
      }
    }

    return stateManager;
  }

  private static List<AirbyteStateMessage> deserializeState(final JsonNode initialState) {
    try {
      return Jsons.object(initialState, new TypeReference<>() {});
    } catch (final IllegalArgumentException e) {
      LOGGER.debug("Failed to deserialize initial state {}.", initialState, e);
      return List.of();
    }
  }

  /**
   * Creates a new {@link MongoDbStateManager} instance. This constructor should not be called
   * directly. Instead, use {@link #createStateManager(JsonNode)}.
   */
  private MongoDbStateManager() {}

  /**
   * Returns the global, CDC state stored by the manager.
   *
   * @return A {@link MongoDbCdcState} instance that represents the global state.
   */
  public MongoDbCdcState getCdcState() {
    return cdcState;
  }

  /**
   * Returns the current stream state for the given stream.
   *
   * @param streamName The name of the stream.
   * @param streamNamespace The namespace of the stream.
   * @return The {@link MongoDbStreamState} associated with the stream or an empty {@link Optional} if
   *         the stream is not currently tracked by the manager.
   */
  public Optional<MongoDbStreamState> getStreamState(final String streamName, final String streamNamespace) {
    final AirbyteStreamNameNamespacePair airbyteStreamNameNamespacePair = new AirbyteStreamNameNamespacePair(streamName, streamNamespace);
    return Optional.ofNullable(pairToStreamState.get(airbyteStreamNameNamespacePair));
  }

  public Map<AirbyteStreamNameNamespacePair, MongoDbStreamState> getStreamStates() {
    return Map.copyOf(pairToStreamState);
  }

  /**
   * Updates the global, CDC state tracked by the manager.
   *
   * @param cdcState The new global, CDC state as an {@link MongoDbCdcState} instance.
   */
  public void updateCdcState(final MongoDbCdcState cdcState) {
    LOGGER.debug("Updating CDC state to {}...", cdcState);
    this.cdcState = cdcState;
  }

  /**
   * Updates the state associated with a stream.
   *
   * @param streamName The name of the stream.
   * @param streamNamespace The namespace of the stream.
   * @param streamState The new stream state.
   */
  public void updateStreamState(final String streamName, final String streamNamespace, final MongoDbStreamState streamState) {
    final AirbyteStreamNameNamespacePair airbyteStreamNameNamespacePair = new AirbyteStreamNameNamespacePair(streamName, streamNamespace);
    LOGGER.debug("Updating stream state for stream {}:{} to {}...", streamNamespace, streamName, streamState);
    pairToStreamState.put(airbyteStreamNameNamespacePair, streamState);
  }

  /**
   * Resets the state stored in this manager by overwriting the CDC state and clearing the stream
   * state.
   *
   * @param cdcState The new CDC state.
   */
  public void resetState(final MongoDbCdcState cdcState) {
    LOGGER.debug("Resetting state with CDC state {}...", cdcState);
    updateCdcState(cdcState);
    pairToStreamState.clear();
  }

  /**
   * Generates an {@link AirbyteStateMessage} from the state tracked by this manager. The resulting
   * state message contains a global state object with the CDC state as the "shared state" and the
   * individual stream states as the "stream states".
   *
   * @return An {@link AirbyteStateMessage} that represents the state stored by the manager.
   */
  public AirbyteStateMessage toState() {
    // Populate global state
    final AirbyteGlobalState globalState = new AirbyteGlobalState();
    // TODO For now, handle the null cdc state case. Once integrated with Debezium, we should
    // never hit this scenario, as we should set the cdc state to the initial offset retrieved at start
    // of the sync.
    final MongoDbCdcState cdcState = getCdcState();
    globalState.setSharedState(cdcState != null ? Jsons.jsonNode(cdcState) : Jsons.emptyObject());
    globalState.setStreamStates(generateStreamStateList(pairToStreamState));

    return new AirbyteStateMessage()
        .withType(AirbyteStateMessage.AirbyteStateType.GLOBAL)
        .withGlobal(globalState);
  }

  private List<AirbyteStreamState> generateStreamStateList(final Map<AirbyteStreamNameNamespacePair, MongoDbStreamState> pairToCursorInfoMap) {
    return pairToCursorInfoMap.entrySet().stream()
        .sorted(Map.Entry.comparingByKey())
        .map(e -> generateStreamState(e.getKey(), e.getValue()))
        .filter(s -> isValidStreamDescriptor(s.getStreamDescriptor()))
        .collect(Collectors.toList());
  }

  private AirbyteStreamState generateStreamState(final AirbyteStreamNameNamespacePair airbyteStreamNameNamespacePair,
                                                 final MongoDbStreamState streamState) {
    return new AirbyteStreamState()
        .withStreamDescriptor(
            new StreamDescriptor()
                .withName(airbyteStreamNameNamespacePair.getName())
                .withNamespace(airbyteStreamNameNamespacePair.getNamespace()))
        .withStreamState(Jsons.jsonNode(streamState));
  }

  /**
   * Tests whether the provided {@link StreamDescriptor} is valid. A valid descriptor is defined as
   * one that has a non-{@code null} name.
   * <p>
   * See <a href=
   * "https://github.com/airbytehq/airbyte/blob/e63458fabb067978beb5eaa74d2bc130919b419f/docs/understanding-airbyte/airbyte-protocol.md">the
   * Airbyte protocol</a> for more details
   *
   * @param streamDescriptor A {@link StreamDescriptor} to be validated.
   * @return {@code true} if the provided {@link StreamDescriptor} is valid or {@code false} if it is
   *         invalid.
   */
  private boolean isValidStreamDescriptor(final StreamDescriptor streamDescriptor) {
    if (streamDescriptor != null) {
      return streamDescriptor.getName() != null;
    } else {
      return false;
    }
  }

  // Required when using stateIterator related functions below.
  public void withIteratorFields(final ConfiguredAirbyteStream stream,
                                 final Instant emittedAt,
                                 final Optional<CdcMetadataInjector<?>> cdcMetadataInjector,
                                 final long checkpointInterval,
                                 final Duration checkpointDuration,
                                 final boolean isEnforceSchema) {
    this.stream = stream;
    this.lastId = this.getStreamState(stream.getStream().getName(), stream.getStream().getNamespace()).map(MongoDbStreamState::id).orElse(null);
    this.fields = CatalogHelpers.getTopLevelFieldNames(stream).stream().collect(Collectors.toSet());
    this.emittedAt = emittedAt;
    this.cdcMetadataInjector = cdcMetadataInjector;
    this.checkpointInterval = checkpointInterval;
    this.checkpointDuration = checkpointDuration;
    this.isEnforceSchema = isEnforceSchema;
  }

  /**
   * @return
   */
  @Override
  public AirbyteStateMessage generateStateMessageAtCheckpoint() {
    if (lastId != null) {
      final var idType = IdType.findByJavaType(lastId.getClass().getSimpleName())
          .orElseThrow(() -> new ConfigErrorException("Unsupported _id type " + lastId.getClass().getSimpleName()));
      final var state = new MongoDbStreamState(lastId.toString(), InitialSnapshotStatus.IN_PROGRESS, idType);
      updateStreamState(stream.getStream().getName(), stream.getStream().getNamespace(), state);
    }
    return toState();
  }

  /**
   * @param
   * @return
   */
  @Override
  public AirbyteMessage processRecordMessage(final Document document) {
    final var fields = CatalogHelpers.getTopLevelFieldNames(stream).stream().collect(Collectors.toSet());

    final var jsonNode = isEnforceSchema ? MongoDbCdcEventUtils.toJsonNode(document, fields) : MongoDbCdcEventUtils.toJsonNodeNoSchema(document);

    lastId = document.get(MongoConstants.ID_FIELD);

    return new AirbyteMessage()
        .withType(Type.RECORD)
        .withRecord(new AirbyteRecordMessage()
            .withStream(stream.getStream().getName())
            .withNamespace(stream.getStream().getNamespace())
            .withEmittedAt(emittedAt.toEpochMilli())
            .withData(injectMetadata(jsonNode)));
  }

  private JsonNode injectMetadata(final JsonNode jsonNode) {
    if (Objects.nonNull(cdcMetadataInjector) && cdcMetadataInjector.isPresent() && jsonNode instanceof ObjectNode) {
      cdcMetadataInjector.get().addMetaDataToRowsFetchedOutsideDebezium((ObjectNode) jsonNode, emittedAt.toString(), null);
    }

    return jsonNode;
  }

  /**
   * @return
   */
  @Override
  public AirbyteStateMessage createFinalStateMessage() {
    if (lastId != null) {
      LOGGER.debug("Emitting final state status for stream {}:{}...", stream.getStream().getNamespace(), stream.getStream().getName());
      final var finalStateStatus = InitialSnapshotStatus.COMPLETE;
      final var idType = IdType.findByJavaType(lastId.getClass().getSimpleName())
          .orElseThrow(() -> new ConfigErrorException("Unsupported _id type " + lastId.getClass().getSimpleName()));
      final var state = new MongoDbStreamState(lastId.toString(), finalStateStatus, idType);

      updateStreamState(stream.getStream().getName(), stream.getStream().getNamespace(), state);
    }
    return toState();
  }

  /**
   * @param recordCount
   * @param lastCheckpoint
   * @return
   */
  @Override
  public boolean shouldEmitStateMessage(long recordCount, Instant lastCheckpoint) {
    // Should a state message be emitted based on the number of messages we've seen?
    final var emitStateDueToMessageCount = recordCount > 0 && recordCount % checkpointInterval == 0;
    // Should a state message be emitted based on then last time a state message was emitted?
    final var emitStateDueToDuration = recordCount > 0 && Duration.between(lastCheckpoint, Instant.now()).compareTo(checkpointDuration) > 0;
    return emitStateDueToMessageCount || emitStateDueToDuration;
  }

}
