/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.operation

import io.airbyte.cdk.integrations.destination.StreamSyncSummary
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage
import io.airbyte.integrations.base.destination.typing_deduping.DestinationHandler
import io.airbyte.integrations.base.destination.typing_deduping.DestinationInitialStatus
import io.airbyte.integrations.base.destination.typing_deduping.InitialRawTableStatus
import io.airbyte.integrations.base.destination.typing_deduping.ParsedCatalog
import io.airbyte.integrations.base.destination.typing_deduping.Sql
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig
import io.airbyte.integrations.base.destination.typing_deduping.StreamId
import io.airbyte.integrations.base.destination.typing_deduping.migrators.Migration
import io.airbyte.integrations.base.destination.typing_deduping.migrators.MinimumDestinationState
import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.mockk.clearMocks
import io.mockk.confirmVerified
import io.mockk.every
import io.mockk.mockk
import io.mockk.spyk
import io.mockk.verify
import io.mockk.verifySequence
import java.util.Optional
import java.util.stream.Stream
import kotlin.test.assertEquals
import org.junit.jupiter.api.Test

/**
 * All of these tests use APPEND sync mode for simplicity.
 * [io.airbyte.cdk.integrations.destination.operation.SyncOperation] doesn't care about sync mode;
 * all of that logic lives in [StreamOperation].
 */
class DefaultSyncOperationTest {
    private data class MockState(
        val needsSoftReset: Boolean,
        val softResetMigrationCompleted: Boolean,
        val nonSoftResetMigrationCompleted: Boolean
    ) : MinimumDestinationState {
        override fun needsSoftReset(): Boolean = needsSoftReset

        override fun <T : MinimumDestinationState> withSoftReset(needsSoftReset: Boolean): T {
            @Suppress("UNCHECKED_CAST") return copy(needsSoftReset = needsSoftReset) as T
        }
    }
    private class TestStreamOperation(destinationState: MockState) : StreamOperation<MockState> {
        // Simulate a StreamOperation implementation that triggers a soft reset upon initialization.
        override val updatedDestinationState: MockState = destinationState.withSoftReset(false)
        override fun writeRecords(
            streamConfig: StreamConfig,
            stream: Stream<PartialAirbyteMessage>
        ) {}
        override fun finalizeTable(streamConfig: StreamConfig, syncSummary: StreamSyncSummary) {}
    }
    private val streamOperations: MutableMap<StreamConfig, StreamOperation<MockState>> =
        mutableMapOf()
    private val streamOperationFactory: StreamOperationFactory<MockState> =
        StreamOperationFactory { initialStatus: DestinationInitialStatus<MockState>, _ ->
            streamOperations.computeIfAbsent(initialStatus.streamConfig) {
                spyk(TestStreamOperation(initialStatus.destinationState))
            }
        }

    private val destinationHandler = mockk<DestinationHandler<MockState>>(relaxed = true)

    @Test
    fun multipleMigrations() {
        val appendInitialStatus =
            DestinationInitialStatus(
                appendStreamConfig,
                isFinalTablePresent = true,
                initialRawTableStatus =
                    InitialRawTableStatus(
                        rawTableExists = true,
                        hasUnprocessedRecords = false,
                        maxProcessedTimestamp = Optional.empty(),
                    ),
                isSchemaMismatch = true,
                isFinalTableEmpty = false,
                destinationState =
                    MockState(
                        needsSoftReset = false,
                        softResetMigrationCompleted = false,
                        nonSoftResetMigrationCompleted = false,
                    )
            )
        every { destinationHandler.gatherInitialState(any()) } returns listOf(appendInitialStatus)

        val syncOperation =
            DefaultSyncOperation(
                parsedCatalog,
                destinationHandler,
                "default_ns",
                streamOperationFactory,
                listOf(migrationWithSoftReset, migrationWithoutSoftReset, badMigration),
            )

        assertEquals(setOf(appendStreamConfig), streamOperations.keys)
        verifySequence {
            destinationHandler.gatherInitialState(any())
            destinationHandler.execute(
                Sql.of("MIGRATE WITH SOFT_RESET airbyte_internal.append_stream;")
            )
            destinationHandler.gatherInitialState(any())
            destinationHandler.execute(
                Sql.of("MIGRATE WITHOUT SOFT_RESET airbyte_internal.append_stream;")
            )
            destinationHandler.execute(Sql.of("BAD MIGRATE airbyte_internal.append_stream;"))
            destinationHandler.commitDestinationStates(
                mapOf(
                    appendStreamConfig.id to
                        MockState(
                            needsSoftReset = true,
                            softResetMigrationCompleted = true,
                            nonSoftResetMigrationCompleted = true,
                        ),
                ),
            )
            destinationHandler.createNamespaces(
                setOf(appendStreamConfig.id.rawNamespace, appendStreamConfig.id.finalNamespace)
            )
            streamOperations.values.onEach { it.updatedDestinationState }
            destinationHandler.commitDestinationStates(
                mapOf(
                    appendStreamConfig.id to
                        MockState(
                            needsSoftReset = false,
                            softResetMigrationCompleted = true,
                            nonSoftResetMigrationCompleted = true,
                        ),
                ),
            )
        }
        confirmVerified(destinationHandler)
        streamOperations.values.onEach { confirmVerified(it) }

        clearMocks(destinationHandler)
        streamOperations.values.onEach { clearMocks(it) }

        syncOperation.finalizeStreams(
            mapOf(appendStreamConfig.id.asStreamDescriptor() to StreamSyncSummary(Optional.of(42)))
        )

        verify(exactly = 1) {
            streamOperations.values.onEach {
                it.finalizeTable(appendStreamConfig, StreamSyncSummary(Optional.of(42)))
            }
        }
        confirmVerified(destinationHandler)
        streamOperations.values.onEach { confirmVerified(it) }
    }

    /**
     * Verify that with an initial DestinationState containing needsSoftReset=true, even if no
     * migrations trigger a soft reset, we still retain the soft reset status.
     */
    @Test
    fun initialSoftReset() {
        val appendInitialStatus =
            DestinationInitialStatus(
                appendStreamConfig,
                isFinalTablePresent = true,
                initialRawTableStatus =
                    InitialRawTableStatus(
                        rawTableExists = true,
                        hasUnprocessedRecords = false,
                        maxProcessedTimestamp = Optional.empty(),
                    ),
                isSchemaMismatch = true,
                isFinalTableEmpty = false,
                destinationState =
                    MockState(
                        // Note the needsSoftReset=true here.
                        needsSoftReset = true,
                        softResetMigrationCompleted = true,
                        nonSoftResetMigrationCompleted = true,
                    )
            )
        every { destinationHandler.gatherInitialState(any()) } returns listOf(appendInitialStatus)

        DefaultSyncOperation(
            parsedCatalog,
            destinationHandler,
            "default_ns",
            streamOperationFactory,
            listOf(migrationWithSoftReset, migrationWithoutSoftReset, badMigration),
        )

        assertEquals(setOf(appendStreamConfig), streamOperations.keys)
        verifySequence {
            destinationHandler.gatherInitialState(any())
            // The "badly-written" migration doesn't check anything in the state,
            // so it always executes.
            destinationHandler.execute(Sql.of("BAD MIGRATE airbyte_internal.append_stream;"))
            destinationHandler.commitDestinationStates(
                mapOf(
                    appendStreamConfig.id to
                        MockState(
                            needsSoftReset = true,
                            softResetMigrationCompleted = true,
                            nonSoftResetMigrationCompleted = true,
                        ),
                ),
            )
            destinationHandler.createNamespaces(
                setOf(appendStreamConfig.id.rawNamespace, appendStreamConfig.id.finalNamespace)
            )
            streamOperations.values.onEach { it.updatedDestinationState }
            destinationHandler.commitDestinationStates(
                mapOf(
                    appendStreamConfig.id to
                        MockState(
                            needsSoftReset = false,
                            softResetMigrationCompleted = true,
                            nonSoftResetMigrationCompleted = true,
                        ),
                ),
            )
        }
        confirmVerified(destinationHandler)
        streamOperations.values.onEach { confirmVerified(it) }
    }

    companion object {
        // A migration that wants a soft reset, and also requires us to refech initial state
        private val migrationWithSoftReset: Migration<MockState> =
            object : Migration<MockState> {
                override fun migrateIfNecessary(
                    destinationHandler: DestinationHandler<MockState>,
                    stream: StreamConfig,
                    state: DestinationInitialStatus<MockState>
                ): Migration.MigrationResult<MockState> {
                    if (!state.destinationState.softResetMigrationCompleted) {
                        destinationHandler.execute(
                            Sql.of("MIGRATE WITH SOFT_RESET ${stream.id.rawTableId("")}"),
                        )
                        return Migration.MigrationResult(
                            state.destinationState.copy(
                                needsSoftReset = true,
                                softResetMigrationCompleted = true,
                            ),
                            true,
                        )
                    } else {
                        return Migration.MigrationResult(
                            state.destinationState,
                            false,
                        )
                    }
                }
            }

        // A migration that doesn't do anything interesting
        private val migrationWithoutSoftReset: Migration<MockState> =
            object : Migration<MockState> {
                override fun migrateIfNecessary(
                    destinationHandler: DestinationHandler<MockState>,
                    stream: StreamConfig,
                    state: DestinationInitialStatus<MockState>
                ): Migration.MigrationResult<MockState> {
                    if (!state.destinationState.nonSoftResetMigrationCompleted) {
                        destinationHandler.execute(
                            Sql.of("MIGRATE WITHOUT SOFT_RESET ${stream.id.rawTableId("")}"),
                        )
                    }
                    return Migration.MigrationResult(
                        state.destinationState.copy(nonSoftResetMigrationCompleted = true),
                        false,
                    )
                }
            }

        // A migration that incorrectly _unsets_ needsSoftReset.
        private val badMigration: Migration<MockState> =
            object : Migration<MockState> {
                override fun migrateIfNecessary(
                    destinationHandler: DestinationHandler<MockState>,
                    stream: StreamConfig,
                    state: DestinationInitialStatus<MockState>
                ): Migration.MigrationResult<MockState> {
                    destinationHandler.execute(
                        Sql.of("BAD MIGRATE ${stream.id.rawTableId("")}"),
                    )
                    return Migration.MigrationResult(
                        state.destinationState.copy(needsSoftReset = false),
                        false,
                    )
                }
            }

        private val appendStreamConfig =
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
                listOf(),
                Optional.empty(),
                linkedMapOf(),
                0,
                0,
                0,
            )
        private val parsedCatalog = ParsedCatalog(listOf(appendStreamConfig))
    }
}
