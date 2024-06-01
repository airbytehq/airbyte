/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.base.destination.typing_deduping

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.integrations.destination.StreamSyncSummary
import io.airbyte.integrations.base.destination.typing_deduping.Sql.Companion.of
import io.airbyte.integrations.base.destination.typing_deduping.Sql.Companion.separately
import io.airbyte.integrations.base.destination.typing_deduping.migrators.Migration
import io.airbyte.integrations.base.destination.typing_deduping.migrators.MinimumDestinationState
import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.airbyte.protocol.models.v0.StreamDescriptor
import java.time.Instant
import java.util.*
import java.util.Map
import java.util.function.Consumer
import kotlin.collections.HashMap
import kotlin.collections.List
import kotlin.collections.MutableMap
import kotlin.collections.emptyList
import kotlin.collections.listOf
import kotlin.collections.set
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.mockito.ArgumentMatchers
import org.mockito.Mockito
import org.mockito.Mockito.mock
import org.mockito.kotlin.any

class DefaultTyperDeduperTest {
    private lateinit var parsedCatalog: ParsedCatalog

    private data class MockState(
        val needsSoftReset: Boolean,
        val softResetMigrationCompleted: Boolean,
        val nonSoftResetMigrationCompleted: Boolean
    ) : MinimumDestinationState {
        override fun needsSoftReset(): Boolean = needsSoftReset

        override fun <T : MinimumDestinationState> withSoftReset(needsSoftReset: Boolean): T {
            @Suppress("UNCHECKED_CAST")
            return MockState(
                needsSoftReset,
                this.softResetMigrationCompleted,
                this.nonSoftResetMigrationCompleted
            )
                as T
        }
    }

    private lateinit var sqlGenerator: MockSqlGenerator
    private lateinit var destinationHandler: DestinationHandler<MockState>

    private lateinit var initialStates: List<DestinationInitialStatus<MockState>>
    private lateinit var updatedStates: MutableMap<StreamId, MockState>

    private lateinit var migrator: DestinationV1V2Migrator
    private lateinit var typerDeduper: TyperDeduper

    private val MIGRATION_REQUIRING_SOFT_RESET: Migration<MockState> =
        object : Migration<MockState> {
            override fun migrateIfNecessary(
                destinationHandler: DestinationHandler<MockState>,
                stream: StreamConfig,
                state: DestinationInitialStatus<MockState>
            ): Migration.MigrationResult<MockState> {
                destinationHandler.execute(of("MIGRATE " + stream.id.rawTableId("")))
                return Migration.MigrationResult(
                    MockState(true, true, state.destinationState.nonSoftResetMigrationCompleted),
                    false
                )
            }
        }

    private val MIGRATION_NOT_REQUIRING_SOFT_RESET: Migration<MockState> =
        object : Migration<MockState> {
            override fun migrateIfNecessary(
                destinationHandler: DestinationHandler<MockState>,
                stream: StreamConfig,
                state: DestinationInitialStatus<MockState>
            ): Migration.MigrationResult<MockState> {
                return Migration.MigrationResult(
                    MockState(
                        state.destinationState.needsSoftReset,
                        state.destinationState.softResetMigrationCompleted,
                        true
                    ),
                    false
                )
            }
        }

    // Something about the Mockito.when(...).thenReturn(initialStates) call is tripping spotbugs,
    // even though we're not doing an explicit null check anywhere. So suppress it.
    @SuppressFBWarnings("RCN_REDUNDANT_NULLCHECK_OF_NONNULL_VALUE")
    @BeforeEach
    @Throws(Exception::class)
    fun setup() {
        sqlGenerator = Mockito.spy(MockSqlGenerator())
        destinationHandler = mock()

        val overwriteNsState: DestinationInitialStatus<MockState> = mock()
        Mockito.`when`(overwriteNsState.destinationState).thenReturn(MockState(false, false, true))
        Mockito.`when`(overwriteNsState.streamConfig).thenReturn(OVERWRITE_STREAM_CONFIG)

        val appendNsState: DestinationInitialStatus<MockState> = mock()
        Mockito.`when`(appendNsState.destinationState).thenReturn(MockState(false, false, true))
        Mockito.`when`(appendNsState.streamConfig).thenReturn(APPEND_STREAM_CONFIG)

        val dedupeNsState: DestinationInitialStatus<MockState> = mock()
        Mockito.`when`(dedupeNsState.destinationState).thenReturn(MockState(false, false, true))
        Mockito.`when`(dedupeNsState.streamConfig).thenReturn(DEDUPE_STREAM_CONFIG)

        initialStates = listOf(overwriteNsState, appendNsState, dedupeNsState)
        Mockito.`when`(destinationHandler.gatherInitialState(ArgumentMatchers.anyList()))
            .thenReturn(initialStates)
        initialStates.forEach(
            Consumer { initialState: DestinationInitialStatus<MockState> ->
                Mockito.`when`(initialState.initialRawTableStatus)
                    .thenReturn(InitialRawTableStatus(true, true, Optional.empty()))
            }
        )

        val updatedStates: MutableMap<StreamId, MockState> = HashMap()
        updatedStates[OVERWRITE_STREAM_CONFIG.id] = MockState(false, false, true)
        updatedStates[APPEND_STREAM_CONFIG.id] = MockState(false, false, true)
        updatedStates[DEDUPE_STREAM_CONFIG.id] = MockState(false, false, true)
        this.updatedStates = updatedStates

        migrator = NoOpDestinationV1V2Migrator()

        parsedCatalog =
            ParsedCatalog(
                listOf(OVERWRITE_STREAM_CONFIG, APPEND_STREAM_CONFIG, DEDUPE_STREAM_CONFIG)
            )

        typerDeduper =
            DefaultTyperDeduper(
                sqlGenerator,
                destinationHandler,
                parsedCatalog,
                migrator,
                emptyList()
            )
    }

    /** When there are no existing tables, we should create them and write to them directly. */
    @Test
    @Throws(Exception::class)
    fun emptyDestination() {
        initialStates.forEach(
            Consumer { initialState: DestinationInitialStatus<MockState> ->
                Mockito.`when`(initialState.isFinalTablePresent).thenReturn(false)
            }
        )

        typerDeduper.prepareSchemasAndRunMigrations()
        Mockito.verify(destinationHandler)
            .execute(
                separately(
                    "CREATE SCHEMA airbyte_internal",
                    "CREATE SCHEMA overwrite_ns",
                    "CREATE SCHEMA append_ns",
                    "CREATE SCHEMA dedup_ns"
                )
            )
        Mockito.verify(destinationHandler).commitDestinationStates(updatedStates)
        Mockito.clearInvocations(destinationHandler)

        typerDeduper.prepareFinalTables()
        Mockito.verify(destinationHandler).execute(of("CREATE TABLE overwrite_ns.overwrite_stream"))
        Mockito.verify(destinationHandler).execute(of("CREATE TABLE append_ns.append_stream"))
        Mockito.verify(destinationHandler).execute(of("CREATE TABLE dedup_ns.dedup_stream"))
        Mockito.verify(destinationHandler).commitDestinationStates(updatedStates)
        Mockito.verifyNoMoreInteractions(*Mockito.ignoreStubs(destinationHandler))
        Mockito.clearInvocations(destinationHandler)

        typerDeduper.typeAndDedupe("overwrite_ns", "overwrite_stream")
        Mockito.verify(destinationHandler)
            .execute(of("UPDATE TABLE overwrite_ns.overwrite_stream WITHOUT SAFER CASTING"))
        typerDeduper.typeAndDedupe("append_ns", "append_stream")
        Mockito.verify(destinationHandler)
            .execute(of("UPDATE TABLE append_ns.append_stream WITHOUT SAFER CASTING"))
        typerDeduper.typeAndDedupe("dedup_ns", "dedup_stream")
        Mockito.verify(destinationHandler)
            .execute(of("UPDATE TABLE dedup_ns.dedup_stream WITHOUT SAFER CASTING"))
        Mockito.verifyNoMoreInteractions(*Mockito.ignoreStubs(destinationHandler))
        Mockito.clearInvocations(destinationHandler)

        typerDeduper.commitFinalTables()
        Mockito.verify(destinationHandler, Mockito.never()).execute(any())
    }

    /**
     * When there's an existing table but it's empty, we should ensure it has the right schema and
     * write to it directly.
     */
    @Test
    @Throws(Exception::class)
    fun existingEmptyTable() {
        initialStates.forEach(
            Consumer { initialState: DestinationInitialStatus<MockState> ->
                Mockito.`when`(initialState.isFinalTablePresent).thenReturn(true)
                Mockito.`when`(initialState.isFinalTableEmpty).thenReturn(true)
                Mockito.`when`(initialState.isSchemaMismatch).thenReturn(true)
            }
        )

        typerDeduper.prepareSchemasAndRunMigrations()
        Mockito.verify(destinationHandler)
            .execute(
                separately(
                    "CREATE SCHEMA airbyte_internal",
                    "CREATE SCHEMA overwrite_ns",
                    "CREATE SCHEMA append_ns",
                    "CREATE SCHEMA dedup_ns"
                )
            )
        Mockito.verify(destinationHandler).commitDestinationStates(updatedStates)
        Mockito.clearInvocations(destinationHandler)

        typerDeduper.prepareFinalTables()
        Mockito.verify(destinationHandler)
            .execute(of("CREATE TABLE overwrite_ns.overwrite_stream_airbyte_tmp"))
        Mockito.verify(destinationHandler)
            .execute(of("PREPARE append_ns.append_stream FOR SOFT RESET"))
        Mockito.verify(destinationHandler)
            .execute(of("UPDATE TABLE append_ns.append_stream_ab_soft_reset WITHOUT SAFER CASTING"))
        Mockito.verify(destinationHandler)
            .execute(
                of(
                    "OVERWRITE TABLE append_ns.append_stream FROM append_ns.append_stream_ab_soft_reset"
                )
            )
        Mockito.verify(destinationHandler)
            .execute(of("PREPARE dedup_ns.dedup_stream FOR SOFT RESET"))
        Mockito.verify(destinationHandler)
            .execute(of("UPDATE TABLE dedup_ns.dedup_stream_ab_soft_reset WITHOUT SAFER CASTING"))
        Mockito.verify(destinationHandler)
            .execute(
                of("OVERWRITE TABLE dedup_ns.dedup_stream FROM dedup_ns.dedup_stream_ab_soft_reset")
            )
        Mockito.verify(destinationHandler).commitDestinationStates(updatedStates)
        Mockito.verifyNoMoreInteractions(*Mockito.ignoreStubs(destinationHandler))
        Mockito.clearInvocations(destinationHandler)

        typerDeduper.typeAndDedupe("overwrite_ns", "overwrite_stream")
        Mockito.verify(destinationHandler)
            .execute(
                of("UPDATE TABLE overwrite_ns.overwrite_stream_airbyte_tmp WITHOUT SAFER CASTING")
            )
        typerDeduper.typeAndDedupe("append_ns", "append_stream")
        Mockito.verify(destinationHandler)
            .execute(of("UPDATE TABLE append_ns.append_stream WITHOUT SAFER CASTING"))
        typerDeduper.typeAndDedupe("dedup_ns", "dedup_stream")
        Mockito.verify(destinationHandler)
            .execute(of("UPDATE TABLE dedup_ns.dedup_stream WITHOUT SAFER CASTING"))
        Mockito.verifyNoMoreInteractions(*Mockito.ignoreStubs(destinationHandler))
        Mockito.clearInvocations(destinationHandler)

        typerDeduper.commitFinalTables()
        Mockito.verify(destinationHandler)
            .execute(
                of(
                    "OVERWRITE TABLE overwrite_ns.overwrite_stream FROM overwrite_ns.overwrite_stream_airbyte_tmp"
                )
            )
        Mockito.verifyNoMoreInteractions(*Mockito.ignoreStubs(destinationHandler))
    }

    /**
     * When there's an existing empty table with the right schema, we don't need to do anything
     * during setup.
     */
    @Test
    @Throws(Exception::class)
    fun existingEmptyTableMatchingSchema() {
        initialStates.forEach(
            Consumer { initialState: DestinationInitialStatus<MockState> ->
                Mockito.`when`(initialState.isFinalTablePresent).thenReturn(true)
                Mockito.`when`(initialState.isFinalTableEmpty).thenReturn(true)
                Mockito.`when`(initialState.isSchemaMismatch).thenReturn(false)
            }
        )

        typerDeduper.prepareSchemasAndRunMigrations()
        Mockito.verify(destinationHandler)
            .execute(
                separately(
                    "CREATE SCHEMA airbyte_internal",
                    "CREATE SCHEMA overwrite_ns",
                    "CREATE SCHEMA append_ns",
                    "CREATE SCHEMA dedup_ns"
                )
            )
        Mockito.clearInvocations(destinationHandler)

        typerDeduper.prepareFinalTables()
        Mockito.verify(destinationHandler, Mockito.never()).execute(any())
    }

    /**
     * When there's an existing nonempty table, we should alter it. For the OVERWRITE stream, we
     * also need to write to a tmp table, and overwrite the real table at the end of the sync.
     */
    @Test
    @Throws(Exception::class)
    fun existingNonemptyTable() {
        initialStates.forEach(
            Consumer { initialState: DestinationInitialStatus<MockState> ->
                Mockito.`when`(initialState.isFinalTablePresent).thenReturn(true)
                Mockito.`when`(initialState.isFinalTableEmpty).thenReturn(false)
                Mockito.`when`(initialState.isSchemaMismatch).thenReturn(true)
                Mockito.`when`(initialState.initialRawTableStatus)
                    .thenReturn(
                        InitialRawTableStatus(
                            true,
                            true,
                            Optional.of(Instant.parse("2023-01-01T12:34:56Z"))
                        )
                    )
            }
        )

        typerDeduper.prepareSchemasAndRunMigrations()
        Mockito.verify(destinationHandler)
            .execute(
                separately(
                    "CREATE SCHEMA airbyte_internal",
                    "CREATE SCHEMA overwrite_ns",
                    "CREATE SCHEMA append_ns",
                    "CREATE SCHEMA dedup_ns"
                )
            )
        Mockito.verify(destinationHandler).commitDestinationStates(updatedStates)
        Mockito.clearInvocations(destinationHandler)

        typerDeduper.prepareFinalTables()
        // NB: We only create a tmp table for the overwrite stream, and do _not_ soft reset the
        // existing
        // overwrite stream's table.
        Mockito.verify(destinationHandler)
            .execute(of("CREATE TABLE overwrite_ns.overwrite_stream_airbyte_tmp"))
        Mockito.verify(destinationHandler)
            .execute(of("PREPARE append_ns.append_stream FOR SOFT RESET"))
        Mockito.verify(destinationHandler)
            .execute(of("UPDATE TABLE append_ns.append_stream_ab_soft_reset WITHOUT SAFER CASTING"))
        Mockito.verify(destinationHandler)
            .execute(
                of(
                    "OVERWRITE TABLE append_ns.append_stream FROM append_ns.append_stream_ab_soft_reset"
                )
            )
        Mockito.verify(destinationHandler)
            .execute(of("PREPARE dedup_ns.dedup_stream FOR SOFT RESET"))
        Mockito.verify(destinationHandler)
            .execute(of("UPDATE TABLE dedup_ns.dedup_stream_ab_soft_reset WITHOUT SAFER CASTING"))
        Mockito.verify(destinationHandler)
            .execute(
                of("OVERWRITE TABLE dedup_ns.dedup_stream FROM dedup_ns.dedup_stream_ab_soft_reset")
            )
        Mockito.verify(destinationHandler).commitDestinationStates(updatedStates)
        Mockito.verifyNoMoreInteractions(*Mockito.ignoreStubs(destinationHandler))
        Mockito.clearInvocations(destinationHandler)

        typerDeduper.typeAndDedupe("overwrite_ns", "overwrite_stream")
        // NB: no airbyte_tmp suffix on the non-overwrite streams
        Mockito.verify(destinationHandler)
            .execute(
                of(
                    "UPDATE TABLE overwrite_ns.overwrite_stream_airbyte_tmp WITHOUT SAFER CASTING WHERE extracted_at > 2023-01-01T12:34:56Z"
                )
            )
        typerDeduper.typeAndDedupe("append_ns", "append_stream")
        Mockito.verify(destinationHandler)
            .execute(
                of(
                    "UPDATE TABLE append_ns.append_stream WITHOUT SAFER CASTING WHERE extracted_at > 2023-01-01T12:34:56Z"
                )
            )
        typerDeduper.typeAndDedupe("dedup_ns", "dedup_stream")
        Mockito.verify(destinationHandler)
            .execute(
                of(
                    "UPDATE TABLE dedup_ns.dedup_stream WITHOUT SAFER CASTING WHERE extracted_at > 2023-01-01T12:34:56Z"
                )
            )
        Mockito.verifyNoMoreInteractions(*Mockito.ignoreStubs(destinationHandler))
        Mockito.clearInvocations(destinationHandler)

        typerDeduper.commitFinalTables()
        Mockito.verify(destinationHandler)
            .execute(
                of(
                    "OVERWRITE TABLE overwrite_ns.overwrite_stream FROM overwrite_ns.overwrite_stream_airbyte_tmp"
                )
            )
        Mockito.verifyNoMoreInteractions(*Mockito.ignoreStubs(destinationHandler))
    }

    /**
     * When there's an existing nonempty table with the right schema, we don't need to modify it,
     * but OVERWRITE streams still need to create a tmp table.
     */
    @Test
    @Throws(Exception::class)
    fun existingNonemptyTableMatchingSchema() {
        initialStates.forEach(
            Consumer { initialState: DestinationInitialStatus<MockState> ->
                Mockito.`when`(initialState.isFinalTablePresent).thenReturn(true)
                Mockito.`when`(initialState.isFinalTableEmpty).thenReturn(false)
                Mockito.`when`(initialState.isSchemaMismatch).thenReturn(false)
                Mockito.`when`(initialState.initialRawTableStatus)
                    .thenReturn(InitialRawTableStatus(true, true, Optional.of(Instant.now())))
            }
        )

        typerDeduper.prepareSchemasAndRunMigrations()
        Mockito.verify(destinationHandler)
            .execute(
                separately(
                    "CREATE SCHEMA airbyte_internal",
                    "CREATE SCHEMA overwrite_ns",
                    "CREATE SCHEMA append_ns",
                    "CREATE SCHEMA dedup_ns"
                )
            )
        Mockito.verify(destinationHandler).commitDestinationStates(updatedStates)
        Mockito.clearInvocations(destinationHandler)

        typerDeduper.prepareFinalTables()
        // NB: We only create one tmp table here.
        // Also, we need to alter the existing _real_ table, not the tmp table!
        Mockito.verify(destinationHandler)
            .execute(of("CREATE TABLE overwrite_ns.overwrite_stream_airbyte_tmp"))
        Mockito.verify(destinationHandler).commitDestinationStates(updatedStates)
        Mockito.verifyNoMoreInteractions(*Mockito.ignoreStubs(destinationHandler))
    }

    @Test
    fun nonexistentStream() {
        Assertions.assertThrows(IllegalArgumentException::class.java) {
            typerDeduper.typeAndDedupe("nonexistent_ns", "nonexistent_stream")
        }
        Mockito.verifyNoInteractions(*Mockito.ignoreStubs(destinationHandler))
    }

    @Test
    @Throws(Exception::class)
    fun failedSetup() {
        Mockito.doThrow(RuntimeException("foo")).`when`(destinationHandler).execute(any())

        Assertions.assertThrows(Exception::class.java) { typerDeduper.prepareFinalTables() }
        Mockito.clearInvocations(destinationHandler)

        typerDeduper.typeAndDedupe("dedup_ns", "dedup_stream")
        typerDeduper.commitFinalTables()

        Mockito.verifyNoInteractions(*Mockito.ignoreStubs(destinationHandler))
    }

    /**
     * Test a typical sync, where the previous sync left no unprocessed raw records. If this sync
     * writes some records for a stream, we should run T+D for that stream.
     */
    @Test
    @Throws(Exception::class)
    fun noUnprocessedRecords() {
        initialStates.forEach(
            Consumer { initialState: DestinationInitialStatus<MockState> ->
                Mockito.`when`(initialState.initialRawTableStatus)
                    .thenReturn(InitialRawTableStatus(true, false, Optional.empty()))
            }
        )

        typerDeduper.prepareSchemasAndRunMigrations()

        typerDeduper.prepareFinalTables()
        Mockito.clearInvocations(destinationHandler)

        typerDeduper.typeAndDedupe(
            Map.of(
                StreamDescriptor().withName("overwrite_stream").withNamespace("overwrite_ns"),
                StreamSyncSummary(Optional.of(0L)),
                StreamDescriptor().withName("append_stream").withNamespace("append_ns"),
                StreamSyncSummary(Optional.of(1L))
            )
        )

        // append_stream and dedup_stream should be T+D-ed. overwrite_stream has explicitly 0
        // records, but
        // dedup_stream
        // is missing from the map, so implicitly has nonzero records.
        Mockito.verify(destinationHandler)
            .execute(of("UPDATE TABLE append_ns.append_stream WITHOUT SAFER CASTING"))
        Mockito.verify(destinationHandler)
            .execute(of("UPDATE TABLE dedup_ns.dedup_stream WITHOUT SAFER CASTING"))
        Mockito.verifyNoMoreInteractions(destinationHandler)
    }

    /**
     * Test a sync where the previous sync failed to run T+D for some stream. Even if this sync
     * writes zero records, it should still run T+D.
     */
    @Test
    @Throws(Exception::class)
    fun unprocessedRecords() {
        initialStates.forEach(
            Consumer { initialState: DestinationInitialStatus<MockState> ->
                Mockito.`when`(initialState.initialRawTableStatus)
                    .thenReturn(
                        InitialRawTableStatus(
                            true,
                            true,
                            Optional.of(Instant.parse("2023-01-23T12:34:56Z"))
                        )
                    )
            }
        )

        typerDeduper.prepareSchemasAndRunMigrations()

        typerDeduper.prepareFinalTables()
        Mockito.clearInvocations(destinationHandler)

        typerDeduper.typeAndDedupe(
            Map.of(
                StreamDescriptor().withName("overwrite_stream").withNamespace("overwrite_ns"),
                StreamSyncSummary(Optional.of(0L)),
                StreamDescriptor().withName("append_stream").withNamespace("append_ns"),
                StreamSyncSummary(Optional.of(1L))
            )
        )

        Mockito.verify(destinationHandler)
            .execute(
                of(
                    "UPDATE TABLE overwrite_ns.overwrite_stream WITHOUT SAFER CASTING WHERE extracted_at > 2023-01-23T12:34:56Z"
                )
            )
        Mockito.verify(destinationHandler)
            .execute(
                of(
                    "UPDATE TABLE append_ns.append_stream WITHOUT SAFER CASTING WHERE extracted_at > 2023-01-23T12:34:56Z"
                )
            )
        Mockito.verify(destinationHandler)
            .execute(
                of(
                    "UPDATE TABLE dedup_ns.dedup_stream WITHOUT SAFER CASTING WHERE extracted_at > 2023-01-23T12:34:56Z"
                )
            )
    }

    /**
     * A test that tries to trigger multiple soft resets on all three streams. The migration should
     * run, and we also detect a schema mismatch. However, only one soft reset should be triggered
     * once per stream. Additionally, the overwrite stream should not trigger a soft reset.
     */
    @Test
    @Throws(Exception::class)
    fun multipleSoftResets() {
        val typerDeduper =
            DefaultTyperDeduper(
                sqlGenerator,
                destinationHandler,
                parsedCatalog,
                migrator,
                listOf(MIGRATION_REQUIRING_SOFT_RESET)
            )

        this.typerDeduper = typerDeduper
        // Notably: isSchemaMismatch = true,
        // and the MockStates have needsSoftReset = false and isMigrated = false.
        Mockito.`when`(destinationHandler.gatherInitialState(ArgumentMatchers.anyList()))
            .thenReturn(
                listOf(
                    DestinationInitialStatus(
                        OVERWRITE_STREAM_CONFIG,
                        true,
                        InitialRawTableStatus(true, true, Optional.of(Instant.ofEpochMilli(42))),
                        true,
                        false,
                        MockState(false, false, true)
                    ),
                    DestinationInitialStatus(
                        APPEND_STREAM_CONFIG,
                        true,
                        InitialRawTableStatus(true, true, Optional.of(Instant.ofEpochMilli(42))),
                        true,
                        false,
                        MockState(false, false, true)
                    ),
                    DestinationInitialStatus(
                        DEDUPE_STREAM_CONFIG,
                        true,
                        InitialRawTableStatus(true, true, Optional.of(Instant.ofEpochMilli(42))),
                        true,
                        false,
                        MockState(false, false, true)
                    )
                )
            )

        typerDeduper.prepareSchemasAndRunMigrations()
        Mockito.verify(destinationHandler).execute(of("MIGRATE airbyte_internal.overwrite_stream"))
        Mockito.verify(destinationHandler).execute(of("MIGRATE airbyte_internal.append_stream"))
        Mockito.verify(destinationHandler).execute(of("MIGRATE airbyte_internal.dedup_stream"))
        Mockito.verify(destinationHandler)
            .commitDestinationStates(
                Map.of(
                    OVERWRITE_STREAM_CONFIG.id,
                    MockState(true, true, true),
                    APPEND_STREAM_CONFIG.id,
                    MockState(true, true, true),
                    DEDUPE_STREAM_CONFIG.id,
                    MockState(true, true, true)
                )
            )
        Mockito.verify(destinationHandler).gatherInitialState(any())
        Mockito.verify(destinationHandler)
            .execute(
                separately(
                    "CREATE SCHEMA airbyte_internal",
                    "CREATE SCHEMA overwrite_ns",
                    "CREATE SCHEMA append_ns",
                    "CREATE SCHEMA dedup_ns"
                )
            )
        Mockito.verifyNoMoreInteractions(destinationHandler)
        Mockito.clearInvocations(destinationHandler)

        typerDeduper.prepareFinalTables()

        // We should trigger a soft reset on the append + dedup streams.
        Mockito.verify(destinationHandler)
            .execute(of("PREPARE append_ns.append_stream FOR SOFT RESET"))
        Mockito.verify(destinationHandler)
            .execute(of("UPDATE TABLE append_ns.append_stream_ab_soft_reset WITHOUT SAFER CASTING"))
        Mockito.verify(destinationHandler)
            .execute(
                of(
                    "OVERWRITE TABLE append_ns.append_stream FROM append_ns.append_stream_ab_soft_reset"
                )
            )

        Mockito.verify(destinationHandler)
            .execute(of("PREPARE dedup_ns.dedup_stream FOR SOFT RESET"))
        Mockito.verify(destinationHandler)
            .execute(of("UPDATE TABLE dedup_ns.dedup_stream_ab_soft_reset WITHOUT SAFER CASTING"))
        Mockito.verify(destinationHandler)
            .execute(
                of("OVERWRITE TABLE dedup_ns.dedup_stream FROM dedup_ns.dedup_stream_ab_soft_reset")
            )

        // The overwrite stream just gets a new table entirely, instead of a soft reset.
        Mockito.verify(destinationHandler)
            .execute(of("CREATE TABLE overwrite_ns.overwrite_stream_airbyte_tmp"))

        // And we should commit the states. Note that we now set needsSoftReset=false.
        Mockito.verify(destinationHandler)
            .commitDestinationStates(
                Map.of(
                    OVERWRITE_STREAM_CONFIG.id,
                    MockState(false, true, true),
                    APPEND_STREAM_CONFIG.id,
                    MockState(false, true, true),
                    DEDUPE_STREAM_CONFIG.id,
                    MockState(false, true, true)
                )
            )

        Mockito.verifyNoMoreInteractions(destinationHandler)
    }

    /**
     * A test where we have multiple migrations. The first migration triggers a soft reset; the
     * second migration does nothing. We should correctly trigger the soft reset.
     */
    @Test
    @Throws(Exception::class)
    fun migrationsMixedResults() {
        val typerDeduper =
            DefaultTyperDeduper(
                sqlGenerator,
                destinationHandler,
                parsedCatalog,
                migrator,
                listOf(MIGRATION_REQUIRING_SOFT_RESET, MIGRATION_NOT_REQUIRING_SOFT_RESET)
            )
        this.typerDeduper = typerDeduper

        Mockito.`when`(destinationHandler.gatherInitialState(ArgumentMatchers.anyList()))
            .thenReturn(
                listOf(
                    DestinationInitialStatus(
                        OVERWRITE_STREAM_CONFIG,
                        true,
                        InitialRawTableStatus(true, true, Optional.of(Instant.ofEpochMilli(42))),
                        false,
                        false,
                        MockState(false, false, false)
                    ),
                    DestinationInitialStatus(
                        APPEND_STREAM_CONFIG,
                        true,
                        InitialRawTableStatus(true, true, Optional.of(Instant.ofEpochMilli(42))),
                        false,
                        false,
                        MockState(false, false, false)
                    ),
                    DestinationInitialStatus(
                        DEDUPE_STREAM_CONFIG,
                        true,
                        InitialRawTableStatus(true, true, Optional.of(Instant.ofEpochMilli(42))),
                        false,
                        false,
                        MockState(false, false, false)
                    )
                )
            )

        typerDeduper.prepareSchemasAndRunMigrations()
        Mockito.verify(destinationHandler).execute(of("MIGRATE airbyte_internal.overwrite_stream"))
        Mockito.verify(destinationHandler).execute(of("MIGRATE airbyte_internal.append_stream"))
        Mockito.verify(destinationHandler).execute(of("MIGRATE airbyte_internal.dedup_stream"))
        Mockito.verify(destinationHandler)
            .commitDestinationStates(
                Map.of(
                    OVERWRITE_STREAM_CONFIG.id,
                    MockState(true, true, true),
                    APPEND_STREAM_CONFIG.id,
                    MockState(true, true, true),
                    DEDUPE_STREAM_CONFIG.id,
                    MockState(true, true, true)
                )
            )
        Mockito.verify(destinationHandler).gatherInitialState(any())
        Mockito.verify(destinationHandler)
            .execute(
                separately(
                    "CREATE SCHEMA airbyte_internal",
                    "CREATE SCHEMA overwrite_ns",
                    "CREATE SCHEMA append_ns",
                    "CREATE SCHEMA dedup_ns"
                )
            )
        Mockito.verifyNoMoreInteractions(destinationHandler)
        Mockito.clearInvocations(destinationHandler)

        typerDeduper.prepareFinalTables()

        // We should trigger a soft reset on the append + dedup streams.
        Mockito.verify(destinationHandler)
            .execute(of("PREPARE append_ns.append_stream FOR SOFT RESET"))
        Mockito.verify(destinationHandler)
            .execute(of("UPDATE TABLE append_ns.append_stream_ab_soft_reset WITHOUT SAFER CASTING"))
        Mockito.verify(destinationHandler)
            .execute(
                of(
                    "OVERWRITE TABLE append_ns.append_stream FROM append_ns.append_stream_ab_soft_reset"
                )
            )

        Mockito.verify(destinationHandler)
            .execute(of("PREPARE dedup_ns.dedup_stream FOR SOFT RESET"))
        Mockito.verify(destinationHandler)
            .execute(of("UPDATE TABLE dedup_ns.dedup_stream_ab_soft_reset WITHOUT SAFER CASTING"))
        Mockito.verify(destinationHandler)
            .execute(
                of("OVERWRITE TABLE dedup_ns.dedup_stream FROM dedup_ns.dedup_stream_ab_soft_reset")
            )

        // The overwrite stream just gets a new table
        Mockito.verify(destinationHandler)
            .execute(of("CREATE TABLE overwrite_ns.overwrite_stream_airbyte_tmp"))

        // And we should commit the states.
        Mockito.verify(destinationHandler)
            .commitDestinationStates(
                Map.of(
                    OVERWRITE_STREAM_CONFIG.id,
                    MockState(false, true, true),
                    APPEND_STREAM_CONFIG.id,
                    MockState(false, true, true),
                    DEDUPE_STREAM_CONFIG.id,
                    MockState(false, true, true)
                )
            )

        Mockito.verifyNoMoreInteractions(destinationHandler)
    }

    /**
     * A test where a previous sync committed a destination state with needsSoftReset=true. We
     * should trigger a soft reset, even though the current sync doesn't need it.
     */
    @Test
    @Throws(Exception::class)
    fun previousSyncSoftReset() {
        // Notably: isSchemaMismatch = false, but the MockStates have needsSoftReset = true.
        Mockito.`when`(destinationHandler.gatherInitialState(ArgumentMatchers.anyList()))
            .thenReturn(
                listOf(
                    DestinationInitialStatus(
                        OVERWRITE_STREAM_CONFIG,
                        true,
                        InitialRawTableStatus(true, true, Optional.of(Instant.ofEpochMilli(42))),
                        false,
                        false,
                        MockState(true, false, false)
                    ),
                    DestinationInitialStatus(
                        APPEND_STREAM_CONFIG,
                        true,
                        InitialRawTableStatus(true, true, Optional.of(Instant.ofEpochMilli(42))),
                        false,
                        false,
                        MockState(true, false, false)
                    ),
                    DestinationInitialStatus(
                        DEDUPE_STREAM_CONFIG,
                        true,
                        InitialRawTableStatus(true, true, Optional.of(Instant.ofEpochMilli(42))),
                        false,
                        false,
                        MockState(true, false, false)
                    )
                )
            )

        typerDeduper.prepareSchemasAndRunMigrations()
        // Even though we didn't do anything, we still commit the destination states.
        // This is technically unnecessary, but it's a single extra call and it's simpler to just do
        // it.
        Mockito.verify(destinationHandler)
            .commitDestinationStates(
                Map.of(
                    OVERWRITE_STREAM_CONFIG.id,
                    MockState(true, false, false),
                    APPEND_STREAM_CONFIG.id,
                    MockState(true, false, false),
                    DEDUPE_STREAM_CONFIG.id,
                    MockState(true, false, false)
                )
            )
        Mockito.verify(destinationHandler).gatherInitialState(any())
        Mockito.verify(destinationHandler)
            .execute(
                separately(
                    "CREATE SCHEMA airbyte_internal",
                    "CREATE SCHEMA overwrite_ns",
                    "CREATE SCHEMA append_ns",
                    "CREATE SCHEMA dedup_ns"
                )
            )
        Mockito.verifyNoMoreInteractions(destinationHandler)
        Mockito.clearInvocations(destinationHandler)

        typerDeduper.prepareFinalTables()

        // We should trigger a soft reset on the append + dedup streams.
        Mockito.verify(destinationHandler)
            .execute(of("PREPARE append_ns.append_stream FOR SOFT RESET"))
        Mockito.verify(destinationHandler)
            .execute(of("UPDATE TABLE append_ns.append_stream_ab_soft_reset WITHOUT SAFER CASTING"))
        Mockito.verify(destinationHandler)
            .execute(
                of(
                    "OVERWRITE TABLE append_ns.append_stream FROM append_ns.append_stream_ab_soft_reset"
                )
            )

        Mockito.verify(destinationHandler)
            .execute(of("PREPARE dedup_ns.dedup_stream FOR SOFT RESET"))
        Mockito.verify(destinationHandler)
            .execute(of("UPDATE TABLE dedup_ns.dedup_stream_ab_soft_reset WITHOUT SAFER CASTING"))
        Mockito.verify(destinationHandler)
            .execute(
                of("OVERWRITE TABLE dedup_ns.dedup_stream FROM dedup_ns.dedup_stream_ab_soft_reset")
            )

        // The overwrite stream just gets a new table entirely, instead of a soft reset.
        Mockito.verify(destinationHandler)
            .execute(of("CREATE TABLE overwrite_ns.overwrite_stream_airbyte_tmp"))

        // And we should commit the states. Note that we now set needsSoftReset=false.
        Mockito.verify(destinationHandler)
            .commitDestinationStates(
                Map.of(
                    OVERWRITE_STREAM_CONFIG.id,
                    MockState(false, false, false),
                    APPEND_STREAM_CONFIG.id,
                    MockState(false, false, false),
                    DEDUPE_STREAM_CONFIG.id,
                    MockState(false, false, false)
                )
            )

        Mockito.verifyNoMoreInteractions(destinationHandler)
    }

    companion object {
        private val OVERWRITE_STREAM_CONFIG =
            StreamConfig(
                StreamId(
                    "overwrite_ns",
                    "overwrite_stream",
                    "airbyte_internal",
                    "overwrite_stream",
                    "overwrite_ns",
                    "overwrite_stream"
                ),
                DestinationSyncMode.OVERWRITE,
                mock(),
                mock(),
                mock(),
                0,
                0,
                0,
            )
        private val APPEND_STREAM_CONFIG =
            StreamConfig(
                StreamId(
                    "append_ns",
                    "append_stream",
                    "airbyte_internal",
                    "append_stream",
                    "append_ns",
                    "append_stream"
                ),
                DestinationSyncMode.APPEND,
                mock(),
                mock(),
                mock(),
                0,
                0,
                0,
            )
        private val DEDUPE_STREAM_CONFIG =
            StreamConfig(
                StreamId(
                    "dedup_ns",
                    "dedup_stream",
                    "airbyte_internal",
                    "dedup_stream",
                    "dedup_ns",
                    "dedup_stream"
                ),
                DestinationSyncMode.APPEND_DEDUP,
                mock(),
                mock(),
                mock(),
                0,
                0,
                0,
            )
    }
}
