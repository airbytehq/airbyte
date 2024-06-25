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
import io.airbyte.protocol.models.v0.AirbyteStreamStatusTraceMessage.AirbyteStreamStatus
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
        override fun writeRecordsImpl(
            streamConfig: StreamConfig,
            suffix: String,
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
    inner class Truncate {
        private val streamConfig =
            StreamConfig(
                streamId,
                DestinationSyncMode.APPEND,
                listOf(),
                Optional.empty(),
                columns,
                generationId = 21,
                minimumGenerationId = 21,
                syncId = 0
            )

        @Test
        fun emptyDestination() {
            val initialState =
                mockk<DestinationInitialStatus<MinimumDestinationState.Impl>> {
                    every { streamConfig } returns this@Truncate.streamConfig
                    every { initialRawTableStatus } returns mockk<InitialRawTableStatus>()
                    every { initialTempRawTableStatus.rawTableExists } returns false
                    every { isFinalTablePresent } returns false
                    every {
                        destinationState.withSoftReset<MinimumDestinationState.Impl>(any())
                    } returns destinationState
                }

            val streamOperations = TestStreamOperation(storageOperation, initialState)

            verifySequence {
                storageOperation.prepareStage(streamId, EXPECTED_SUFFIX)
                storageOperation.createFinalTable(streamConfig, "", false)
            }
            confirmVerified(storageOperation)

            clearMocks(storageOperation)
            streamOperations.finalizeTable(
                streamConfig,
                StreamSyncSummary(42, AirbyteStreamStatus.COMPLETE)
            )

            verifySequence {
                storageOperation.cleanupStage(streamId)
                storageOperation.overwriteStage(streamId, EXPECTED_SUFFIX)
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
        fun existingEmptyFinalTableSchemaMismatch() {
            val initialState =
                mockk<DestinationInitialStatus<MinimumDestinationState.Impl>> {
                    every { streamConfig } returns this@Truncate.streamConfig
                    every { initialRawTableStatus } returns mockk<InitialRawTableStatus>()
                    every { initialTempRawTableStatus.rawTableExists } returns false
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
                storageOperation.prepareStage(streamId, EXPECTED_SUFFIX)
                storageOperation.createFinalTable(streamConfig, EXPECTED_SUFFIX, true)
            }
            confirmVerified(storageOperation)

            clearMocks(storageOperation)
            streamOperations.finalizeTable(
                streamConfig,
                StreamSyncSummary(42, AirbyteStreamStatus.COMPLETE)
            )

            verifySequence {
                storageOperation.cleanupStage(streamId)
                storageOperation.overwriteStage(streamId, EXPECTED_SUFFIX)
                storageOperation.typeAndDedupe(
                    streamConfig,
                    Optional.empty(),
                    EXPECTED_SUFFIX,
                )
                storageOperation.overwriteFinalTable(streamConfig, EXPECTED_SUFFIX)
            }
            confirmVerified(storageOperation)
            checkUnnecessaryStub(
                initialState,
                initialState.initialRawTableStatus,
                initialState.destinationState
            )
        }

        @Test
        fun existingEmptyFinalTableMatchingSchema() {
            val initialState =
                mockk<DestinationInitialStatus<MinimumDestinationState.Impl>> {
                    every { streamConfig } returns this@Truncate.streamConfig
                    every { initialRawTableStatus } returns mockk<InitialRawTableStatus>()
                    every { initialTempRawTableStatus.rawTableExists } returns false
                    every { isFinalTablePresent } returns true
                    every { isFinalTableEmpty } returns true
                    every { isSchemaMismatch } returns false
                    every {
                        destinationState.withSoftReset<MinimumDestinationState.Impl>(any())
                    } returns destinationState
                }

            val streamOperations = TestStreamOperation(storageOperation, initialState)

            verifySequence {
                storageOperation.prepareStage(streamId, EXPECTED_SUFFIX)
                // No table creation - we can just reuse the existing table.
            }
            confirmVerified(storageOperation)

            clearMocks(storageOperation)
            streamOperations.finalizeTable(
                streamConfig,
                StreamSyncSummary(42, AirbyteStreamStatus.COMPLETE)
            )

            verifySequence {
                storageOperation.cleanupStage(streamId)
                storageOperation.overwriteStage(streamId, EXPECTED_SUFFIX)
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
        fun existingNonEmptyFinalTable() {
            val initialState =
                mockk<DestinationInitialStatus<MinimumDestinationState.Impl>> {
                    every { streamConfig } returns this@Truncate.streamConfig
                    every { initialRawTableStatus } returns mockk<InitialRawTableStatus>()
                    every { initialTempRawTableStatus.rawTableExists } returns false
                    every { isFinalTablePresent } returns true
                    every { isFinalTableEmpty } returns false
                    every {
                        destinationState.withSoftReset<MinimumDestinationState.Impl>(any())
                    } returns destinationState
                }

            val streamOperations = TestStreamOperation(storageOperation, initialState)

            verifySequence {
                storageOperation.prepareStage(streamId, EXPECTED_SUFFIX)
                storageOperation.createFinalTable(streamConfig, EXPECTED_SUFFIX, true)
            }
            confirmVerified(storageOperation)

            clearMocks(storageOperation)
            streamOperations.finalizeTable(
                streamConfig,
                StreamSyncSummary(42, AirbyteStreamStatus.COMPLETE)
            )

            verifySequence {
                storageOperation.cleanupStage(streamId)
                storageOperation.overwriteStage(streamId, EXPECTED_SUFFIX)
                storageOperation.typeAndDedupe(
                    streamConfig,
                    Optional.empty(),
                    EXPECTED_SUFFIX,
                )
                storageOperation.overwriteFinalTable(streamConfig, EXPECTED_SUFFIX)
            }
            confirmVerified(storageOperation)
            checkUnnecessaryStub(
                initialState,
                initialState.initialRawTableStatus,
                initialState.destinationState
            )
        }

        @Test
        fun existingNonEmptyFinalTableStatusIncomplete() {
            val initialState =
                mockk<DestinationInitialStatus<MinimumDestinationState.Impl>> {
                    every { streamConfig } returns this@Truncate.streamConfig
                    every { initialRawTableStatus } returns mockk<InitialRawTableStatus>()
                    every { initialTempRawTableStatus.rawTableExists } returns false
                    every { isFinalTablePresent } returns true
                    every { isFinalTableEmpty } returns false
                    every {
                        destinationState.withSoftReset<MinimumDestinationState.Impl>(any())
                    } returns destinationState
                }

            val streamOperations = TestStreamOperation(storageOperation, initialState)
            // No point in verifying setup, completely identical to existingNonEmptyTable
            clearMocks(storageOperation)
            streamOperations.finalizeTable(
                streamConfig,
                StreamSyncSummary(42, AirbyteStreamStatus.INCOMPLETE)
            )

            verifySequence {
                storageOperation.cleanupStage(streamId)
                // Don't run T+D, and don't overwrite the final table.
            }
            confirmVerified(storageOperation)
            checkUnnecessaryStub(
                initialState,
                initialState.initialRawTableStatus,
                initialState.destinationState
            )
        }

        @Test
        fun existingNonEmptyFinalTableNoNewRecords() {
            val initialState =
                mockk<DestinationInitialStatus<MinimumDestinationState.Impl>> {
                    every { streamConfig } returns this@Truncate.streamConfig
                    every { initialRawTableStatus } returns mockk<InitialRawTableStatus>()
                    every { initialTempRawTableStatus.rawTableExists } returns false
                    every { isFinalTablePresent } returns true
                    every { isFinalTableEmpty } returns false
                    every {
                        destinationState.withSoftReset<MinimumDestinationState.Impl>(any())
                    } returns destinationState
                }

            val streamOperations = TestStreamOperation(storageOperation, initialState)

            verifySequence {
                storageOperation.prepareStage(streamId, EXPECTED_SUFFIX)
                storageOperation.createFinalTable(streamConfig, EXPECTED_SUFFIX, true)
            }
            confirmVerified(storageOperation)

            clearMocks(storageOperation)
            streamOperations.finalizeTable(
                streamConfig,
                StreamSyncSummary(0, AirbyteStreamStatus.COMPLETE)
            )

            verifySequence {
                storageOperation.cleanupStage(streamId)
                storageOperation.overwriteStage(streamId, EXPECTED_SUFFIX)
                storageOperation.overwriteFinalTable(streamConfig, EXPECTED_SUFFIX)
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
            "io.airbyte.integrations.base.destination.operation.AbstractStreamOperationTest#generationIds"
        )
        fun existingTempRawTableMatchingGeneration(existingTempTableGeneration: Long?) {
            val initialState =
                mockk<DestinationInitialStatus<MinimumDestinationState.Impl>> {
                    every { streamConfig } returns this@Truncate.streamConfig
                    every { initialTempRawTableStatus.rawTableExists } returns true
                    every { isFinalTablePresent } returns false
                    every {
                        destinationState.withSoftReset<MinimumDestinationState.Impl>(any())
                    } returns destinationState
                }
            every { storageOperation.getStageGeneration(streamId, EXPECTED_SUFFIX) } returns
                existingTempTableGeneration

            val streamOperations = TestStreamOperation(storageOperation, initialState)

            verifySequence {
                storageOperation.getStageGeneration(streamId, EXPECTED_SUFFIX)
                storageOperation.prepareStage(streamId, EXPECTED_SUFFIX)
                storageOperation.createFinalTable(streamConfig, "", false)
            }
            confirmVerified(storageOperation)

            clearMocks(storageOperation)
            streamOperations.finalizeTable(
                streamConfig,
                StreamSyncSummary(42, AirbyteStreamStatus.COMPLETE)
            )

            verifySequence {
                storageOperation.cleanupStage(streamId)
                storageOperation.overwriteStage(streamId, EXPECTED_SUFFIX)
                storageOperation.typeAndDedupe(
                    streamConfig,
                    Optional.empty(),
                    "",
                )
            }
            confirmVerified(storageOperation)
            checkUnnecessaryStub(initialState, initialState.destinationState)
        }

        @Test
        fun existingTempRawTableWrongGeneration() {
            val initialState =
                mockk<DestinationInitialStatus<MinimumDestinationState.Impl>> {
                    every { streamConfig } returns this@Truncate.streamConfig
                    every { initialTempRawTableStatus.rawTableExists } returns true
                    every { isFinalTablePresent } returns false
                    every {
                        destinationState.withSoftReset<MinimumDestinationState.Impl>(any())
                    } returns destinationState
                }
            every { storageOperation.getStageGeneration(streamId, EXPECTED_SUFFIX) } returns -1

            val streamOperations = TestStreamOperation(storageOperation, initialState)

            verifySequence {
                storageOperation.getStageGeneration(streamId, EXPECTED_SUFFIX)
                storageOperation.prepareStage(streamId, EXPECTED_SUFFIX, replace = true)
                storageOperation.createFinalTable(streamConfig, "", false)
            }
            confirmVerified(storageOperation)

            clearMocks(storageOperation)
            streamOperations.finalizeTable(
                streamConfig,
                StreamSyncSummary(42, AirbyteStreamStatus.COMPLETE)
            )

            verifySequence {
                storageOperation.cleanupStage(streamId)
                storageOperation.overwriteStage(streamId, EXPECTED_SUFFIX)
                storageOperation.typeAndDedupe(
                    streamConfig,
                    Optional.empty(),
                    "",
                )
            }
            confirmVerified(storageOperation)
            checkUnnecessaryStub(initialState, initialState.destinationState)
        }
    }

    @Nested
    inner class NormalSync {
        @ParameterizedTest
        @MethodSource(
            "io.airbyte.integrations.base.destination.operation.AbstractStreamOperationTest#nonOverwriteStreamConfigs"
        )
        fun emptyDestination(streamConfig: StreamConfig) {
            val initialState =
                mockk<DestinationInitialStatus<MinimumDestinationState.Impl>> {
                    every { this@mockk.streamConfig } returns streamConfig
                    every { initialTempRawTableStatus.rawTableExists } returns false
                    every { initialRawTableStatus.maxProcessedTimestamp } returns Optional.empty()
                    every { isFinalTablePresent } returns false
                    every {
                        destinationState.withSoftReset<MinimumDestinationState.Impl>(any())
                    } returns destinationState
                }

            val streamOperations = TestStreamOperation(storageOperation, initialState)

            verifySequence {
                storageOperation.prepareStage(streamId, "")
                storageOperation.createFinalTable(streamConfig, "", false)
            }
            confirmVerified(storageOperation)

            clearMocks(storageOperation)
            streamOperations.finalizeTable(
                streamConfig,
                StreamSyncSummary(42, AirbyteStreamStatus.COMPLETE)
            )

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
        fun existingFinalTableSchemaMismatch(streamConfig: StreamConfig) {
            val initialState =
                mockk<DestinationInitialStatus<MinimumDestinationState.Impl>> {
                    every { this@mockk.streamConfig } returns streamConfig
                    every { initialTempRawTableStatus.rawTableExists } returns false
                    every { initialRawTableStatus.maxProcessedTimestamp } returns Optional.empty()
                    every { isFinalTablePresent } returns true
                    every { isSchemaMismatch } returns true
                    every {
                        destinationState.withSoftReset<MinimumDestinationState.Impl>(any())
                    } returns destinationState
                }

            val streamOperations = TestStreamOperation(storageOperation, initialState)

            verifySequence {
                storageOperation.prepareStage(streamId, "")
                storageOperation.softResetFinalTable(streamConfig)
            }
            confirmVerified(storageOperation)

            clearMocks(storageOperation)
            streamOperations.finalizeTable(
                streamConfig,
                StreamSyncSummary(42, AirbyteStreamStatus.COMPLETE)
            )

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
        fun existingFinalTableSchemaMatch(streamConfig: StreamConfig) {
            val initialState =
                mockk<DestinationInitialStatus<MinimumDestinationState.Impl>> {
                    every { this@mockk.streamConfig } returns streamConfig
                    every { initialTempRawTableStatus.rawTableExists } returns false
                    every { initialRawTableStatus.maxProcessedTimestamp } returns Optional.empty()
                    every { isFinalTablePresent } returns true
                    every { isSchemaMismatch } returns false
                    every { destinationState } returns MinimumDestinationState.Impl(false)
                }

            val streamOperations = TestStreamOperation(storageOperation, initialState)

            verifySequence {
                storageOperation.prepareStage(streamId, "")
                // No soft reset - we can just reuse the existing table.
            }
            confirmVerified(storageOperation)

            clearMocks(storageOperation)
            streamOperations.finalizeTable(
                streamConfig,
                StreamSyncSummary(42, AirbyteStreamStatus.COMPLETE)
            )

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

        /**
         * Run a test where the current sync emits 0 records. Verify all the behavior around
         * existing raw tables.
         */
        @ParameterizedTest
        @MethodSource(
            "io.airbyte.integrations.base.destination.operation.AbstractStreamOperationTest#normalSyncRawTableStatuses"
        )
        fun testRawTableHandling(
            shouldRunTD: Boolean,
            timestampFilter: Optional<Instant>,
            realRawTableStatus: InitialRawTableStatus,
            tempRawTableStatus: InitialRawTableStatus,
            streamConfig: StreamConfig,
        ) {
            val initialState =
                mockk<DestinationInitialStatus<MinimumDestinationState.Impl>> {
                    every { this@mockk.streamConfig } returns streamConfig
                    every { initialRawTableStatus } returns realRawTableStatus
                    every { initialTempRawTableStatus } returns tempRawTableStatus
                    every { isFinalTablePresent } returns true
                    every { isSchemaMismatch } returns false
                    every { destinationState } returns MinimumDestinationState.Impl(false)
                }

            val streamOperations = TestStreamOperation(storageOperation, initialState)

            verifySequence {
                storageOperation.prepareStage(streamId, "")
                if (tempRawTableStatus.rawTableExists) {
                    storageOperation.transferFromTempStage(streamId, EXPECTED_SUFFIX)
                }
                // No soft reset - we can just reuse the existing table.
            }
            confirmVerified(storageOperation)

            clearMocks(storageOperation)
            streamOperations.finalizeTable(
                streamConfig,
                StreamSyncSummary(0, AirbyteStreamStatus.COMPLETE)
            )

            verifySequence {
                storageOperation.cleanupStage(streamId)
                if (shouldRunTD) {
                    storageOperation.typeAndDedupe(
                        streamConfig,
                        timestampFilter,
                        "",
                    )
                }
            }
            confirmVerified(storageOperation)
            checkUnnecessaryStub(initialState)
        }

        @ParameterizedTest
        @MethodSource(
            "io.airbyte.integrations.base.destination.operation.AbstractStreamOperationTest#nonOverwriteStreamConfigs"
        )
        fun existingFinalTableAndStateRequiresSoftReset(streamConfig: StreamConfig) {
            val initialState =
                mockk<DestinationInitialStatus<MinimumDestinationState.Impl>> {
                    every { this@mockk.streamConfig } returns streamConfig
                    every { initialTempRawTableStatus.rawTableExists } returns false
                    every { initialRawTableStatus.maxProcessedTimestamp } returns Optional.empty()
                    every { isFinalTablePresent } returns true
                    every { isSchemaMismatch } returns false
                    every { destinationState } returns MinimumDestinationState.Impl(true)
                }

            val streamOperations = TestStreamOperation(storageOperation, initialState)

            verifySequence {
                storageOperation.prepareStage(streamId, "")
                storageOperation.softResetFinalTable(streamConfig)
            }
            confirmVerified(storageOperation)

            clearMocks(storageOperation)
            streamOperations.finalizeTable(
                streamConfig,
                StreamSyncSummary(42, AirbyteStreamStatus.COMPLETE)
            )

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
        fun existingNonEmptyFinalTableNoNewRecords(
            streamConfig: StreamConfig,
            hasUnprocessedRecords: Boolean
        ) {
            val initialState =
                mockk<DestinationInitialStatus<MinimumDestinationState.Impl>> {
                    every { this@mockk.streamConfig } returns streamConfig
                    every { initialTempRawTableStatus.rawTableExists } returns false
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

            verifySequence { storageOperation.prepareStage(streamId, "") }
            confirmVerified(storageOperation)

            clearMocks(storageOperation)
            streamOperations.finalizeTable(
                streamConfig,
                StreamSyncSummary(0, AirbyteStreamStatus.COMPLETE)
            )

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

        const val EXPECTED_SUFFIX = "_airbyte_tmp"
        val maxProcessedTimestamp = Optional.of(Instant.parse("2024-01-23T12:34:56Z"))

        private val appendStreamConfig =
            StreamConfig(
                streamId,
                DestinationSyncMode.APPEND,
                listOf(),
                Optional.empty(),
                columns,
                generationId = 21,
                minimumGenerationId = 0,
                syncId = 0
            )
        private val dedupStreamConfig =
            StreamConfig(
                streamId,
                DestinationSyncMode.APPEND_DEDUP,
                listOf(pk1, pk2),
                Optional.of(cursor),
                columns,
                generationId = 21,
                minimumGenerationId = 0,
                syncId = 0
            )
        private val streamConfigs = arrayOf(appendStreamConfig, dedupStreamConfig)

        // junit 5 doesn't support class-level parameterization...
        // so we have to hack this in a somewhat dumb way.
        // append and dedup should behave identically from StreamOperations' POV,
        // so just shove them together.
        @JvmStatic
        fun nonOverwriteStreamConfigs(): Stream<Arguments> =
            streamConfigs.map { Arguments.of(it) }.stream()

        // Some tests are further parameterized, which this method supports.
        @JvmStatic
        fun nonOverwriteStreamConfigsAndBoolean(): Stream<Arguments> =
            Stream.of(
                Arguments.of(appendStreamConfig, true),
                Arguments.of(appendStreamConfig, false),
                Arguments.of(dedupStreamConfig, true),
                Arguments.of(dedupStreamConfig, false),
            )

        // ValueSource and CsvSource don't support null, so we have to write an entire method.
        @JvmStatic
        fun generationIds(): Stream<Arguments> =
            Stream.of(
                Arguments.of(null),
                Arguments.of(21L),
            )

        /**
         * The five arguments are:
         * * whether we need to run T+D (assuming the sync emitted 0 records and was successful)
         * * if we need to run T+D, the timestamp filter to use.
         * * the initial real raw table status
         * * the initial temp raw table status
         * * the StreamConfig to use
         */
        @JvmStatic
        fun normalSyncRawTableStatuses(): Stream<Arguments> {
            val validRawTableStatuses =
                arrayOf(
                    // The raw table doesn't exist
                    InitialRawTableStatus(
                        rawTableExists = false,
                        hasUnprocessedRecords = false,
                        maxProcessedTimestamp = Optional.empty()
                    ),
                    // The raw table exists, but is empty
                    InitialRawTableStatus(
                        rawTableExists = true,
                        hasUnprocessedRecords = false,
                        maxProcessedTimestamp = Optional.empty()
                    ),
                    // The raw table exists and contains records, but they're all processed and old
                    InitialRawTableStatus(
                        rawTableExists = true,
                        hasUnprocessedRecords = false,
                        maxProcessedTimestamp = Optional.of(Instant.parse("2023-01-01T12:34:56Z")),
                    ),
                    // The raw table exists and contains records, but they're all processed and new
                    InitialRawTableStatus(
                        rawTableExists = true,
                        hasUnprocessedRecords = false,
                        maxProcessedTimestamp = Optional.of(Instant.parse("2024-01-01T12:34:56Z")),
                    ),
                    // The raw table exists and contains unprocessed records. Already-processed
                    // records are old.
                    InitialRawTableStatus(
                        rawTableExists = true,
                        hasUnprocessedRecords = true,
                        maxProcessedTimestamp = Optional.of(Instant.parse("2023-01-01T12:34:56Z")),
                    ),
                    // The raw table exists and contains unprocessed records. Already-processed
                    // records are new.
                    InitialRawTableStatus(
                        rawTableExists = true,
                        hasUnprocessedRecords = true,
                        maxProcessedTimestamp = Optional.of(Instant.parse("2024-01-01T12:34:56Z")),
                    )
                )
            return streamConfigs
                .flatMap { streamConfig ->
                    validRawTableStatuses.flatMap { realRawStatus ->
                        validRawTableStatuses.map { tempRawStatus ->
                            val shouldRunTD =
                                realRawStatus.hasUnprocessedRecords ||
                                    tempRawStatus.hasUnprocessedRecords

                            // Find the lower of the two timestamps.
                            val timestampFilter =
                                if (realRawStatus.maxProcessedTimestamp.isPresent) {
                                    if (tempRawStatus.maxProcessedTimestamp.isPresent) {
                                        if (
                                            realRawStatus.maxProcessedTimestamp
                                                .get()
                                                .isBefore(tempRawStatus.maxProcessedTimestamp.get())
                                        ) {
                                            realRawStatus.maxProcessedTimestamp
                                        } else {
                                            tempRawStatus.maxProcessedTimestamp
                                        }
                                    } else {
                                        realRawStatus.maxProcessedTimestamp
                                    }
                                } else {
                                    tempRawStatus.maxProcessedTimestamp
                                }

                            Arguments.of(
                                shouldRunTD,
                                timestampFilter,
                                realRawStatus,
                                tempRawStatus,
                                streamConfig,
                            )
                        }
                    }
                }
                .stream()
        }
    }
}
