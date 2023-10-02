/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.mongodb.MongoException;
import com.mongodb.client.MongoCursor;
import io.airbyte.cdk.integrations.debezium.CdcMetadataInjector;
import io.airbyte.cdk.integrations.debezium.internals.mongodb.MongoDbCdcEventUtils;
import io.airbyte.commons.exceptions.ConfigErrorException;
import io.airbyte.integrations.source.mongodb.state.IdType;
import io.airbyte.integrations.source.mongodb.state.InitialSnapshotStatus;
import io.airbyte.integrations.source.mongodb.state.MongoDbStateManager;
import io.airbyte.integrations.source.mongodb.state.MongoDbStreamState;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.time.Duration;
import java.time.Instant;
import java.util.Iterator;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;
import java.util.stream.Collectors;
import org.bson.Document;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * A state-emitting iterator that emits a state message every checkpointInterval messages when
 * iterating over a MongoCursor.
 * <p>
 * Will also output a state message as the last message after the wrapper iterator has completed.
 */
public class MongoDbStateIterator implements Iterator<AirbyteMessage> {

  private static final Logger LOGGER = LoggerFactory.getLogger(MongoDbStateIterator.class);

  private final MongoCursor<Document> iter;
  private final Optional<CdcMetadataInjector<?>> cdcMetadataInjector;
  private final MongoDbStateManager stateManager;
  private final ConfiguredAirbyteStream stream;
  private final Set<String> fields;
  private final Instant emittedAt;
  private Instant lastCheckpoint = Instant.now();
  private final Integer checkpointInterval;
  private final Duration checkpointDuration;

  /**
   * Counts the number of records seen in this batch, resets when a state-message has been generated.
   */
  private int count = 0;

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
  public MongoDbStateIterator(final MongoCursor<Document> iter,
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

  @Override
  public boolean hasNext() {
    LOGGER.debug("Checking hasNext() for stream {}...", getStream());
    try {
      if (iter.hasNext()) {
        return true;
      }
    } catch (final MongoException e) {
      // If hasNext throws an exception, log it and then treat it as if hasNext returned false.
      iterThrewException = true;
      LOGGER.info("hasNext threw an exception for stream {}: {}", getStream(), e.getMessage(), e);
    }

    // no more records in cursor + no record messages have been emitted => collection is empty
    if (lastId == null) {
      return false;
    }

    // no more records in cursor + record messages have been emitted => we should emit a final state
    // message.
    if (!finalStateNext) {
      finalStateNext = true;
      LOGGER.debug("Final state is now true for stream {}...", getStream());
      return true;
    }

    return false;
  }

  @Override
  public AirbyteMessage next() {
    LOGGER.debug("Getting next message from stream {}...", getStream());
    // Should a state message be emitted based on the number of messages we've seen?
    final var emitStateDueToMessageCount = count > 0 && count % checkpointInterval == 0;
    // Should a state message be emitted based on then last time a state message was emitted?
    final var emitStateDueToDuration = count > 0 && Duration.between(lastCheckpoint, Instant.now()).compareTo(checkpointDuration) > 0;

    if (finalStateNext) {
      LOGGER.debug("Emitting final state status for stream {}:{}...", stream.getStream().getNamespace(), stream.getStream().getName());
      final var finalStateStatus = iterThrewException ? InitialSnapshotStatus.IN_PROGRESS : InitialSnapshotStatus.COMPLETE;
      final var idType = IdType.findByJavaType(lastId.getClass().getSimpleName())
          .orElseThrow(() -> new ConfigErrorException("Unsupported _id type " + lastId.getClass().getSimpleName()));
      final var state = new MongoDbStreamState(lastId.toString(), finalStateStatus, idType);

      stateManager.updateStreamState(stream.getStream().getName(), stream.getStream().getNamespace(), state);

      return new AirbyteMessage()
          .withType(Type.STATE)
          .withState(stateManager.toState());
    } else if (emitStateDueToMessageCount || emitStateDueToDuration) {
      count = 0;
      lastCheckpoint = Instant.now();

      if (lastId != null) {
        final var idType = IdType.findByJavaType(lastId.getClass().getSimpleName())
            .orElseThrow(() -> new ConfigErrorException("Unsupported _id type " + lastId.getClass().getSimpleName()));
        final var state = new MongoDbStreamState(lastId.toString(), InitialSnapshotStatus.IN_PROGRESS, idType);
        stateManager.updateStreamState(stream.getStream().getName(), stream.getStream().getNamespace(), state);
      }

      return new AirbyteMessage()
          .withType(Type.STATE)
          .withState(stateManager.toState());
    }

    count++;
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

  private String getStream() {
    return String.format("%s:%s", stream.getStream().getNamespace(), stream.getStream().getName());
  }

}
