/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping;

import static io.airbyte.integrations.base.destination.typing_deduping.Sql.separately;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyList;
import static org.mockito.Mockito.clearInvocations;
import static org.mockito.Mockito.doThrow;
import static org.mockito.Mockito.ignoreStubs;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.verifyNoInteractions;
import static org.mockito.Mockito.verifyNoMoreInteractions;
import static org.mockito.Mockito.when;

import io.airbyte.cdk.integrations.destination.StreamSyncSummary;
import io.airbyte.integrations.base.destination.typing_deduping.migrators.Migration;
import io.airbyte.integrations.base.destination.typing_deduping.migrators.MinimumDestinationState;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.time.Instant;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import lombok.SneakyThrows;
import org.jetbrains.annotations.NotNull;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

public class DefaultTyperDeduperTest {

  private ParsedCatalog parsedCatalog;
  private static final StreamConfig OVERWRITE_STREAM_CONFIG = new StreamConfig(
      new StreamId("overwrite_ns", "overwrite_stream", "airbyte_internal", "overwrite_stream", "overwrite_ns", "overwrite_stream"),
      null,
      DestinationSyncMode.OVERWRITE,
      null,
      null,
      null);
  private static final StreamConfig APPEND_STREAM_CONFIG = new StreamConfig(
      new StreamId("append_ns", "append_stream", "airbyte_internal", "append_stream", "append_ns", "append_stream"),
      null,
      DestinationSyncMode.APPEND,
      null,
      null,
      null);
  private static final StreamConfig DEDUPE_STREAM_CONFIG = new StreamConfig(
      new StreamId("dedup_ns", "dedup_stream", "airbyte_internal", "dedup_stream", "dedup_ns", "dedup_stream"),
      null,
      DestinationSyncMode.APPEND_DEDUP,
      null,
      null,
      null);

  private record MockState(
                           boolean needsSoftReset,
                           boolean softResetMigrationCompleted,
                           boolean nonSoftResetMigrationCompleted)
      implements MinimumDestinationState {

    @Override
    public MockState withSoftReset(boolean needsSoftReset) {
      return new MockState(needsSoftReset, this.softResetMigrationCompleted, this.nonSoftResetMigrationCompleted);
    }

  }

  private MockSqlGenerator sqlGenerator;
  private DestinationHandler<MockState> destinationHandler;

  private List<DestinationInitialStatus<MockState>> initialStates;
  private Map<StreamId, MockState> updatedStates;

  private DestinationV1V2Migrator migrator;
  private TyperDeduper typerDeduper;

  private final Migration<MockState> MIGRATION_REQUIRING_SOFT_RESET = new Migration<>() {

    @SneakyThrows
    @NotNull
    @Override
    public MigrationResult<MockState> migrateIfNecessary(DestinationHandler<MockState> destinationHandler,
                                                         @NotNull StreamConfig stream,
                                                         DestinationInitialStatus<MockState> state) {
      destinationHandler.execute(Sql.of("MIGRATE " + stream.id().rawTableId("")));
      return new MigrationResult<>(new MockState(true, true, state.destinationState().nonSoftResetMigrationCompleted), false);
    }

  };

  private final Migration<MockState> MIGRATION_NOT_REQUIRING_SOFT_RESET = new Migration<>() {

    @NotNull
    @Override
    public MigrationResult<MockState> migrateIfNecessary(@NotNull DestinationHandler<MockState> destinationHandler,
                                                         @NotNull StreamConfig stream,
                                                         DestinationInitialStatus<MockState> status) {
      return new MigrationResult<>(
          new MockState(
              status.destinationState().needsSoftReset,
              status.destinationState().softResetMigrationCompleted,
              true),
          false);
    }

  };

  private final Migration<MockState> MIGRATION_NOOP = new Migration<>() {

    @NotNull
    @Override
    public MigrationResult<MockState> migrateIfNecessary(@NotNull DestinationHandler<MockState> destinationHandler,
                                                         @NotNull StreamConfig stream,
                                                         DestinationInitialStatus<MockState> status) {
      return new MigrationResult<>(
          new MockState(
              status.destinationState().needsSoftReset,
              status.destinationState().softResetMigrationCompleted,
              true),
          false);
    }

  };

  @BeforeEach
  void setup() throws Exception {
    sqlGenerator = spy(new MockSqlGenerator());
    destinationHandler = mock(DestinationHandler.class);

    DestinationInitialStatus<MockState> overwriteNsState = mock(DestinationInitialStatus.class);
    when(overwriteNsState.destinationState()).thenReturn(new MockState(false, false, true));
    when(overwriteNsState.streamConfig()).thenReturn(OVERWRITE_STREAM_CONFIG);

    DestinationInitialStatus<MockState> appendNsState = mock(DestinationInitialStatus.class);
    when(appendNsState.destinationState()).thenReturn(new MockState(false, false, true));
    when(appendNsState.streamConfig()).thenReturn(APPEND_STREAM_CONFIG);

    DestinationInitialStatus<MockState> dedupeNsState = mock(DestinationInitialStatus.class);
    when(dedupeNsState.destinationState()).thenReturn(new MockState(false, false, true));
    when(dedupeNsState.streamConfig()).thenReturn(DEDUPE_STREAM_CONFIG);

    initialStates = List.of(overwriteNsState, appendNsState, dedupeNsState);
    when(destinationHandler.gatherInitialState(anyList()))
        .thenReturn(initialStates);
    initialStates
        .forEach(initialState -> when(initialState.initialRawTableStatus()).thenReturn(new InitialRawTableStatus(true, true, Optional.empty())));

    updatedStates = new HashMap<>();
    updatedStates.put(OVERWRITE_STREAM_CONFIG.id(), new MockState(false, false, true));
    updatedStates.put(APPEND_STREAM_CONFIG.id(), new MockState(false, false, true));
    updatedStates.put(DEDUPE_STREAM_CONFIG.id(), new MockState(false, false, true));

    migrator = new NoOpDestinationV1V2Migrator();

    parsedCatalog = new ParsedCatalog(List.of(
        OVERWRITE_STREAM_CONFIG,
        APPEND_STREAM_CONFIG,
        DEDUPE_STREAM_CONFIG));

    typerDeduper = new DefaultTyperDeduper<>(sqlGenerator, destinationHandler, parsedCatalog, migrator, Collections.emptyList());
  }

  /**
   * When there are no existing tables, we should create them and write to them directly.
   */
  @Test
  void emptyDestination() throws Exception {
    initialStates.forEach(initialState -> when(initialState.isFinalTablePresent()).thenReturn(false));

    typerDeduper.prepareSchemasAndRunMigrations();
    verify(destinationHandler)
        .execute(separately("CREATE SCHEMA airbyte_internal", "CREATE SCHEMA overwrite_ns", "CREATE SCHEMA append_ns", "CREATE SCHEMA dedup_ns"));
    verify(destinationHandler).commitDestinationStates(updatedStates);
    clearInvocations(destinationHandler);

    typerDeduper.prepareFinalTables();
    verify(destinationHandler).execute(Sql.of("CREATE TABLE overwrite_ns.overwrite_stream"));
    verify(destinationHandler).execute(Sql.of("CREATE TABLE append_ns.append_stream"));
    verify(destinationHandler).execute(Sql.of("CREATE TABLE dedup_ns.dedup_stream"));
    verify(destinationHandler).commitDestinationStates(updatedStates);
    verifyNoMoreInteractions(ignoreStubs(destinationHandler));
    clearInvocations(destinationHandler);

    typerDeduper.typeAndDedupe("overwrite_ns", "overwrite_stream", false);
    verify(destinationHandler).execute(Sql.of("UPDATE TABLE overwrite_ns.overwrite_stream WITHOUT SAFER CASTING"));
    typerDeduper.typeAndDedupe("append_ns", "append_stream", false);
    verify(destinationHandler).execute(Sql.of("UPDATE TABLE append_ns.append_stream WITHOUT SAFER CASTING"));
    typerDeduper.typeAndDedupe("dedup_ns", "dedup_stream", false);
    verify(destinationHandler).execute(Sql.of("UPDATE TABLE dedup_ns.dedup_stream WITHOUT SAFER CASTING"));
    verifyNoMoreInteractions(ignoreStubs(destinationHandler));
    clearInvocations(destinationHandler);

    typerDeduper.commitFinalTables();
    verify(destinationHandler, never()).execute(any());
  }

  /**
   * When there's an existing table but it's empty, we should ensure it has the right schema and write
   * to it directly.
   */
  @Test
  void existingEmptyTable() throws Exception {
    initialStates.forEach(initialState -> {
      when(initialState.isFinalTablePresent()).thenReturn(true);
      when(initialState.isFinalTableEmpty()).thenReturn(true);
      when(initialState.isSchemaMismatch()).thenReturn(true);
    });

    typerDeduper.prepareSchemasAndRunMigrations();
    verify(destinationHandler)
        .execute(separately("CREATE SCHEMA airbyte_internal", "CREATE SCHEMA overwrite_ns", "CREATE SCHEMA append_ns", "CREATE SCHEMA dedup_ns"));
    verify(destinationHandler).commitDestinationStates(updatedStates);
    clearInvocations(destinationHandler);

    typerDeduper.prepareFinalTables();
    verify(destinationHandler).execute(Sql.of("CREATE TABLE overwrite_ns.overwrite_stream_airbyte_tmp"));
    verify(destinationHandler).execute(Sql.of("PREPARE append_ns.append_stream FOR SOFT RESET"));
    verify(destinationHandler).execute(Sql.of("UPDATE TABLE append_ns.append_stream_ab_soft_reset WITHOUT SAFER CASTING"));
    verify(destinationHandler).execute(Sql.of("OVERWRITE TABLE append_ns.append_stream FROM append_ns.append_stream_ab_soft_reset"));
    verify(destinationHandler).execute(Sql.of("PREPARE dedup_ns.dedup_stream FOR SOFT RESET"));
    verify(destinationHandler).execute(Sql.of("UPDATE TABLE dedup_ns.dedup_stream_ab_soft_reset WITHOUT SAFER CASTING"));
    verify(destinationHandler).execute(Sql.of("OVERWRITE TABLE dedup_ns.dedup_stream FROM dedup_ns.dedup_stream_ab_soft_reset"));
    verify(destinationHandler).commitDestinationStates(updatedStates);
    verifyNoMoreInteractions(ignoreStubs(destinationHandler));
    clearInvocations(destinationHandler);

    typerDeduper.typeAndDedupe("overwrite_ns", "overwrite_stream", false);
    verify(destinationHandler).execute(Sql.of("UPDATE TABLE overwrite_ns.overwrite_stream_airbyte_tmp WITHOUT SAFER CASTING"));
    typerDeduper.typeAndDedupe("append_ns", "append_stream", false);
    verify(destinationHandler).execute(Sql.of("UPDATE TABLE append_ns.append_stream WITHOUT SAFER CASTING"));
    typerDeduper.typeAndDedupe("dedup_ns", "dedup_stream", false);
    verify(destinationHandler).execute(Sql.of("UPDATE TABLE dedup_ns.dedup_stream WITHOUT SAFER CASTING"));
    verifyNoMoreInteractions(ignoreStubs(destinationHandler));
    clearInvocations(destinationHandler);

    typerDeduper.commitFinalTables();
    verify(destinationHandler).execute(Sql.of("OVERWRITE TABLE overwrite_ns.overwrite_stream FROM overwrite_ns.overwrite_stream_airbyte_tmp"));
    verifyNoMoreInteractions(ignoreStubs(destinationHandler));
  }

  /**
   * When there's an existing empty table with the right schema, we don't need to do anything during
   * setup.
   */
  @Test
  void existingEmptyTableMatchingSchema() throws Exception {
    initialStates.forEach(initialState -> {
      when(initialState.isFinalTablePresent()).thenReturn(true);
      when(initialState.isFinalTableEmpty()).thenReturn(true);
      when(initialState.isSchemaMismatch()).thenReturn(false);
    });

    typerDeduper.prepareSchemasAndRunMigrations();
    verify(destinationHandler)
        .execute(separately("CREATE SCHEMA airbyte_internal", "CREATE SCHEMA overwrite_ns", "CREATE SCHEMA append_ns", "CREATE SCHEMA dedup_ns"));
    clearInvocations(destinationHandler);

    typerDeduper.prepareFinalTables();
    verify(destinationHandler, never()).execute(any());
  }

  /**
   * When there's an existing nonempty table, we should alter it. For the OVERWRITE stream, we also
   * need to write to a tmp table, and overwrite the real table at the end of the sync.
   */
  @Test
  void existingNonemptyTable() throws Exception {
    initialStates.forEach(initialState -> {
      when(initialState.isFinalTablePresent()).thenReturn(true);
      when(initialState.isFinalTableEmpty()).thenReturn(false);
      when(initialState.isSchemaMismatch()).thenReturn(true);
      when(initialState.initialRawTableStatus())
          .thenReturn(new InitialRawTableStatus(true, true, Optional.of(Instant.parse("2023-01-01T12:34:56Z"))));
    });

    typerDeduper.prepareSchemasAndRunMigrations();
    verify(destinationHandler)
        .execute(separately("CREATE SCHEMA airbyte_internal", "CREATE SCHEMA overwrite_ns", "CREATE SCHEMA append_ns", "CREATE SCHEMA dedup_ns"));
    verify(destinationHandler).commitDestinationStates(updatedStates);
    clearInvocations(destinationHandler);

    typerDeduper.prepareFinalTables();
    // NB: We only create a tmp table for the overwrite stream, and do _not_ soft reset the existing
    // overwrite stream's table.
    verify(destinationHandler).execute(Sql.of("CREATE TABLE overwrite_ns.overwrite_stream_airbyte_tmp"));
    verify(destinationHandler).execute(Sql.of("PREPARE append_ns.append_stream FOR SOFT RESET"));
    verify(destinationHandler).execute(Sql.of("UPDATE TABLE append_ns.append_stream_ab_soft_reset WITHOUT SAFER CASTING"));
    verify(destinationHandler).execute(Sql.of("OVERWRITE TABLE append_ns.append_stream FROM append_ns.append_stream_ab_soft_reset"));
    verify(destinationHandler).execute(Sql.of("PREPARE dedup_ns.dedup_stream FOR SOFT RESET"));
    verify(destinationHandler).execute(Sql.of("UPDATE TABLE dedup_ns.dedup_stream_ab_soft_reset WITHOUT SAFER CASTING"));
    verify(destinationHandler).execute(Sql.of("OVERWRITE TABLE dedup_ns.dedup_stream FROM dedup_ns.dedup_stream_ab_soft_reset"));
    verify(destinationHandler).commitDestinationStates(updatedStates);
    verifyNoMoreInteractions(ignoreStubs(destinationHandler));
    clearInvocations(destinationHandler);

    typerDeduper.typeAndDedupe("overwrite_ns", "overwrite_stream", false);
    // NB: no airbyte_tmp suffix on the non-overwrite streams
    verify(destinationHandler)
        .execute(Sql.of("UPDATE TABLE overwrite_ns.overwrite_stream_airbyte_tmp WITHOUT SAFER CASTING WHERE extracted_at > 2023-01-01T12:34:56Z"));
    typerDeduper.typeAndDedupe("append_ns", "append_stream", false);
    verify(destinationHandler)
        .execute(Sql.of("UPDATE TABLE append_ns.append_stream WITHOUT SAFER CASTING WHERE extracted_at > 2023-01-01T12:34:56Z"));
    typerDeduper.typeAndDedupe("dedup_ns", "dedup_stream", false);
    verify(destinationHandler).execute(Sql.of("UPDATE TABLE dedup_ns.dedup_stream WITHOUT SAFER CASTING WHERE extracted_at > 2023-01-01T12:34:56Z"));
    verifyNoMoreInteractions(ignoreStubs(destinationHandler));
    clearInvocations(destinationHandler);

    typerDeduper.commitFinalTables();
    verify(destinationHandler).execute(Sql.of("OVERWRITE TABLE overwrite_ns.overwrite_stream FROM overwrite_ns.overwrite_stream_airbyte_tmp"));
    verifyNoMoreInteractions(ignoreStubs(destinationHandler));
  }

  /**
   * When there's an existing nonempty table with the right schema, we don't need to modify it, but
   * OVERWRITE streams still need to create a tmp table.
   */
  @Test
  void existingNonemptyTableMatchingSchema() throws Exception {
    initialStates.forEach(initialState -> {
      when(initialState.isFinalTablePresent()).thenReturn(true);
      when(initialState.isFinalTableEmpty()).thenReturn(false);
      when(initialState.isSchemaMismatch()).thenReturn(false);
      when(initialState.initialRawTableStatus()).thenReturn(new InitialRawTableStatus(true, true, Optional.of(Instant.now())));
    });

    typerDeduper.prepareSchemasAndRunMigrations();
    verify(destinationHandler)
        .execute(separately("CREATE SCHEMA airbyte_internal", "CREATE SCHEMA overwrite_ns", "CREATE SCHEMA append_ns", "CREATE SCHEMA dedup_ns"));
    verify(destinationHandler).commitDestinationStates(updatedStates);
    clearInvocations(destinationHandler);

    typerDeduper.prepareFinalTables();
    // NB: We only create one tmp table here.
    // Also, we need to alter the existing _real_ table, not the tmp table!
    verify(destinationHandler).execute(Sql.of("CREATE TABLE overwrite_ns.overwrite_stream_airbyte_tmp"));
    verify(destinationHandler).commitDestinationStates(updatedStates);
    verifyNoMoreInteractions(ignoreStubs(destinationHandler));
  }

  @Test
  void nonexistentStream() {
    assertThrows(IllegalArgumentException.class,
        () -> typerDeduper.typeAndDedupe("nonexistent_ns", "nonexistent_stream", false));
    verifyNoInteractions(ignoreStubs(destinationHandler));
  }

  @Test
  void failedSetup() throws Exception {
    doThrow(new RuntimeException("foo")).when(destinationHandler).execute(any());

    assertThrows(Exception.class, () -> typerDeduper.prepareFinalTables());
    clearInvocations(destinationHandler);

    typerDeduper.typeAndDedupe("dedup_ns", "dedup_stream", false);
    typerDeduper.commitFinalTables();

    verifyNoInteractions(ignoreStubs(destinationHandler));
  }

  /**
   * Test a typical sync, where the previous sync left no unprocessed raw records. If this sync writes
   * some records for a stream, we should run T+D for that stream.
   */
  @Test
  void noUnprocessedRecords() throws Exception {
    initialStates
        .forEach(initialState -> when(initialState.initialRawTableStatus()).thenReturn(new InitialRawTableStatus(true, false, Optional.empty())));

    typerDeduper.prepareSchemasAndRunMigrations();

    typerDeduper.prepareFinalTables();
    clearInvocations(destinationHandler);

    typerDeduper.typeAndDedupe(Map.of(
        new StreamDescriptor().withName("overwrite_stream").withNamespace("overwrite_ns"), new StreamSyncSummary(Optional.of(0L)),
        new StreamDescriptor().withName("append_stream").withNamespace("append_ns"), new StreamSyncSummary(Optional.of(1L))));

    // append_stream and dedup_stream should be T+D-ed. overwrite_stream has explicitly 0 records, but
    // dedup_stream
    // is missing from the map, so implicitly has nonzero records.
    verify(destinationHandler).execute(Sql.of("UPDATE TABLE append_ns.append_stream WITHOUT SAFER CASTING"));
    verify(destinationHandler).execute(Sql.of("UPDATE TABLE dedup_ns.dedup_stream WITHOUT SAFER CASTING"));
    verifyNoMoreInteractions(destinationHandler);
  }

  /**
   * Test a sync where the previous sync failed to run T+D for some stream. Even if this sync writes
   * zero records, it should still run T+D.
   */
  @Test
  void unprocessedRecords() throws Exception {
    initialStates.forEach(initialState -> when(initialState.initialRawTableStatus())
        .thenReturn(new InitialRawTableStatus(true, true, Optional.of(Instant.parse("2023-01-23T12:34:56Z")))));

    typerDeduper.prepareSchemasAndRunMigrations();

    typerDeduper.prepareFinalTables();
    clearInvocations(destinationHandler);

    typerDeduper.typeAndDedupe(Map.of(
        new StreamDescriptor().withName("overwrite_stream").withNamespace("overwrite_ns"), new StreamSyncSummary(Optional.of(0L)),
        new StreamDescriptor().withName("append_stream").withNamespace("append_ns"), new StreamSyncSummary(Optional.of(1L))));

    verify(destinationHandler)
        .execute(Sql.of("UPDATE TABLE overwrite_ns.overwrite_stream WITHOUT SAFER CASTING WHERE extracted_at > 2023-01-23T12:34:56Z"));
    verify(destinationHandler)
        .execute(Sql.of("UPDATE TABLE append_ns.append_stream WITHOUT SAFER CASTING WHERE extracted_at > 2023-01-23T12:34:56Z"));
    verify(destinationHandler).execute(Sql.of("UPDATE TABLE dedup_ns.dedup_stream WITHOUT SAFER CASTING WHERE extracted_at > 2023-01-23T12:34:56Z"));
  }

  /**
   * A test that tries to trigger multiple soft resets on all three streams. The migration should run,
   * and we also detect a schema mismatch. However, only one soft reset should be triggered once per
   * stream. Additionally, the overwrite stream should not trigger a soft reset.
   */
  @Test
  void multipleSoftResets() throws Exception {
    typerDeduper = new DefaultTyperDeduper<>(
        sqlGenerator,
        destinationHandler,
        parsedCatalog,
        migrator,
        List.of(MIGRATION_REQUIRING_SOFT_RESET));

    // Notably: isSchemaMismatch = true,
    // and the MockStates have needsSoftReset = false and isMigrated = false.
    when(destinationHandler.gatherInitialState(anyList()))
        .thenReturn(List.of(
            new DestinationInitialStatus<>(
                OVERWRITE_STREAM_CONFIG,
                true,
                new InitialRawTableStatus(true, true, Optional.of(Instant.ofEpochMilli(42))),
                true,
                false,
                new MockState(false, false, true)),
            new DestinationInitialStatus<>(
                APPEND_STREAM_CONFIG,
                true,
                new InitialRawTableStatus(true, true, Optional.of(Instant.ofEpochMilli(42))),
                true,
                false,
                new MockState(false, false, true)),
            new DestinationInitialStatus<>(
                DEDUPE_STREAM_CONFIG,
                true,
                new InitialRawTableStatus(true, true, Optional.of(Instant.ofEpochMilli(42))),
                true,
                false,
                new MockState(false, false, true))));

    typerDeduper.prepareSchemasAndRunMigrations();
    verify(destinationHandler).execute(Sql.of("MIGRATE airbyte_internal.overwrite_stream"));
    verify(destinationHandler).execute(Sql.of("MIGRATE airbyte_internal.append_stream"));
    verify(destinationHandler).execute(Sql.of("MIGRATE airbyte_internal.dedup_stream"));
    verify(destinationHandler).commitDestinationStates(Map.of(
        OVERWRITE_STREAM_CONFIG.id(), new MockState(true, true, true),
        APPEND_STREAM_CONFIG.id(), new MockState(true, true, true),
        DEDUPE_STREAM_CONFIG.id(), new MockState(true, true, true)));
    verify(destinationHandler).gatherInitialState(any());
    verify(destinationHandler)
        .execute(separately("CREATE SCHEMA airbyte_internal", "CREATE SCHEMA overwrite_ns", "CREATE SCHEMA append_ns", "CREATE SCHEMA dedup_ns"));
    verifyNoMoreInteractions(destinationHandler);
    clearInvocations(destinationHandler);

    typerDeduper.prepareFinalTables();

    // We should trigger a soft reset on the append + dedup streams.
    verify(destinationHandler).execute(Sql.of("PREPARE append_ns.append_stream FOR SOFT RESET"));
    verify(destinationHandler).execute(Sql.of("UPDATE TABLE append_ns.append_stream_ab_soft_reset WITHOUT SAFER CASTING"));
    verify(destinationHandler).execute(Sql.of("OVERWRITE TABLE append_ns.append_stream FROM append_ns.append_stream_ab_soft_reset"));

    verify(destinationHandler).execute(Sql.of("PREPARE dedup_ns.dedup_stream FOR SOFT RESET"));
    verify(destinationHandler).execute(Sql.of("UPDATE TABLE dedup_ns.dedup_stream_ab_soft_reset WITHOUT SAFER CASTING"));
    verify(destinationHandler).execute(Sql.of("OVERWRITE TABLE dedup_ns.dedup_stream FROM dedup_ns.dedup_stream_ab_soft_reset"));

    // The overwrite stream just gets a new table entirely, instead of a soft reset.
    verify(destinationHandler).execute(Sql.of("CREATE TABLE overwrite_ns.overwrite_stream_airbyte_tmp"));

    // And we should commit the states. Note that we now set needsSoftReset=false.
    verify(destinationHandler).commitDestinationStates(Map.of(
        OVERWRITE_STREAM_CONFIG.id(), new MockState(false, true, true),
        APPEND_STREAM_CONFIG.id(), new MockState(false, true, true),
        DEDUPE_STREAM_CONFIG.id(), new MockState(false, true, true)));

    verifyNoMoreInteractions(destinationHandler);
  }

  /**
   * A test where we have multiple migrations. The first migration triggers a soft reset; the second
   * migration does nothing. We should correctly trigger the soft reset.
   */
  @Test
  void migrationsMixedResults() throws Exception {
    typerDeduper = new DefaultTyperDeduper<>(
        sqlGenerator,
        destinationHandler,
        parsedCatalog,
        migrator,
        List.of(MIGRATION_REQUIRING_SOFT_RESET, MIGRATION_NOT_REQUIRING_SOFT_RESET));

    when(destinationHandler.gatherInitialState(anyList()))
        .thenReturn(List.of(
            new DestinationInitialStatus<>(
                OVERWRITE_STREAM_CONFIG,
                true,
                new InitialRawTableStatus(true, true, Optional.of(Instant.ofEpochMilli(42))),
                false,
                false,
                new MockState(false, false, false)),
            new DestinationInitialStatus<>(
                APPEND_STREAM_CONFIG,
                true,
                new InitialRawTableStatus(true, true, Optional.of(Instant.ofEpochMilli(42))),
                false,
                false,
                new MockState(false, false, false)),
            new DestinationInitialStatus<>(
                DEDUPE_STREAM_CONFIG,
                true,
                new InitialRawTableStatus(true, true, Optional.of(Instant.ofEpochMilli(42))),
                false,
                false,
                new MockState(false, false, false))));

    typerDeduper.prepareSchemasAndRunMigrations();
    verify(destinationHandler).execute(Sql.of("MIGRATE airbyte_internal.overwrite_stream"));
    verify(destinationHandler).execute(Sql.of("MIGRATE airbyte_internal.append_stream"));
    verify(destinationHandler).execute(Sql.of("MIGRATE airbyte_internal.dedup_stream"));
    verify(destinationHandler).commitDestinationStates(Map.of(
        OVERWRITE_STREAM_CONFIG.id(), new MockState(true, true, true),
        APPEND_STREAM_CONFIG.id(), new MockState(true, true, true),
        DEDUPE_STREAM_CONFIG.id(), new MockState(true, true, true)));
    verify(destinationHandler).gatherInitialState(any());
    verify(destinationHandler)
        .execute(separately("CREATE SCHEMA airbyte_internal", "CREATE SCHEMA overwrite_ns", "CREATE SCHEMA append_ns", "CREATE SCHEMA dedup_ns"));
    verifyNoMoreInteractions(destinationHandler);
    clearInvocations(destinationHandler);

    typerDeduper.prepareFinalTables();

    // We should trigger a soft reset on the append + dedup streams.
    verify(destinationHandler).execute(Sql.of("PREPARE append_ns.append_stream FOR SOFT RESET"));
    verify(destinationHandler).execute(Sql.of("UPDATE TABLE append_ns.append_stream_ab_soft_reset WITHOUT SAFER CASTING"));
    verify(destinationHandler).execute(Sql.of("OVERWRITE TABLE append_ns.append_stream FROM append_ns.append_stream_ab_soft_reset"));

    verify(destinationHandler).execute(Sql.of("PREPARE dedup_ns.dedup_stream FOR SOFT RESET"));
    verify(destinationHandler).execute(Sql.of("UPDATE TABLE dedup_ns.dedup_stream_ab_soft_reset WITHOUT SAFER CASTING"));
    verify(destinationHandler).execute(Sql.of("OVERWRITE TABLE dedup_ns.dedup_stream FROM dedup_ns.dedup_stream_ab_soft_reset"));

    // The overwrite stream just gets a new table
    verify(destinationHandler).execute(Sql.of("CREATE TABLE overwrite_ns.overwrite_stream_airbyte_tmp"));

    // And we should commit the states.
    verify(destinationHandler).commitDestinationStates(Map.of(
        OVERWRITE_STREAM_CONFIG.id(), new MockState(false, true, true),
        APPEND_STREAM_CONFIG.id(), new MockState(false, true, true),
        DEDUPE_STREAM_CONFIG.id(), new MockState(false, true, true)));

    verifyNoMoreInteractions(destinationHandler);
  }

  /**
   * A test where a previous sync committed a destination state with needsSoftReset=true. We should
   * trigger a soft reset, even though the current sync doesn't need it.
   */
  @Test
  void previousSyncSoftReset() throws Exception {
    // Notably: isSchemaMismatch = false, but the MockStates have needsSoftReset = true.
    when(destinationHandler.gatherInitialState(anyList()))
        .thenReturn(List.of(
            new DestinationInitialStatus<>(
                OVERWRITE_STREAM_CONFIG,
                true,
                new InitialRawTableStatus(true, true, Optional.of(Instant.ofEpochMilli(42))),
                false,
                false,
                new MockState(true, false, false)),
            new DestinationInitialStatus<>(
                APPEND_STREAM_CONFIG,
                true,
                new InitialRawTableStatus(true, true, Optional.of(Instant.ofEpochMilli(42))),
                false,
                false,
                new MockState(true, false, false)),
            new DestinationInitialStatus<>(
                DEDUPE_STREAM_CONFIG,
                true,
                new InitialRawTableStatus(true, true, Optional.of(Instant.ofEpochMilli(42))),
                false,
                false,
                new MockState(true, false, false))));

    typerDeduper.prepareSchemasAndRunMigrations();
    // Even though we didn't do anything, we still commit the destination states.
    // This is technically unnecessary, but it's a single extra call and it's simpler to just do it.
    verify(destinationHandler).commitDestinationStates(Map.of(
        OVERWRITE_STREAM_CONFIG.id(), new MockState(true, false, false),
        APPEND_STREAM_CONFIG.id(), new MockState(true, false, false),
        DEDUPE_STREAM_CONFIG.id(), new MockState(true, false, false)));
    verify(destinationHandler).gatherInitialState(any());
    verify(destinationHandler)
        .execute(separately("CREATE SCHEMA airbyte_internal", "CREATE SCHEMA overwrite_ns", "CREATE SCHEMA append_ns", "CREATE SCHEMA dedup_ns"));
    verifyNoMoreInteractions(destinationHandler);
    clearInvocations(destinationHandler);

    typerDeduper.prepareFinalTables();

    // We should trigger a soft reset on the append + dedup streams.
    verify(destinationHandler).execute(Sql.of("PREPARE append_ns.append_stream FOR SOFT RESET"));
    verify(destinationHandler).execute(Sql.of("UPDATE TABLE append_ns.append_stream_ab_soft_reset WITHOUT SAFER CASTING"));
    verify(destinationHandler).execute(Sql.of("OVERWRITE TABLE append_ns.append_stream FROM append_ns.append_stream_ab_soft_reset"));

    verify(destinationHandler).execute(Sql.of("PREPARE dedup_ns.dedup_stream FOR SOFT RESET"));
    verify(destinationHandler).execute(Sql.of("UPDATE TABLE dedup_ns.dedup_stream_ab_soft_reset WITHOUT SAFER CASTING"));
    verify(destinationHandler).execute(Sql.of("OVERWRITE TABLE dedup_ns.dedup_stream FROM dedup_ns.dedup_stream_ab_soft_reset"));

    // The overwrite stream just gets a new table entirely, instead of a soft reset.
    verify(destinationHandler).execute(Sql.of("CREATE TABLE overwrite_ns.overwrite_stream_airbyte_tmp"));

    // And we should commit the states. Note that we now set needsSoftReset=false.
    verify(destinationHandler).commitDestinationStates(Map.of(
        OVERWRITE_STREAM_CONFIG.id(), new MockState(false, false, false),
        APPEND_STREAM_CONFIG.id(), new MockState(false, false, false),
        DEDUPE_STREAM_CONFIG.id(), new MockState(false, false, false)));

    verifyNoMoreInteractions(destinationHandler);
  }

}
