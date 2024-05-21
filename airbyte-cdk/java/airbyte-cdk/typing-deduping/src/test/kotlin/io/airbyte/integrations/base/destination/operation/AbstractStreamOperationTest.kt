/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.operation

import io.airbyte.cdk.integrations.destination.StreamSyncSummary
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteProtocolType
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType
import io.airbyte.integrations.base.destination.typing_deduping.ColumnId
import io.airbyte.integrations.base.destination.typing_deduping.DestinationInitialStatus
import io.airbyte.integrations.base.destination.typing_deduping.InitialRawTableStatus
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig
import io.airbyte.integrations.base.destination.typing_deduping.StreamId
import io.airbyte.integrations.base.destination.typing_deduping.migrators.MinimumDestinationState
import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.mockk.checkUnnecessaryStub
import io.mockk.clearMocks
import io.mockk.confirmVerified
import io.mockk.every
import io.mockk.mockk
import io.mockk.verifySequence
import java.time.Instant
import java.util.Optional
import java.util.stream.Stream
import org.junit.jupiter.api.Nested
import org.junit.jupiter.api.Test
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.Arguments
import org.junit.jupiter.params.provider.MethodSource
import org.junit.jupiter.params.provider.ValueSource

/**
 * Verify that [AbstractStreamOperation] behaves correctly, given various initial states. We
 * intentionally mock the [DestinationInitialStatus]. This allows us to verify that the stream ops
 * only looks at specific fields - the mocked initial statuses will throw exceptions for unstubbed
 * methods.
 *
 * For example, we don't need to write separate test cases for "final table does not exist and
 * destination state has softReset=true/false" - instead we have a single test case for "final table
 * does not exist", and it doesn't stub the `needsSoftReset` method. If we introduce a bug in stream
 * ops and it starts checking needsSoftReset even though the final table doesn't exist, then these
 * tests will start failing.
 */
class AbstractStreamOperationTest {
    class TestStreamOperation(
        storageOperation: StorageOperation<Stream<PartialAirbyteMessage>>,
        destinationInitialStatus: DestinationInitialStatus<MinimumDestinationState.Impl>
    ) :
        AbstractStreamOperation<MinimumDestinationState.Impl, Stream<PartialAirbyteMessage>>(
            storageOperation,
            destinationInitialStatus,
        ) {
        override fun writeRecords(
            streamConfig: StreamConfig,
            stream: Stream<PartialAirbyteMessage>
        ) {
            // noop
        }
    }

    // This mock is purely for verification. Set relaxed=true so we don't need to stub every call.
    // Our tests use confirmVerified() to check that we didn't miss any actions.
    private val storageOperation =
        mockk<StorageOperation<Stream<PartialAirbyteMessage>>>(relaxed = true)

    @Nested
    inner class Overwrite {
        private val streamConfig =
            StreamConfig(
                streamId,
                DestinationSyncMode.OVERWRITE,
                listOf(),
                Optional.empty(),
                columns,
                // TODO currently these values are unused. Eventually we should restructure this
                // class
                // to test based on generation ID instead of sync mode.
                0,
                0,
                0
            )

        @Test
        fun emptyDestination() {
            val initialState =
                mockk<DestinationInitialStatus<MinimumDestinationState.Impl>> {
                    every { streamConfig } returns this@Overwrite.streamConfig
                    every { initialRawTableStatus } returns mockk<InitialRawTableStatus>()
                    every { isFinalTablePresent } returns false
                    every {
                        destinationState.withSoftReset<MinimumDestinationState.Impl>(any())
                    } returns destinationState
                }

            val streamOperations = TestStreamOperation(storageOperation, initialState)

            verifySequence {
                storageOperation.prepareStage(streamId, streamConfig.destinationSyncMode)
                storageOperation.createFinalTable(streamConfig, "", false)
            }
            confirmVerified(storageOperation)

            clearMocks(storageOperation)
            streamOperations.finalizeTable(streamConfig, StreamSyncSummary(Optional.of(42)))

            verifySequence {
                storageOperation.cleanupStage(streamId)
                storageOperation.typeAndDedupe(
                    streamConfig,
                    Optional.empty(),
                    "",
                )
            }
            confirmVerified(storageOperation)
            checkUnnecessaryStub(
                initialState,
                initialState.initialRawTableStatus,
                initialState.destinationState
            )
        }

        @Test
        fun existingEmptyTableSchemaMismatch() {
            val initialState =
                mockk<DestinationInitialStatus<MinimumDestinationState.Impl>> {
                    every { streamConfig } returns this@Overwrite.streamConfig
                    every { initialRawTableStatus } returns mockk<InitialRawTableStatus>()
                    every { isFinalTablePresent } returns true
                    every { isFinalTableEmpty } returns true
                    // Even though there's a schema mismatch, we're running in overwrite mode,
                    // so we shouldn't execute a soft reset.
                    // We do need to use a temp final table though.
                    every { isSchemaMismatch } returns true
                    every {
                        destinationState.withSoftReset<MinimumDestinationState.Impl>(any())
                    } returns destinationState
                }

            val streamOperations = TestStreamOperation(storageOperation, initialState)

            verifySequence {
                storageOperation.prepareStage(streamId, streamConfig.destinationSyncMode)
                storageOperation.createFinalTable(streamConfig, EXPECTED_OVERWRITE_SUFFIX, true)
            }
            confirmVerified(storageOperation)

            clearMocks(storageOperation)
            streamOperations.finalizeTable(streamConfig, StreamSyncSummary(Optional.of(42)))

            verifySequence {
                storageOperation.cleanupStage(streamId)
                storageOperation.typeAndDedupe(
                    streamConfig,
                    Optional.empty(),
                    EXPECTED_OVERWRITE_SUFFIX,
                )
                storageOperation.overwriteFinalTable(streamConfig, EXPECTED_OVERWRITE_SUFFIX)
            }
            confirmVerified(storageOperation)
            checkUnnecessaryStub(
                initialState,
                initialState.initialRawTableStatus,
                initialState.destinationState
            )
        }

        @Test
        fun existingEmptyTableMatchingSchema() {
            val initialState =
                mockk<DestinationInitialStatus<MinimumDestinationState.Impl>> {
                    every { streamConfig } returns this@Overwrite.streamConfig
                    every { initialRawTableStatus } returns mockk<InitialRawTableStatus>()
                    every { isFinalTablePresent } returns true
                    every { isFinalTableEmpty } returns true
                    every { isSchemaMismatch } returns false
                    every {
                        destinationState.withSoftReset<MinimumDestinationState.Impl>(any())
                    } returns destinationState
                }

            val streamOperations = TestStreamOperation(storageOperation, initialState)

            verifySequence {
                storageOperation.prepareStage(streamId, streamConfig.destinationSyncMode)
                // No table creation - we can just reuse the existing table.
            }
            confirmVerified(storageOperation)

            clearMocks(storageOperation)
            streamOperations.finalizeTable(streamConfig, StreamSyncSummary(Optional.of(42)))

            verifySequence {
                storageOperation.cleanupStage(streamId)
                storageOperation.typeAndDedupe(
                    streamConfig,
                    Optional.empty(),
                    "",
                )
            }
            confirmVerified(storageOperation)
            checkUnnecessaryStub(
                initialState,
                initialState.initialRawTableStatus,
                initialState.destinationState
            )
        }

        @Test
        fun existingNonEmptyTable() {
            val initialState =
                mockk<DestinationInitialStatus<MinimumDestinationState.Impl>> {
                    every { streamConfig } returns this@Overwrite.streamConfig
                    every { initialRawTableStatus } returns mockk<InitialRawTableStatus>()
                    every { isFinalTablePresent } returns true
                    every { isFinalTableEmpty } returns false
                    every {
                        destinationState.withSoftReset<MinimumDestinationState.Impl>(any())
                    } returns destinationState
                }

            val streamOperations = TestStreamOperation(storageOperation, initialState)

            verifySequence {
                storageOperation.prepareStage(streamId, streamConfig.destinationSyncMode)
                storageOperation.createFinalTable(streamConfig, EXPECTED_OVERWRITE_SUFFIX, true)
            }
            confirmVerified(storageOperation)

            clearMocks(storageOperation)
            streamOperations.finalizeTable(streamConfig, StreamSyncSummary(Optional.of(42)))

            verifySequence {
                storageOperation.cleanupStage(streamId)
                storageOperation.typeAndDedupe(
                    streamConfig,
                    Optional.empty(),
                    EXPECTED_OVERWRITE_SUFFIX,
                )
                storageOperation.overwriteFinalTable(streamConfig, EXPECTED_OVERWRITE_SUFFIX)
            }
            confirmVerified(storageOperation)
            checkUnnecessaryStub(
                initialState,
                initialState.initialRawTableStatus,
                initialState.destinationState
            )
        }

        @ParameterizedTest
        @ValueSource(booleans = [true, false])
        fun existingNonEmptyTableNoNewRecords(hasUnprocessedRecords: Boolean) {
            val initialState =
                mockk<DestinationInitialStatus<MinimumDestinationState.Impl>> {
                    every { streamConfig } returns this@Overwrite.streamConfig
                    every { initialRawTableStatus } returns mockk<InitialRawTableStatus>()
                    // This is an overwrite sync, so we can ignore the old raw records.
                    // We should skip T+D if the current sync emitted 0 records.
                    every { initialRawTableStatus.hasUnprocessedRecords } returns
                        hasUnprocessedRecords
                    every { isFinalTablePresent } returns true
                    every { isFinalTableEmpty } returns false
                    every {
                        destinationState.withSoftReset<MinimumDestinationState.Impl>(any())
                    } returns destinationState
                }

            val streamOperations = TestStreamOperation(storageOperation, initialState)

            verifySequence {
                storageOperation.prepareStage(streamId, streamConfig.destinationSyncMode)
                storageOperation.createFinalTable(streamConfig, EXPECTED_OVERWRITE_SUFFIX, true)
            }
            confirmVerified(storageOperation)

            clearMocks(storageOperation)
            streamOperations.finalizeTable(streamConfig, StreamSyncSummary(Optional.of(0)))

            verifySequence {
                storageOperation.cleanupStage(streamId)
                storageOperation.overwriteFinalTable(streamConfig, EXPECTED_OVERWRITE_SUFFIX)
            }
            confirmVerified(storageOperation)
            checkUnnecessaryStub(
                initialState,
                initialState.initialRawTableStatus,
                initialState.destinationState
            )
        }
    }

    @Nested
    inner class NonOverwrite {
        @ParameterizedTest
        @MethodSource(
            "io.airbyte.integrations.base.destination.operation.AbstractStreamOperationTest#nonOverwriteStreamConfigs"
        )
        fun emptyDestination(streamConfig: StreamConfig) {
            val initialState =
                mockk<DestinationInitialStatus<MinimumDestinationState.Impl>> {
                    every { this@mockk.streamConfig } returns streamConfig
                    every { initialRawTableStatus.maxProcessedTimestamp } returns Optional.empty()
                    every { isFinalTablePresent } returns false
                    every {
                        destinationState.withSoftReset<MinimumDestinationState.Impl>(any())
                    } returns destinationState
                }

            val streamOperations = TestStreamOperation(storageOperation, initialState)

            verifySequence {
                storageOperation.prepareStage(streamId, streamConfig.destinationSyncMode)
                storageOperation.createFinalTable(streamConfig, "", false)
            }
            confirmVerified(storageOperation)

            clearMocks(storageOperation)
            streamOperations.finalizeTable(streamConfig, StreamSyncSummary(Optional.of(42)))

            verifySequence {
                storageOperation.cleanupStage(streamId)
                storageOperation.typeAndDedupe(
                    streamConfig,
                    Optional.empty(),
                    "",
                )
            }
            confirmVerified(storageOperation)
            checkUnnecessaryStub(
                initialState,
                initialState.initialRawTableStatus,
                initialState.destinationState
            )
        }

        @ParameterizedTest
        @MethodSource(
            "io.airbyte.integrations.base.destination.operation.AbstractStreamOperationTest#nonOverwriteStreamConfigs"
        )
        fun existingTableSchemaMismatch(streamConfig: StreamConfig) {
            val initialState =
                mockk<DestinationInitialStatus<MinimumDestinationState.Impl>> {
                    every { this@mockk.streamConfig } returns streamConfig
                    every { initialRawTableStatus.maxProcessedTimestamp } returns Optional.empty()
                    every { isFinalTablePresent } returns true
                    every { isSchemaMismatch } returns true
                    every {
                        destinationState.withSoftReset<MinimumDestinationState.Impl>(any())
                    } returns destinationState
                }

            val streamOperations = TestStreamOperation(storageOperation, initialState)

            verifySequence {
                storageOperation.prepareStage(streamId, streamConfig.destinationSyncMode)
                storageOperation.softResetFinalTable(streamConfig)
            }
            confirmVerified(storageOperation)

            clearMocks(storageOperation)
            streamOperations.finalizeTable(streamConfig, StreamSyncSummary(Optional.of(42)))

            verifySequence {
                storageOperation.cleanupStage(streamId)
                storageOperation.typeAndDedupe(
                    streamConfig,
                    Optional.empty(),
                    "",
                )
            }
            confirmVerified(storageOperation)
            checkUnnecessaryStub(
                initialState,
                initialState.initialRawTableStatus,
                initialState.destinationState
            )
        }

        @ParameterizedTest
        @MethodSource(
            "io.airbyte.integrations.base.destination.operation.AbstractStreamOperationTest#nonOverwriteStreamConfigs"
        )
        fun existingTableSchemaMatch(streamConfig: StreamConfig) {
            val initialState =
                mockk<DestinationInitialStatus<MinimumDestinationState.Impl>> {
                    every { this@mockk.streamConfig } returns streamConfig
                    every { initialRawTableStatus.maxProcessedTimestamp } returns Optional.empty()
                    every { isFinalTablePresent } returns true
                    every { isSchemaMismatch } returns false
                    every { destinationState } returns MinimumDestinationState.Impl(false)
                }

            val streamOperations = TestStreamOperation(storageOperation, initialState)

            verifySequence {
                storageOperation.prepareStage(streamId, streamConfig.destinationSyncMode)
                // No soft reset - we can just reuse the existing table.
            }
            confirmVerified(storageOperation)

            clearMocks(storageOperation)
            streamOperations.finalizeTable(streamConfig, StreamSyncSummary(Optional.of(42)))

            verifySequence {
                storageOperation.cleanupStage(streamId)
                storageOperation.typeAndDedupe(
                    streamConfig,
                    Optional.empty(),
                    "",
                )
            }
            confirmVerified(storageOperation)
            checkUnnecessaryStub(initialState, initialState.initialRawTableStatus)
        }

        @ParameterizedTest
        @MethodSource(
            "io.airbyte.integrations.base.destination.operation.AbstractStreamOperationTest#nonOverwriteStreamConfigs"
        )
        fun existingTableAndStateRequiresSoftReset(streamConfig: StreamConfig) {
            val initialState =
                mockk<DestinationInitialStatus<MinimumDestinationState.Impl>> {
                    every { this@mockk.streamConfig } returns streamConfig
                    every { initialRawTableStatus.maxProcessedTimestamp } returns Optional.empty()
                    every { isFinalTablePresent } returns true
                    every { isSchemaMismatch } returns false
                    every { destinationState } returns MinimumDestinationState.Impl(true)
                }

            val streamOperations = TestStreamOperation(storageOperation, initialState)

            verifySequence {
                storageOperation.prepareStage(streamId, streamConfig.destinationSyncMode)
                storageOperation.softResetFinalTable(streamConfig)
            }
            confirmVerified(storageOperation)

            clearMocks(storageOperation)
            streamOperations.finalizeTable(streamConfig, StreamSyncSummary(Optional.of(42)))

            verifySequence {
                storageOperation.cleanupStage(streamId)
                storageOperation.typeAndDedupe(
                    streamConfig,
                    Optional.empty(),
                    "",
                )
            }
            confirmVerified(storageOperation)
            checkUnnecessaryStub(initialState, initialState.initialRawTableStatus)
        }

        @ParameterizedTest
        @MethodSource(
            "io.airbyte.integrations.base.destination.operation.AbstractStreamOperationTest#nonOverwriteStreamConfigsAndBoolean"
        )
        fun existingNonEmptyTableNoNewRecords(
            streamConfig: StreamConfig,
            hasUnprocessedRecords: Boolean
        ) {
            val initialState =
                mockk<DestinationInitialStatus<MinimumDestinationState.Impl>> {
                    every { this@mockk.streamConfig } returns streamConfig
                    // This is an overwrite sync, so we can ignore the old raw records.
                    // We should skip T+D if the current sync emitted 0 records.
                    every { initialRawTableStatus.hasUnprocessedRecords } returns
                        hasUnprocessedRecords
                    if (hasUnprocessedRecords) {
                        // We only care about this value if we're executing T+D.
                        // If there are no unprocessed records from a previous sync, and no new
                        // records from
                        // this sync,
                        // we don't need to set it.
                        every { initialRawTableStatus.maxProcessedTimestamp } returns
                            maxProcessedTimestamp
                    }
                    every { isFinalTablePresent } returns true
                    every { isSchemaMismatch } returns false
                    every { destinationState } returns MinimumDestinationState.Impl(false)
                }

            val streamOperations = TestStreamOperation(storageOperation, initialState)

            verifySequence {
                storageOperation.prepareStage(streamId, streamConfig.destinationSyncMode)
            }
            confirmVerified(storageOperation)

            clearMocks(storageOperation)
            streamOperations.finalizeTable(streamConfig, StreamSyncSummary(Optional.of(0)))

            verifySequence {
                storageOperation.cleanupStage(streamId)
                // If this sync emitted no records, we only need to run T+D if a previous sync
                // emitted
                // some records but failed to run T+D.
                if (hasUnprocessedRecords) {
                    storageOperation.typeAndDedupe(streamConfig, maxProcessedTimestamp, "")
                }
            }
            confirmVerified(storageOperation)
            checkUnnecessaryStub(initialState, initialState.initialRawTableStatus)
        }
    }

    companion object {
        val streamId =
            StreamId(
                "final_namespace",
                "final_name",
                "raw_namespace",
                "raw_name",
                "original_namespace",
                "original_name",
            )
        private val pk1 = ColumnId("pk1", "pk1_original_name", "pk1_canonical_name")
        private val pk2 = ColumnId("pk2", "pk2_original_name", "pk2_canonical_name")
        private val cursor = ColumnId("cursor", "cursor_original_name", "cursor_canonical_name")
        val columns: LinkedHashMap<ColumnId, AirbyteType> =
            linkedMapOf(
                pk1 to AirbyteProtocolType.INTEGER,
                pk2 to AirbyteProtocolType.STRING,
                cursor to AirbyteProtocolType.TIMESTAMP_WITH_TIMEZONE,
                ColumnId(
                    "username",
                    "username_original_name",
                    "username_canonical_name",
                ) to AirbyteProtocolType.STRING,
            )

        const val EXPECTED_OVERWRITE_SUFFIX = "_airbyte_tmp"
        val maxProcessedTimestamp = Optional.of(Instant.parse("2024-01-23T12:34:56Z"))

        private val appendStreamConfig =
            StreamConfig(
                streamId,
                DestinationSyncMode.APPEND,
                listOf(),
                Optional.empty(),
                columns,
                // TODO currently these values are unused. Eventually we should restructure this
                // class
                // to test based on generation ID instead of sync mode.
                0,
                0,
                0
            )
        private val dedupStreamConfig =
            StreamConfig(
                streamId,
                DestinationSyncMode.APPEND_DEDUP,
                listOf(pk1, pk2),
                Optional.of(cursor),
                columns,
                // TODO currently these values are unused. Eventually we should restructure this
                // class
                // to test based on generation ID instead of sync mode.
                0,
                0,
                0
            )

        // junit 5 doesn't support class-level parameterization...
        // so we have to hack this in a somewhat dumb way.
        // append and dedup should behave identically from StreamOperations' POV,
        // so just shove them together.
        @JvmStatic
        fun nonOverwriteStreamConfigs(): Stream<Arguments> =
            Stream.of(
                Arguments.of(appendStreamConfig),
                Arguments.of(dedupStreamConfig),
            )

        // Some tests are further parameterized, which this method supports.
        @JvmStatic
        fun nonOverwriteStreamConfigsAndBoolean(): Stream<Arguments> =
            Stream.of(
                Arguments.of(appendStreamConfig, true),
                Arguments.of(appendStreamConfig, false),
                Arguments.of(dedupStreamConfig, true),
                Arguments.of(dedupStreamConfig, false),
            )
    }
}
