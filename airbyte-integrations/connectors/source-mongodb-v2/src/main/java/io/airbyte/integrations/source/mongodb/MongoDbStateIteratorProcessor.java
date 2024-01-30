package io.airbyte.integrations.source.mongodb;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.mongodb.client.MongoCursor;
import io.airbyte.cdk.integrations.debezium.CdcMetadataInjector;
import io.airbyte.integrations.source.mongodb.cdc.MongoDbCdcEventUtils;
import io.airbyte.cdk.integrations.source.relationaldb.state.SourceStateIteratorProcessor;
import io.airbyte.commons.exceptions.ConfigErrorException;
import io.airbyte.integrations.source.mongodb.state.IdType;
import io.airbyte.integrations.source.mongodb.state.InitialSnapshotStatus;
import io.airbyte.integrations.source.mongodb.state.MongoDbStateManager;
import io.airbyte.integrations.source.mongodb.state.MongoDbStreamState;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.time.Duration;
import java.time.Instant;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;
import java.util.stream.Collectors;
import org.bson.Document;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MongoDbStateIteratorProcessor implements SourceStateIteratorProcessor<AirbyteMessage> {

  private static final Logger LOGGER = LoggerFactory.getLogger(MongoDbStateIterator.class);

  private final MongoCursor<Document> iter;
  private final Optional<CdcMetadataInjector<?>> cdcMetadataInjector;
  private final MongoDbStateManager stateManager;
  private final ConfiguredAirbyteStream stream;
  private final Set<String> fields;
  private final Instant emittedAt;
  private final Integer checkpointInterval;
  private final Duration checkpointDuration;

  /**
   * Pointer to the last document _id seen by this iterator, necessary to track for state messages.
   */
  private Object lastId;

  /**
   * This iterator outputs a final state when the wrapped `iter` has concluded. When this is true, the
   * final message will be returned.
   */
  private boolean finalStateNext = false;

  /**
   * Tracks if the underlying iterator threw an exception. This helps to determine the final state
   * status emitted from the final next call.
   */
  private boolean iterThrewException = false;

  /**
   * Constructor.
   *
   * @param iter {@link MongoCursor} that iterates over Mongo documents
   * @param stateManager {@link MongoDbStateManager} that manages global and per-stream state
   * @param cdcMetadataInjector The {@link CdcMetadataInjector} used to add metadata to a published
   *        record.
   * @param stream the stream that this iterator represents
   * @param emittedAt when this iterator was started
   * @param checkpointInterval how often a state message should be emitted based on number of
   *        messages.
   * @param checkpointDuration how often a state message should be emitted based on time.
   */
  public MongoDbStateIteratorProcessor(final MongoCursor<Document> iter,
      final MongoDbStateManager stateManager,
      final Optional<CdcMetadataInjector<?>> cdcMetadataInjector,
      final ConfiguredAirbyteStream stream,
      final Instant emittedAt,
      final int checkpointInterval,
      final Duration checkpointDuration) {
    this.iter = iter;
    this.stateManager = stateManager;
    this.stream = stream;
    this.checkpointInterval = checkpointInterval;
    this.checkpointDuration = checkpointDuration;
    this.emittedAt = emittedAt;
    this.fields = CatalogHelpers.getTopLevelFieldNames(stream).stream().collect(Collectors.toSet());
    this.lastId =
        stateManager.getStreamState(stream.getStream().getName(), stream.getStream().getNamespace()).map(MongoDbStreamState::id).orElse(null);
    this.cdcMetadataInjector = cdcMetadataInjector;
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
      stateManager.updateStreamState(stream.getStream().getName(), stream.getStream().getNamespace(), state);
    }
    return stateManager.toState();
  }

  /**
   * @param message
   * @return
   */
  @Override
  public AirbyteMessage processRecordMessage(AirbyteMessage message) {
    final var document = iter.next();
    final var jsonNode = MongoDbCdcEventUtils.toJsonNode(document, fields);

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
      final var finalStateStatus = iterThrewException ? InitialSnapshotStatus.IN_PROGRESS : InitialSnapshotStatus.COMPLETE;
      final var idType = IdType.findByJavaType(lastId.getClass().getSimpleName())
          .orElseThrow(() -> new ConfigErrorException("Unsupported _id type " + lastId.getClass().getSimpleName()));
      final var state = new MongoDbStreamState(lastId.toString(), finalStateStatus, idType);

      stateManager.updateStreamState(stream.getStream().getName(), stream.getStream().getNamespace(), state);
    }
    return stateManager.toState();
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
