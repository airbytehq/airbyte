/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.operation

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
import io.mockk.slot
import io.mockk.verify
import java.util.Optional
import org.junit.jupiter.api.Test
import org.mockito.kotlin.internal.createInstance

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

    private val destinationHandler = mockk<DestinationHandler<MockState>>(relaxed = true)
    private val streamOperations =
        mapOf(
            overwriteStreamConfig to mockk<StreamOperation<MockState>>(relaxed = true),
            appendStreamConfig to mockk<StreamOperation<MockState>>(relaxed = true),
            dedupStreamConfig to mockk<StreamOperation<MockState>>(relaxed = true),
        )
    private val streamOperationsFactory =
        mockk<StreamOperationsFactory<MockState>> {
            val initialStatusSlot = slot<DestinationInitialStatus<MockState>>()
            every { createInstance(capture(initialStatusSlot)) } answers
                {
                    streamOperations[initialStatusSlot.captured.streamConfig]!!
                }
        }

    @Test
    fun multipleSoftResets() {
        val overwriteInitialStatus =
            DestinationInitialStatus(
                overwriteStreamConfig,
                isFinalTablePresent = true,
                initialRawTableStatus =
                    InitialRawTableStatus(
                        rawTableExists = true,
                        hasUnprocessedRecords = false,
                        maxProcessedTimestamp = Optional.empty()
                    ),
                isSchemaMismatch = true,
                isFinalTableEmpty = false,
                destinationState =
                    MockState(
                        needsSoftReset = false,
                        softResetMigrationCompleted = false,
                        nonSoftResetMigrationCompleted = true
                    )
            )
        val appendInitialStatus =
            DestinationInitialStatus(
                appendStreamConfig,
                isFinalTablePresent = true,
                initialRawTableStatus =
                    InitialRawTableStatus(
                        rawTableExists = true,
                        hasUnprocessedRecords = false,
                        maxProcessedTimestamp = Optional.empty()
                    ),
                isSchemaMismatch = true,
                isFinalTableEmpty = false,
                destinationState =
                    MockState(
                        needsSoftReset = false,
                        softResetMigrationCompleted = false,
                        nonSoftResetMigrationCompleted = true
                    )
            )
        val dedupInitialStatus =
            DestinationInitialStatus(
                dedupStreamConfig,
                isFinalTablePresent = true,
                initialRawTableStatus =
                    InitialRawTableStatus(
                        rawTableExists = true,
                        hasUnprocessedRecords = false,
                        maxProcessedTimestamp = Optional.empty()
                    ),
                isSchemaMismatch = true,
                isFinalTableEmpty = false,
                destinationState =
                    MockState(
                        needsSoftReset = false,
                        softResetMigrationCompleted = false,
                        nonSoftResetMigrationCompleted = true
                    )
            )
        every { destinationHandler.gatherInitialState(any()) } returns
            listOf(
                overwriteInitialStatus,
                appendInitialStatus,
                dedupInitialStatus,
            )

        val syncOperation =
            DefaultSyncOperation(
                parsedCatalog,
                destinationHandler,
                "default_ns",
                streamOperationsFactory,
                listOf(migrationWithSoftReset, migrationWithoutSoftReset),
            )

        verify(exactly = 1) {
            destinationHandler.gatherInitialState(any())
            destinationHandler.execute(
                Sql.of("MIGRATE WITH SOFT_RESET airbyte_internal.overwrite_stream;")
            )
            destinationHandler.execute(
                Sql.of("MIGRATE WITH SOFT_RESET airbyte_internal.append_stream;")
            )
            destinationHandler.execute(
                Sql.of("MIGRATE WITH SOFT_RESET airbyte_internal.dedup_stream;")
            )
            destinationHandler.commitDestinationStates(
                mapOf(
                    overwriteStreamConfig.id to
                        MockState(
                            needsSoftReset = true,
                            softResetMigrationCompleted = true,
                            nonSoftResetMigrationCompleted = true,
                        ),
                    appendStreamConfig.id to
                        MockState(
                            needsSoftReset = true,
                            softResetMigrationCompleted = true,
                            nonSoftResetMigrationCompleted = true,
                        ),
                    dedupStreamConfig.id to
                        MockState(
                            needsSoftReset = true,
                            softResetMigrationCompleted = true,
                            nonSoftResetMigrationCompleted = true,
                        ),
                ),
            )
            streamOperationsFactory.createInstance(
                overwriteInitialStatus.copy(
                    destinationState =
                        overwriteInitialStatus.destinationState.copy(
                            needsSoftReset = true,
                            softResetMigrationCompleted = true,
                        ),
                ),
            )
            streamOperationsFactory.createInstance(
                appendInitialStatus.copy(
                    destinationState =
                        appendInitialStatus.destinationState.copy(
                            needsSoftReset = true,
                            softResetMigrationCompleted = true,
                        ),
                ),
            )
            streamOperationsFactory.createInstance(
                dedupInitialStatus.copy(
                    destinationState =
                        dedupInitialStatus.destinationState.copy(
                            needsSoftReset = true,
                            softResetMigrationCompleted = true,
                        ),
                ),
            )
        }
        confirmVerified(destinationHandler)
        confirmVerified(streamOperationsFactory)
        streamOperations.values.onEach { confirmVerified(it) }

        clearMocks(destinationHandler)
        clearMocks(streamOperationsFactory)
        streamOperations.values.onEach { clearMocks(it) }
    }

    companion object {
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
                    }
                    return Migration.MigrationResult(
                        state.destinationState.copy(
                            needsSoftReset = true,
                            softResetMigrationCompleted = true,
                        ),
                        false,
                    )
                }
            }

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
                        false
                    )
                }
            }

        private val overwriteStreamConfig =
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
                mockk(),
                mockk(),
                mockk(),
                0,
                0,
                0,
            )
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
                mockk(),
                mockk(),
                mockk(),
                0,
                0,
                0,
            )
        private val dedupStreamConfig =
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
                mockk(),
                mockk(),
                mockk(),
                0,
                0,
                0,
            )
        private val parsedCatalog =
            ParsedCatalog(listOf(overwriteStreamConfig, appendStreamConfig, dedupStreamConfig))
    }
}
