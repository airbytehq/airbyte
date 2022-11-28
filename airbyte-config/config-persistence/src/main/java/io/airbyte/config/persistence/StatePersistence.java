/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence;

import static io.airbyte.db.instance.configs.jooq.generated.Tables.STATE;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.enums.Enums;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.State;
import io.airbyte.config.StateType;
import io.airbyte.config.StateWrapper;
import io.airbyte.config.helpers.StateMessageHelper;
import io.airbyte.db.Database;
import io.airbyte.db.ExceptionWrappingDatabase;
import io.airbyte.protocol.models.AirbyteGlobalState;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.AirbyteStreamState;
import io.airbyte.protocol.models.StreamDescriptor;
import java.io.IOException;
import java.time.OffsetDateTime;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Collectors;
import org.jooq.DSLContext;
import org.jooq.JSONB;
import org.jooq.Record;
import org.jooq.RecordMapper;
import org.jooq.impl.DSL;

/**
 * State Persistence
 *
 * Handle persisting States to the Database.
 *
 * Supports migration from Legacy to Global or Stream. Other type migrations need to go through a
 * reset. (an exception will be thrown)
 */
public class StatePersistence {

  private final ExceptionWrappingDatabase database;

  public StatePersistence(final Database database) {
    this.database = new ExceptionWrappingDatabase(database);
  }

  /**
   * Get the current State of a Connection
   *
   * @param connectionId
   * @return
   * @throws IOException
   */
  public Optional<StateWrapper> getCurrentState(final UUID connectionId) throws IOException {
    final List<StateRecord> records = this.database.query(ctx -> getStateRecords(ctx, connectionId));

    if (records.isEmpty()) {
      return Optional.empty();
    }

    return switch (getStateType(connectionId, records)) {
      case GLOBAL -> Optional.of(buildGlobalState(records));
      case STREAM -> Optional.of(buildStreamState(records));
      default -> Optional.of(buildLegacyState(records));
    };
  }

  /**
   * Create or update the states described in the StateWrapper. Null states will be deleted.
   *
   * The only state migrations supported are going from a Legacy state to either a Global or Stream
   * state. Other state type migrations should go through an explicit reset. An exception will be
   * thrown to prevent the system from getting into a bad state.
   *
   * @param connectionId
   * @param state
   * @throws IOException
   */
  public void updateOrCreateState(final UUID connectionId, final StateWrapper state)
      throws IOException {
    final Optional<StateWrapper> previousState = getCurrentState(connectionId);
    final StateType currentStateType = state.getStateType();
    final boolean isMigration = StateMessageHelper.isMigration(currentStateType, previousState);

    // The only case where we allow a state migration is moving from LEGACY.
    // We expect any other migration to go through an explicit reset.
    if (!isMigration && previousState.isPresent() && previousState.get().getStateType() != currentStateType) {
      throw new IllegalStateException("Unexpected type migration from '" + previousState.get().getStateType() + "' to '" + currentStateType +
          "'. Migration of StateType need to go through an explicit reset.");
    }

    this.database.transaction(ctx -> {
      if (isMigration) {
        clearLegacyState(ctx, connectionId);
      }
      switch (state.getStateType()) {
        case GLOBAL -> saveGlobalState(ctx, connectionId, state.getGlobal().getGlobal());
        case STREAM -> saveStreamState(ctx, connectionId, state.getStateMessages());
        case LEGACY -> saveLegacyState(ctx, connectionId, state.getLegacyState());
      }
      return null;
    });
  }

  private static void clearLegacyState(final DSLContext ctx, final UUID connectionId) {
    writeStateToDb(ctx, connectionId, null, null, StateType.LEGACY, null);
  }

  private static void saveGlobalState(final DSLContext ctx, final UUID connectionId, final AirbyteGlobalState globalState) {
    writeStateToDb(ctx, connectionId, null, null, StateType.GLOBAL, globalState.getSharedState());
    for (final AirbyteStreamState streamState : globalState.getStreamStates()) {
      writeStateToDb(ctx,
          connectionId,
          streamState.getStreamDescriptor().getName(),
          streamState.getStreamDescriptor().getNamespace(),
          StateType.GLOBAL,
          streamState.getStreamState());
    }
  }

  private static void saveStreamState(final DSLContext ctx, final UUID connectionId, final List<AirbyteStateMessage> stateMessages) {
    for (final AirbyteStateMessage stateMessage : stateMessages) {
      final AirbyteStreamState streamState = stateMessage.getStream();
      writeStateToDb(ctx,
          connectionId,
          streamState.getStreamDescriptor().getName(),
          streamState.getStreamDescriptor().getNamespace(),
          StateType.STREAM,
          streamState.getStreamState());
    }
  }

  private static void saveLegacyState(final DSLContext ctx, final UUID connectionId, final JsonNode state) {
    writeStateToDb(ctx, connectionId, null, null, StateType.LEGACY, state);
  }

  /**
   * Performs the actual SQL operation depending on the state
   *
   * If the state is null, it will delete the row, otherwise do an insert or update on conflict
   */
  static void writeStateToDb(final DSLContext ctx,
                             final UUID connectionId,
                             final String streamName,
                             final String namespace,
                             final StateType stateType,
                             final JsonNode state) {
    if (state != null) {
      final boolean hasState = ctx.selectFrom(STATE)
          .where(
              STATE.CONNECTION_ID.eq(connectionId),
              PersistenceHelpers.isNullOrEquals(STATE.STREAM_NAME, streamName),
              PersistenceHelpers.isNullOrEquals(STATE.NAMESPACE, namespace))
          .fetch().isNotEmpty();

      // NOTE: the legacy code was storing a State object instead of just the State data field. We kept
      // the same behavior for consistency.
      final JSONB jsonbState = JSONB.valueOf(Jsons.serialize(stateType != StateType.LEGACY ? state : new State().withState(state)));
      final OffsetDateTime now = OffsetDateTime.now();

      if (!hasState) {
        ctx.insertInto(STATE)
            .columns(
                STATE.ID,
                STATE.CREATED_AT,
                STATE.UPDATED_AT,
                STATE.CONNECTION_ID,
                STATE.STREAM_NAME,
                STATE.NAMESPACE,
                STATE.STATE_,
                STATE.TYPE)
            .values(
                UUID.randomUUID(),
                now,
                now,
                connectionId,
                streamName,
                namespace,
                jsonbState,
                Enums.convertTo(stateType, io.airbyte.db.instance.configs.jooq.generated.enums.StateType.class))
            .execute();

      } else {
        ctx.update(STATE)
            .set(STATE.UPDATED_AT, now)
            .set(STATE.STATE_, jsonbState)
            .where(
                STATE.CONNECTION_ID.eq(connectionId),
                PersistenceHelpers.isNullOrEquals(STATE.STREAM_NAME, streamName),
                PersistenceHelpers.isNullOrEquals(STATE.NAMESPACE, namespace))
            .execute();
      }

    } else {
      // If the state is null, we remove the state instead of keeping a null row
      ctx.deleteFrom(STATE)
          .where(
              STATE.CONNECTION_ID.eq(connectionId),
              PersistenceHelpers.isNullOrEquals(STATE.STREAM_NAME, streamName),
              PersistenceHelpers.isNullOrEquals(STATE.NAMESPACE, namespace))
          .execute();
    }
  }

  /**
   * Get the StateType for a given list of StateRecords
   *
   * @param connectionId The connectionId of the records, used to add more debugging context if an
   *        error is detected
   * @param records The list of StateRecords to process, must not be empty
   * @return the StateType of the records
   * @throws IllegalStateException If StateRecords have inconsistent types
   */
  @SuppressWarnings("PMD.AvoidLiteralsInIfCondition")
  private static io.airbyte.db.instance.configs.jooq.generated.enums.StateType getStateType(
                                                                                            final UUID connectionId,
                                                                                            final List<StateRecord> records) {
    final Set<io.airbyte.db.instance.configs.jooq.generated.enums.StateType> types =
        records.stream().map(r -> r.type).collect(Collectors.toSet());
    if (types.size() == 1) {
      return types.stream().findFirst().get();
    }

    throw new IllegalStateException("Inconsistent StateTypes for connectionId " + connectionId +
        " (" + String.join(", ", types.stream().map(stateType -> stateType.getLiteral()).toList()) + ")");
  }

  /**
   * Get the state records from the DB
   *
   * @param ctx A valid DSL context to use for the query
   * @param connectionId the ID of the connection
   * @return The StateRecords for the connectionId
   */
  private static List<StateRecord> getStateRecords(final DSLContext ctx, final UUID connectionId) {
    return ctx.select(DSL.asterisk())
        .from(STATE)
        .where(STATE.CONNECTION_ID.eq(connectionId))
        .fetch(getStateRecordMapper())
        .stream().toList();
  }

  /**
   * Build Global state
   *
   * The list of records can contain one global shared state that is the state without streamName and
   * without namespace The other records should be translated into AirbyteStreamState
   */
  private static StateWrapper buildGlobalState(final List<StateRecord> records) {
    // Split the global shared state from the other per stream records
    final Map<Boolean, List<StateRecord>> partitions = records.stream()
        .collect(Collectors.partitioningBy(r -> r.streamName == null && r.namespace == null));

    final AirbyteGlobalState globalState = new AirbyteGlobalState()
        .withSharedState(partitions.get(Boolean.TRUE).stream().map(r -> r.state).findFirst().orElse(null))
        .withStreamStates(partitions.get(Boolean.FALSE).stream().map(StatePersistence::buildAirbyteStreamState).toList());

    final AirbyteStateMessage msg = new AirbyteStateMessage()
        .withType(AirbyteStateType.GLOBAL)
        .withGlobal(globalState);
    return new StateWrapper().withStateType(StateType.GLOBAL).withGlobal(msg);
  }

  /**
   * Build StateWrapper for a PerStream state
   */
  private static StateWrapper buildStreamState(final List<StateRecord> records) {
    final List<AirbyteStateMessage> messages = records.stream().map(
        record -> new AirbyteStateMessage()
            .withType(AirbyteStateType.STREAM)
            .withStream(buildAirbyteStreamState(record)))
        .toList();
    return new StateWrapper().withStateType(StateType.STREAM).withStateMessages(messages);
  }

  /**
   * Build a StateWrapper for Legacy state
   */
  private static StateWrapper buildLegacyState(final List<StateRecord> records) {
    final State legacyState = Jsons.convertValue(records.get(0).state, State.class);
    return new StateWrapper()
        .withStateType(StateType.LEGACY)
        .withLegacyState(legacyState.getState());
  }

  /**
   * Convert a StateRecord to an AirbyteStreamState
   */
  private static AirbyteStreamState buildAirbyteStreamState(final StateRecord record) {
    return new AirbyteStreamState()
        .withStreamDescriptor(new StreamDescriptor().withName(record.streamName).withNamespace(record.namespace))
        .withStreamState(record.state);
  }

  private static RecordMapper<Record, StateRecord> getStateRecordMapper() {
    return record -> new StateRecord(
        record.get(STATE.TYPE, io.airbyte.db.instance.configs.jooq.generated.enums.StateType.class),
        record.get(STATE.STREAM_NAME, String.class),
        record.get(STATE.NAMESPACE, String.class),
        Jsons.deserialize(record.get(STATE.STATE_).data()));
  }

  private record StateRecord(
                             io.airbyte.db.instance.configs.jooq.generated.enums.StateType type,
                             String streamName,
                             String namespace,
                             JsonNode state) {}

}
