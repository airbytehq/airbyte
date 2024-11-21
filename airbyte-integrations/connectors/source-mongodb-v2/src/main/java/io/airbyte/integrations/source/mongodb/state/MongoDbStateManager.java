/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.state;

import static io.airbyte.integrations.source.mongodb.state.IdType.idToStringRepresenation;
import static io.airbyte.integrations.source.mongodb.state.InitialSnapshotStatus.FULL_REFRESH;
import static io.airbyte.integrations.source.mongodb.state.InitialSnapshotStatus.IN_PROGRESS;
import static io.airbyte.protocol.models.v0.SyncMode.INCREMENTAL;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.cdk.integrations.debezium.CdcMetadataInjector;
import io.airbyte.cdk.integrations.source.relationaldb.state.SourceStateMessageProducer;
import io.airbyte.commons.exceptions.ConfigErrorException;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.mongodb.MongoConstants;
import io.airbyte.integrations.source.mongodb.MongoDbSourceConfig;
import io.airbyte.integrations.source.mongodb.cdc.MongoDbCdcConnectorMetadataInjector;
import io.airbyte.integrations.source.mongodb.cdc.MongoDbCdcEventUtils;
import io.airbyte.integrations.source.mongodb.cdc.MongoDbCdcState;
import io.airbyte.protocol.models.v0.*;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import java.time.Instant;
import java.util.*;
import java.util.stream.Collectors;
import org.bson.Document;
import org.bson.types.Binary;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * A state manager for MongoDB CDC syncs.
 */
public class MongoDbStateManager implements SourceStateMessageProducer<Document> {

  private static final Logger LOGGER = LoggerFactory.getLogger(MongoDbStateManager.class);

  /**
   * The global CDC state.
   */
  private MongoDbCdcState cdcState;

  private Instant emittedAt;
  private Optional<CdcMetadataInjector<?>> cdcMetadataInjector;
  private boolean isEnforceSchema;

  private Map<AirbyteStreamNameNamespacePair, Object> streamPairToLastIdMap;

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
  public static MongoDbStateManager createStateManager(final JsonNode initialState, final MongoDbSourceConfig config) {
    final MongoDbStateManager stateManager = new MongoDbStateManager();
    stateManager.streamPairToLastIdMap = new HashMap<>();
    stateManager.isEnforceSchema = config.getEnforceSchema();
    stateManager.emittedAt = Instant.now();
    stateManager.cdcMetadataInjector = Optional.of(MongoDbCdcConnectorMetadataInjector.getInstance(stateManager.emittedAt));

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
   * directly. Instead, use {@link #createStateManager(JsonNode, MongoDbSourceConfig)}.
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

  public void deleteStreamState(final String streamName, final String streamNamespace) {
    final AirbyteStreamNameNamespacePair airbyteStreamNameNamespacePair = new AirbyteStreamNameNamespacePair(streamName, streamNamespace);
    LOGGER.debug("Deleting stream state for stream {}:{} ...", streamNamespace, streamName);
    pairToStreamState.remove(airbyteStreamNameNamespacePair);
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

  /**
   * Generates an intermediate state message for checkpointing purpose.
   */
  @Override
  public AirbyteStateMessage generateStateMessageAtCheckpoint(final ConfiguredAirbyteStream stream) {
    final AirbyteStreamNameNamespacePair pair = new AirbyteStreamNameNamespacePair(stream.getStream().getName(), stream.getStream().getNamespace());
    final var syncMode = stream.getSyncMode();
    // Assuming we will always process at least 1 record message before sending out the state message.
    // shouldEmitStateMessage should guard this.
    var lastId = streamPairToLastIdMap.get(pair);
    if (lastId != null) {
      final var state = composeStateFromlastId(lastId, syncMode == INCREMENTAL ? IN_PROGRESS : FULL_REFRESH);
      updateStreamState(stream.getStream().getName(), stream.getStream().getNamespace(), state);
    }
    return toState();
  }

  /**
   * Process the record message and save last Id to the map.
   */
  @Override
  public AirbyteMessage processRecordMessage(final ConfiguredAirbyteStream stream, final Document document) {
    final var fields = CatalogHelpers.getTopLevelFieldNames(stream).stream().collect(Collectors.toSet());

    final var jsonNode = isEnforceSchema ? MongoDbCdcEventUtils.toJsonNode(document, fields) : MongoDbCdcEventUtils.toJsonNodeNoSchema(document);

    final var lastId = document.get(MongoConstants.ID_FIELD);
    final AirbyteStreamNameNamespacePair pair = new AirbyteStreamNameNamespacePair(stream.getStream().getName(), stream.getStream().getNamespace());
    streamPairToLastIdMap.put(pair, lastId);

    return new AirbyteMessage()
        .withType(Type.RECORD)
        .withRecord(new AirbyteRecordMessage()
            .withStream(stream.getStream().getName())
            .withNamespace(stream.getStream().getNamespace())
            .withEmittedAt(emittedAt.toEpochMilli())
            .withData((stream.getSyncMode() == INCREMENTAL) ? injectMetadata(jsonNode) : jsonNode));
  }

  private JsonNode injectMetadata(final JsonNode jsonNode) {
    if (Objects.nonNull(cdcMetadataInjector) && cdcMetadataInjector.isPresent() && jsonNode instanceof ObjectNode) {
      cdcMetadataInjector.get().addMetaDataToRowsFetchedOutsideDebezium((ObjectNode) jsonNode, emittedAt.toString(), null);
    }

    return jsonNode;
  }

  private MongoDbStreamState composeStateFromlastId(final Object lastId, final InitialSnapshotStatus status) {
    final var idType = IdType.findByJavaType(lastId.getClass().getSimpleName())
        .orElseThrow(() -> new ConfigErrorException("Unsupported _id type " + lastId.getClass().getSimpleName()));
    Byte binarySubType = 0;
    if (idType.equals(IdType.BINARY)) {
      final var binCurrentId = (Binary) lastId;
      binarySubType = binCurrentId.getType();
    }
    return new MongoDbStreamState(idToStringRepresenation(lastId, idType),
        status,
        idType,
        binarySubType);
  }

  /**
   * @return final state message.
   */
  @Override
  public AirbyteStateMessage createFinalStateMessage(final ConfiguredAirbyteStream stream) {
    if (stream.getSyncMode() == INCREMENTAL) {
      final AirbyteStreamNameNamespacePair pair = new AirbyteStreamNameNamespacePair(stream.getStream().getName(), stream.getStream().getNamespace());
      if (!streamPairToLastIdMap.containsKey(pair)) {
        var initialLastId = getStreamState(stream.getStream().getName(), stream.getStream().getNamespace()).map(MongoDbStreamState::id).orElse(null);
        streamPairToLastIdMap.put(pair, initialLastId);
      }
      var lastId = streamPairToLastIdMap.get(pair);
      if (lastId != null) {
        LOGGER.debug("Emitting final state status for stream {}:{}...", stream.getStream().getNamespace(), stream.getStream().getName());
        final var state = composeStateFromlastId(lastId, InitialSnapshotStatus.COMPLETE);
        updateStreamState(stream.getStream().getName(), stream.getStream().getNamespace(), state);
      }
    } else {
      final AirbyteStreamNameNamespacePair pair = new AirbyteStreamNameNamespacePair(stream.getStream().getName(), stream.getStream().getNamespace());
      var lastId = streamPairToLastIdMap.get(pair);
      if (lastId != null) {
        final var idType = IdType.findByJavaType(lastId.getClass().getSimpleName())
            .orElseThrow(() -> new ConfigErrorException("Unsupported _id type " + lastId.getClass().getSimpleName()));
        updateStreamState(stream.getStream().getName(), stream.getStream().getNamespace(),
            composeStateFromlastId(lastId, InitialSnapshotStatus.FULL_REFRESH));
      }
    }
    return toState();
  }

  /**
   * Make sure we have processed at least 1 record from the stream.
   */
  @Override
  public boolean shouldEmitStateMessage(final ConfiguredAirbyteStream stream) {
    return streamPairToLastIdMap.get(new AirbyteStreamNameNamespacePair(stream.getStream().getName(), stream.getStream().getNamespace())) != null;
  }

}
