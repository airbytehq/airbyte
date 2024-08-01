/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.operation

import com.fasterxml.jackson.databind.node.IntNode
import io.airbyte.cdk.integrations.destination.StreamSyncSummary
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteRecordMessage
import io.airbyte.integrations.base.destination.operation.AbstractStreamOperation.Companion.NO_SUFFIX
import io.airbyte.integrations.base.destination.operation.AbstractStreamOperation.Companion.TMP_TABLE_SUFFIX
import io.airbyte.integrations.base.destination.typing_deduping.ColumnId
import io.airbyte.integrations.base.destination.typing_deduping.DestinationInitialStatus
import io.airbyte.integrations.base.destination.typing_deduping.ImportType
import io.airbyte.integrations.base.destination.typing_deduping.InitialRawTableStatus
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig
import io.airbyte.integrations.base.destination.typing_deduping.StreamId
import io.airbyte.integrations.base.destination.typing_deduping.migrators.MinimumDestinationState
import io.airbyte.protocol.models.v0.AirbyteStreamStatusTraceMessage.AirbyteStreamStatus
import io.github.oshai.kotlinlogging.KotlinLogging
import io.kotest.common.ExperimentalKotest
import io.kotest.common.runBlocking
import io.kotest.property.Exhaustive
import io.kotest.property.PropTestConfig
import io.kotest.property.assume
import io.kotest.property.exhaustive.boolean
import io.kotest.property.exhaustive.cartesian
import io.kotest.property.exhaustive.cartesianTriples
import io.kotest.property.exhaustive.collection
import io.kotest.property.exhaustive.concat
import io.kotest.property.exhaustive.enum
import io.kotest.property.exhaustive.map
import io.kotest.property.exhaustive.of
import io.kotest.property.forAll
import java.time.Instant
import java.util.Optional
import java.util.stream.Stream
import kotlin.test.assertEquals
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertAll

private val logger = KotlinLogging.logger {}

/**
 * This test executes all valid permutations of syncs. In particular, it exercises:
 * * Whether the raw, temp raw, final, temp final tables exist at the start of the sync
 * * If they exist, whether they contain records
 * * If they contain records, what generation(s) those records belong to
 * * And whether those records have been processed by T+D
 * * If the final table exists, whether its schema matches the expected schema
 * * All combinations of generation and min generation
 * * Dedupe vs append mode
 *
 * [doTest] just runs through the stages of a sync (setup, record writing, finalization). It's built
 * using a very basic in-memory StorageOperation - [TestStorageOperation].
 */
class AbstractStreamOperationRidiculousTest {
    // PropTestConfig is marked experimental for some reason,
    // but kotest docs say you should just use it.
    @OptIn(ExperimentalKotest::class)
    @Test
    fun doTest() {
        runBlocking {
            // for my own curiosity: stats on how many tests cases are generated / valid
            var totalGeneratedCount = 0
            var validCount = 0
            forAll(
                // There are a _lot_ of invalid test cases (nearly 99%).
                // And I think it's better to generate all test cases + discard them
                // instead of trying to only generate valid test cases.
                // So configure kotest to not fail on a high discard ratio.
                PropTestConfig(maxDiscardPercentage = 100),
                potentialGenerations,
                potentialMinimumGenerations,
                potentialPreexistingRawTables,
                potentialPreexistingFinalTables,
                potentialPreexistingTempRawTables,
                potentialPreexistingTempFinalTables,
                potentialImportTypes,
                potentialSchemaMismatch,
                potentialTerminalStatuses,
                potentialNewRecords,
            ) {
                generationId,
                minimumGenerationId,
                preexistingRawTable,
                preexistingFinalTable,
                preexistingTempRawTable,
                preexistingTempFinalTable,
                importType,
                schemaMismatch,
                terminalStatus,
                newRecords,
                ->
                totalGeneratedCount++
                // `assume` throws AssumptionFailedException if the input is false.
                // kotest will discard the test case on this exception.
                assume(
                    isValidTestCase(
                        preexistingRawTable,
                        preexistingTempRawTable,
                        preexistingFinalTable,
                        preexistingTempFinalTable,
                        importType,
                        generationId,
                        minimumGenerationId,
                        schemaMismatch,
                        terminalStatus,
                        newRecords,
                    )
                )
                validCount++

                val (
                    initialRawTables: Map<String, Table>,
                    initialFinalTables: Map<String, Table>,
                    initialStatus: DestinationInitialStatus<MinimumDestinationState.Impl>,
                    expectedRawRecords: Map<String, Table>,
                    expectedFinalRecords: Map<String, Table>
                ) =
                    constructTestArguments(
                        preexistingRawTable,
                        preexistingTempRawTable,
                        preexistingFinalTable,
                        preexistingTempFinalTable,
                        importType,
                        generationId,
                        minimumGenerationId,
                        schemaMismatch,
                        terminalStatus,
                        newRecords,
                    )

                val storageOperation =
                    TestStorageOperation(
                        initialRawTables.toMutableMap(),
                        initialFinalTables.toMutableMap(),
                    )
                val streamOperation = TestStreamOperation(storageOperation, initialStatus)
                streamOperation.writeRecords(
                    initialStatus.streamConfig,
                    newRecords
                        .map {
                            PartialAirbyteMessage()
                                .withRecord(
                                    PartialAirbyteRecordMessage()
                                        .withNamespace(
                                            initialStatus.streamConfig.id.originalNamespace
                                        )
                                        .withStream(initialStatus.streamConfig.id.originalName)
                                        .withEmittedAt(it.extractedAt.toEpochMilli())
                                        // A real record would have an object node here,
                                        // but our "test data" doesn't need all of that.
                                        .withData(IntNode(it.id))
                                )
                        }
                        .stream()
                )
                streamOperation.finalizeTable(
                    initialStatus.streamConfig,
                    StreamSyncSummary(newRecords.size.toLong(), terminalStatus)
                )

                // we _could_ return false here, but throwing an assertion exception
                // generates a more useful error message.
                assertAll(
                    {
                        assertEquals(
                            expectedRawRecords,
                            storageOperation.rawTables,
                            "Raw tables were incorrect"
                        )
                    },
                    {
                        assertEquals(
                            expectedFinalRecords,
                            storageOperation.finalTables,
                            "Final tables were incorrect"
                        )
                    }
                )

                logger.info { "--- END OF TEST CASE ---" }

                true
            }
            logger.info {
                "Executed $validCount / $totalGeneratedCount = ${Math.round(1000.0 * validCount / totalGeneratedCount) / 10.0}% test cases"
            }
        }
    }

    companion object {
        private val streamId =
            StreamId(
                "final_namespace",
                "final_name",
                "raw_namespace",
                "raw_name",
                "original_namespace",
                "original_name",
            )

        val potentialGenerations = Exhaustive.of(0, 1, 42)
        val potentialMinimumGenerations = Exhaustive.of(0, 1, 42)

        // Tables are represented as List<Record>?
        // where `null` means the table does not exist at the start of the sync.
        val potentialPreexistingRawTables =
            potentialGenerations.values
                .map {
                    // For each generation, we generate all possible sets of records..
                    Exhaustive.collection(
                        generatePotentialRecordsAnyLoadedState(it) + listOf(emptyList())
                    )
                }
                // Then we build up all possible combinations between those
                // possible generations.
                .fold(Exhaustive.of(emptyList())) {
                    acc: Exhaustive<List<Record>>,
                    incomingGeneration: Exhaustive<List<Record>> ->
                    acc.cartesian(incomingGeneration) { a, b -> a + b }
                }
                // Or the table doesn't exist
                .concat(Exhaustive.of(null))
                .map { records -> records?.sortedBy { it.id } }
        val potentialPreexistingFinalTables =
            potentialGenerations.values
                .map {
                    // For each generation, we generate all possible sets of records.
                    Exhaustive.of(
                        emptyList(),
                        generatePotentialRecords(generationId = it, loaded = true)
                    )
                }
                // Identical to raw tables - build all combinations between
                // possible generations.
                .fold(Exhaustive.of(emptyList())) {
                    acc: Exhaustive<List<Record>>,
                    incomingGeneration: Exhaustive<List<Record>> ->
                    acc.cartesian(incomingGeneration) { a, b -> a + b }
                }
                // Or the table doesn't exist
                .concat(Exhaustive.of(null))
                .map { records -> records?.sortedBy { it.id } }
        val potentialPreexistingTempRawTables =
        // The temp raw table always contains records from a single generation,
        // and we never execute T+D against the raw table (i.e. loaded=false).
        Exhaustive.collection(
                    potentialGenerations.values.map {
                        generatePotentialRecords(generationId = it, loaded = false)
                    },
                )
                // or is empty/nonexistent
                .concat(Exhaustive.of(emptyList(), null))
        // The temp final table is always nonexistent or empty
        val potentialPreexistingTempFinalTables = Exhaustive.of<List<Record>?>(null, emptyList())

        val potentialImportTypes = Exhaustive.enum<ImportType>()
        val potentialSchemaMismatch = Exhaustive.boolean()
        // A sync either emits 0, 1, or 2 records.
        // We set extracted_at to something relatively far in the future,
        // because the preexisting records all have extracted_at set to
        // generationId * 1000.
        val potentialNewRecords =
            Exhaustive.of(
                emptyList(),
                listOf(InputRecord(1, Instant.ofEpochMilli(100_000_000))),
                listOf(
                    InputRecord(1, Instant.ofEpochMilli(100_000_000)),
                    InputRecord(2, Instant.ofEpochMilli(100_000_000)),
                ),
            )
        // We can't just use AirbyteStreamStatus.entries, because that includes
        // non-terminal statuses like RUNNING.
        val potentialTerminalStatuses =
            Exhaustive.of(AirbyteStreamStatus.COMPLETE, AirbyteStreamStatus.INCOMPLETE)

        /**
         * Generate all possible combinations of records for a single generation, across all
         * possible loaded states..
         *
         * Note that we set extracted_at to generationId * 1000. This emulates expected behavior,
         * where later generations are extracted later.
         */
        private fun generatePotentialRecordsAnyLoadedState(generationId: Int): List<List<Record>> =
            Exhaustive.boolean()
                .cartesianTriples()
                .map { (a, b, c) ->
                    val potentialRecords = generatePotentialRecords(generationId, loaded = true)
                    listOf(
                        potentialRecords[0].copy(loaded = a),
                        potentialRecords[1].copy(loaded = b),
                        potentialRecords[2].copy(loaded = c),
                    )
                }
                .concat(Exhaustive.of(emptyList()))
                .values

        /**
         * Generate potential records for a single generation and loaded state. Includes a duplicate
         * record (id=2).
         *
         * If you change the number of records here, make sure to update
         * [generatePotentialRecordsAnyLoadedState] to match it.
         */
        private fun generatePotentialRecords(
            generationId: Int,
            loaded: Boolean,
        ): List<Record> =
            listOf(
                Record(
                    id = 1,
                    extractedAt = Instant.ofEpochMilli(generationId * 1000L),
                    generationId = generationId.toLong(),
                    loaded = loaded,
                ),
                Record(
                    id = 2,
                    extractedAt = Instant.ofEpochMilli(generationId * 1000L),
                    generationId = generationId.toLong(),
                    loaded = loaded,
                ),
                // Duplicate record
                Record(
                    id = 2,
                    extractedAt = Instant.ofEpochMilli(generationId * 1000L + 1),
                    generationId = generationId.toLong(),
                    loaded = loaded,
                ),
            )

        /**
         * Check whether a test case is reasonable. E.g. all existing records are from the current
         * generation or lower, etc.
         *
         * It's expected that the vast majority of test cases are invalid, simply because most
         * combinations of records x generations are incoherent.
         */
        // Intentionally have some unused params.
        // It shows which params can contribute to a test case being
        // valid or invalid.
        // Specifically: importType, terminalStatus, and newRecords are all valid
        // no matter what. Which makes sense:
        // append/dedupe has no bearing on whether a set of tables "makes sense"
        // (e.g. a user could run a sync in dedupe mode, but have duplicate records
        // in their final table, because their previous sync ran in append mode).
        // By definition, we should be able to handle both COMPLETE and INCOMPLETE
        // no matter what the initial state of the world was.
        // And similarly, we should be able to handle any number of records.
        private fun isValidTestCase(
            preexistingRawTable: List<Record>?,
            preexistingTempRawTable: List<Record>?,
            preexistingFinalTable: List<Record>?,
            preexistingTempFinalTable: List<Record>?,
            importType: ImportType,
            generationId: Int,
            minimumGenerationId: Int,
            schemaMismatch: Boolean,
            terminalStatus: AirbyteStreamStatus,
            newRecords: List<InputRecord>
        ): Boolean {
            // We don't support truncating at arbitrary generation
            if (minimumGenerationId != 0 && minimumGenerationId != generationId) {
                return false
            }

            if (preexistingRawTable != null) {
                // The raw table should only ever contain records from strictly less than the min
                // generation,
                // or min_gen <= it <= generationId.
                // If we don't meet that requirement, skip the test case.
                // (This is because when we _start_ a truncate sync, we write to a temp raw table,
                // and the generation ID will already have been incremented;
                // and when we _commit_ a truncate sync, we nuke the previous raw table.
                // So there's never a time when the real raw table contains both records from before
                // and after the min generation.)
                // Also, for sanity, skip tests where there are records from a future generation.
                val rawTableBelowMinGen =
                    preexistingRawTable.all { it.generationId < minimumGenerationId }
                val rawTableAboveMinGen =
                    preexistingRawTable.all { it.generationId in minimumGenerationId..generationId }
                if (!rawTableBelowMinGen && !rawTableAboveMinGen) {
                    return false
                }

                if (preexistingRawTable.isNotEmpty() && rawTableAboveMinGen) {
                    // If we've already committed the temp raw table, then it shouldn't exist
                    // anymore.
                    if (preexistingTempRawTable != null) {
                        return false
                    }
                }
            }
            // More basic sanity checks
            // This intentionally doesn't include preexistingRawTable, because
            // we already did some more stringent checks on it.
            val allTablesWithinCurrentGeneration =
                ((preexistingTempRawTable
                        ?: emptyList()) +
                        (preexistingFinalTable ?: emptyList()) +
                        (preexistingTempFinalTable ?: emptyList()))
                    .all { it.generationId <= generationId }
            if (!allTablesWithinCurrentGeneration) {
                return false
            }

            // Every record in the final table should exist in the raw table
            if (preexistingFinalTable != null) {
                for (finalRecord in preexistingFinalTable) {
                    val matchingRawRecord =
                        (preexistingRawTable ?: emptyList()).firstOrNull {
                            it.id == finalRecord.id &&
                                it.generationId == finalRecord.generationId &&
                                it.loaded
                        }
                    if (matchingRawRecord == null) {
                        return false
                    }
                }
            }

            // Schema mismatch only makes sense if the final table exists.
            // If the final table doesn't exist, then we can't have a
            // schema mismatch.
            if (schemaMismatch && preexistingFinalTable == null) {
                return false
            }

            return true
        }

        /**
         * Convert the test state to what a sync would actually execute with. For example, the test
         * state includes a List<Record> representing the entire table. But a real sync never
         * executes `select *`, it only ever needs `select generation_id limit 1`, etc.
         *
         * We also compute the expected records here (i.e. after the sync, what records should be in
         * each of the temp/real raw/final tables).
         */
        data class TestArguments(
            val initialRawTables: Map<String, Table>,
            val initialFinalTables: Map<String, Table>,
            val initialStatus: DestinationInitialStatus<MinimumDestinationState.Impl>,
            val expectedRawRecords: Map<String, Table>,
            val expectedFinalRecords: Map<String, Table>,
        )

        private fun constructTestArguments(
            preexistingRawTable: List<Record>?,
            preexistingTempRawTable: List<Record>?,
            preexistingFinalTable: List<Record>?,
            preexistingTempFinalTable: List<Record>?,
            importType: ImportType,
            generationId: Int,
            minimumGenerationId: Int,
            schemaMismatch: Boolean,
            terminalStatus: AirbyteStreamStatus,
            newRecords: List<InputRecord>,
        ): TestArguments {
            val initialStatus =
                DestinationInitialStatus(
                    StreamConfig(
                        streamId,
                        importType,
                        primaryKey =
                            listOf(
                                ColumnId(
                                    "id",
                                    "id",
                                    "id",
                                ),
                            ),
                        cursor = Optional.empty(),
                        columns = linkedMapOf(),
                        generationId = generationId.toLong(),
                        minimumGenerationId = minimumGenerationId.toLong(),
                        syncId = 1234L,
                    ),
                    isFinalTablePresent = preexistingFinalTable != null,
                    buildInitialRawTableStatus(preexistingRawTable),
                    buildInitialRawTableStatus(preexistingTempRawTable),
                    schemaMismatch,
                    isFinalTableEmpty = preexistingFinalTable?.isEmpty() ?: true,
                    MinimumDestinationState.Impl(needsSoftReset = false),
                    finalTableGenerationId = preexistingFinalTable?.firstOrNull()?.generationId,
                    finalTempTableGenerationId =
                        preexistingTempFinalTable?.firstOrNull()?.generationId,
                )

            // Computing the expected records is _ludicrously_ complicated,
            // which reflects how difficult it is to describe all the nonsense
            // we do during a sync >.>

            val isNotTruncateSync = minimumGenerationId == 0
            // We write to the real raw table in normal syncs,
            // or in truncate syncs if the existing raw table has valid generations.
            val shouldWriteToRealRawTable =
            // Non truncate syncs always write to the real raw table
            isNotTruncateSync ||
                    // Truncate syncs write to a temp raw table if one exists.
                    // If one doesn't already exist, then we check whether the
                    // real raw table exists and matches our min generation,
                    // and use it if it does.
                    (preexistingTempRawTable == null &&
                        preexistingRawTable != null &&
                        preexistingRawTable.all { it.generationId >= minimumGenerationId })
            // We need to know about soft resets for the raw table to compute
            // the loaded-ness of raw records.
            val shouldSoftReset =
            // Normal syncs do a soft reset when there's a schema mismatch
            (schemaMismatch && isNotTruncateSync) ||
                    // Truncate syncs reuse the final table if it is nonempty
                    // and of the correct generation, and therefore trigger
                    // a soft reset if there's a schema mismatch.
                    (!isNotTruncateSync &&
                        schemaMismatch &&
                        // If there's a schema mismatch, then by definition the final table exists,
                        // so use !!
                        preexistingFinalTable!!.isNotEmpty() &&
                        preexistingFinalTable.all { it.generationId >= minimumGenerationId })
            val syncSuccess = terminalStatus == AirbyteStreamStatus.COMPLETE
            // Whether we actually wrote records to the real raw table.
            val committedToRealRawTable = syncSuccess || shouldWriteToRealRawTable
            // Non-truncate syncs always "commit" (i.e. write their data to the
            // real raw table + trigger T+D if there are records to process).
            // Similarly, successful syncs always commit (if there are any
            // records to process).
            // But unsuccessful truncate syncs do _not_ commit.
            val shouldCommit = isNotTruncateSync || syncSuccess
            val shouldRunTypingDeduping =
                shouldCommit &&
                    (newRecords.isNotEmpty() ||
                        (preexistingRawTable?.any { !it.loaded } ?: false) ||
                        (preexistingTempRawTable?.any { !it.loaded } ?: false))
            val newRecordsToLoad =
                newRecords.map {
                    Record(
                        it.id,
                        it.extractedAt,
                        generationId.toLong(),
                        loaded = false,
                    )
                }
            val expectedRawRecords =
                mutableMapOf<String, Table>().run {
                    if (committedToRealRawTable) {
                        // If our sync was successful, then we should have all the records from both
                        // the
                        // temp and real raw tables, plus the new records, filtered by generation
                        // ID.
                        // The same is true if we were writing directly to the real raw table,
                        // because
                        // we should have moved the temp table's records into the real table.
                        put(
                            NO_SUFFIX,
                            Table.of(
                                ((preexistingRawTable ?: emptyList()).map {
                                        it.copy(loaded = it.loaded || shouldSoftReset)
                                    } + (preexistingTempRawTable ?: emptyList()) + newRecordsToLoad)
                                    .filter { it.generationId >= minimumGenerationId }
                                    .map { it.copy(loaded = it.loaded || shouldRunTypingDeduping) },
                            )
                        )
                    } else {
                        // Otherwise, we just leave the existing table untouched.
                        if (preexistingRawTable != null) {
                            put(NO_SUFFIX, Table.of(preexistingRawTable))
                        }

                        // If we didn't commit to the real raw table,
                        // then we have a temp final table.
                        // It includes preexisting records, plus new records, filtered
                        // by generation ID.
                        put(
                            TMP_TABLE_SUFFIX,
                            Table.of(
                                ((preexistingTempRawTable ?: emptyList()) + newRecordsToLoad)
                                    .filter { it.generationId >= minimumGenerationId }
                            ),
                        )
                    }

                    this
                }

            val targetingRealFinalTable =
            // Normal syncs always use the real final table
            isNotTruncateSync ||
                    // Truncate syncs when the real final table doesn't yet exist
                    // write to the real final table
                    preexistingFinalTable == null ||
                    // Or truncate syncs where the final table has the correct schema and is empty
                    (!schemaMismatch && preexistingFinalTable.isEmpty()) ||
                    // Or truncate syncs where the final table is non-empty but has the correct
                    // generation.
                    // (schema mismatch is irrelevant here, we'll trigger a soft reset.)
                    (preexistingFinalTable.isNotEmpty() &&
                        preexistingFinalTable.all { it.generationId >= minimumGenerationId })
            val expectedFinalRecords =
                mutableMapOf<String, Table>().run {
                    if (syncSuccess || targetingRealFinalTable) {
                        // Successful syncs always write to the real final table.
                        // Some other syncs also _target_ the real final table,
                        // though they maybe don't actually write anything to it.
                        // For those syncs, if there was a preexisting temp final
                        // table for some reason, we should just leave it alone.
                        if (targetingRealFinalTable) {
                            preexistingTempFinalTable?.let { put(TMP_TABLE_SUFFIX, Table.of(it)) }
                        }

                        if (shouldRunTypingDeduping) {
                            // If we ran a soft reset, then we discard the final table.
                            // Otherwise, we preserve its records.
                            val preexistingFinalTableRecordsToExpect =
                                if (shouldSoftReset || preexistingFinalTable == null) {
                                    emptyList()
                                } else {
                                    preexistingFinalTable
                                }
                            // Similarly, if we ran a soft reset, then we re-T+D the entire raw
                            // table.
                            // Otherwise, we only take unloaded records.
                            val preexistingRawTableRecordsToExpect =
                                if (shouldSoftReset) {
                                    preexistingRawTable
                                } else {
                                    preexistingRawTable?.filter { !it.loaded }
                                }
                                    ?: emptyList()
                            put(
                                NO_SUFFIX,
                                Table.of(
                                    sortAndMaybeDedupeRecords(
                                            importType,
                                            preexistingFinalTableRecordsToExpect +
                                                preexistingRawTableRecordsToExpect +
                                                (preexistingTempRawTable ?: emptyList()) +
                                                newRecordsToLoad
                                        )
                                        .filter { it.generationId >= minimumGenerationId }
                                        .map { it.copy(loaded = true) }
                                )
                            )
                        } else {
                            // It's possible for us to target the real final table, but not actually
                            // run T+D. For example, a truncate sync could receive a stream COMPLETE
                            // status, but have 0 records to process.
                            // In particular, this means that it's possible for DEDUPE syncs to have
                            // duplicate records after a successful sync. E.g. a user runs an APPEND
                            // sync, switches to DEDUPE, and runs a sync which emits 0 records.
                            val realFinalRecordsToExpect =
                                if (shouldSoftReset) {
                                    sortAndMaybeDedupeRecords(
                                        importType,
                                        preexistingRawTable ?: emptyList()
                                    )
                                } else {
                                    preexistingFinalTable ?: emptyList()
                                }
                            put(
                                NO_SUFFIX,
                                Table.of(
                                    realFinalRecordsToExpect
                                        .map { it.copy(loaded = true) }
                                        // Regardless, we should always obey the min gen ID.
                                        .filter { it.generationId >= minimumGenerationId }
                                )
                            )
                        }
                    } else {
                        // This sync is targeting the temp final table, and therefore definitely
                        // didn't execute T+D.
                        // We preserve both the real and temp final tables,
                        // modulo soft reset.
                        val realFinalRecordsToExpect =
                            if (shouldSoftReset) {
                                sortAndMaybeDedupeRecords(
                                        importType,
                                        preexistingRawTable ?: emptyList()
                                    )
                                    .map { it.copy(loaded = true) }
                            } else {
                                // If a final table already existed, leave it unchanged.
                                // Otherwise, we create an empty final table.
                                preexistingFinalTable ?: emptyList()
                            }
                        put(NO_SUFFIX, Table.of(realFinalRecordsToExpect))

                        // In a non-truncate sync where a temp final table already exists for some
                        // reason,
                        // leave it unchanged.
                        // In a truncate sync where we don't commit, we always create a temp final
                        // table.
                        put(TMP_TABLE_SUFFIX, Table.of(emptyList()))
                    }

                    this
                }

            val initialRawTables = mutableMapOf<String, Table>()
            preexistingRawTable?.let { initialRawTables[NO_SUFFIX] = Table.of(it) }
            preexistingTempRawTable?.let { initialRawTables[TMP_TABLE_SUFFIX] = Table.of(it) }

            val initialFinalTables = mutableMapOf<String, Table>()
            preexistingFinalTable?.let { initialFinalTables[NO_SUFFIX] = Table.of(it) }
            preexistingTempFinalTable?.let { initialFinalTables[TMP_TABLE_SUFFIX] = Table.of(it) }

            return TestArguments(
                initialRawTables,
                initialFinalTables,
                initialStatus,
                expectedRawRecords,
                expectedFinalRecords,
            )
        }

        private fun buildInitialRawTableStatus(preexistingRawTable: List<Record>?) =
            InitialRawTableStatus(
                rawTableExists = preexistingRawTable != null,
                hasUnprocessedRecords = (preexistingRawTable?.any { !it.loaded }) ?: false,
                // The typical min timestamp logic.
                // Finds the earliest unloaded record and subtracts 1 millis
                // to account for a strict `>` comparison,
                // or if all records are loaded, finds the latest record.
                maxProcessedTimestamp =
                    Optional.ofNullable(
                        preexistingRawTable
                            ?.filter { !it.loaded }
                            ?.minOfOrNull { it.extractedAt.minusMillis(1) }
                            ?: preexistingRawTable?.maxOfOrNull { it.extractedAt },
                    ),
            )
    }
}

data class InputRecord(val id: Int, val extractedAt: Instant)

data class Record(
    val id: Int,
    val extractedAt: Instant,
    val generationId: Long,
    val loaded: Boolean = false
)

data class Table(val records: MutableList<Record>) {
    fun addRecords(generationId: Long, records: List<InputRecord>) {
        this.records.addAll(records.map { Record(it.id, it.extractedAt, generationId) })
    }

    companion object {
        // Can't just declare `constructor(records: List<Record>): this(records.toMutableList())`
        // because `constructor Table(records: List<Record>)` and
        // `constructor Table(records: MutableList<Record>)` have the same JVM signature
        fun of(records: List<Record>) = Table(records.toMutableList())
    }
}

/**
 * Dumb in-memory StorageOperation implementation. Assumes that each sync has exactly one stream,
 * and therefore we can store a map from table name suffix to the contents of that table.
 */
class TestStorageOperation(
    val rawTables: MutableMap<String, Table> = mutableMapOf(),
    val finalTables: MutableMap<String, Table> = mutableMapOf(),
) : StorageOperation<List<InputRecord>> {
    override fun prepareStage(streamId: StreamId, suffix: String, replace: Boolean) {
        if (replace || !rawTables.containsKey(suffix)) {
            rawTables[suffix] = Table(mutableListOf())
        }
    }

    override fun overwriteStage(streamId: StreamId, suffix: String) {
        rawTables[NO_SUFFIX] = rawTables[suffix]!!
        rawTables.remove(suffix)
    }

    override fun transferFromTempStage(streamId: StreamId, suffix: String) {
        if (!rawTables.containsKey(NO_SUFFIX)) {
            rawTables[suffix] = Table(mutableListOf())
        }
        rawTables[NO_SUFFIX]!!.records.addAll(rawTables[suffix]!!.records)
        rawTables.remove(suffix)
    }

    override fun getStageGeneration(streamId: StreamId, suffix: String): Long? =
        rawTables[suffix]!!.let { it.records.firstOrNull()?.generationId }

    override fun cleanupStage(streamId: StreamId) {
        // noop
    }

    override fun createFinalTable(streamConfig: StreamConfig, suffix: String, replace: Boolean) {
        if (replace || !finalTables.containsKey(suffix)) {
            finalTables[suffix] = Table(mutableListOf())
        }
    }

    override fun softResetFinalTable(streamConfig: StreamConfig) {
        createFinalTable(streamConfig, "_ab_soft_reset", true)
        rawTables[NO_SUFFIX]!!.records.replaceAll { it.copy(loaded = false) }
        typeAndDedupe(streamConfig, Optional.empty(), "_ab_soft_reset")
        overwriteFinalTable(streamConfig, "_ab_soft_reset")
    }

    override fun overwriteFinalTable(streamConfig: StreamConfig, tmpTableSuffix: String) {
        finalTables[NO_SUFFIX] = finalTables[tmpTableSuffix]!!
        finalTables.remove(tmpTableSuffix)
    }

    override fun typeAndDedupe(
        streamConfig: StreamConfig,
        maxProcessedTimestamp: Optional<Instant>,
        finalTableSuffix: String
    ) {
        val recordsToTypeAndDedupe =
            rawTables[NO_SUFFIX]!!.records.filter {
                !it.loaded && it.extractedAt.isAfter(maxProcessedTimestamp.orElse(Instant.MIN))
            }
        rawTables[NO_SUFFIX]!!.records.replaceAll {
            it.copy(loaded = it.loaded || recordsToTypeAndDedupe.contains(it))
        }

        val finalTable = finalTables[finalTableSuffix]!!
        val newFinalTable =
            sortAndMaybeDedupeRecords(
                streamConfig.postImportAction,
                finalTable.records + recordsToTypeAndDedupe.map { it.copy(loaded = true) },
            )
        finalTable.records.clear()
        finalTable.records.addAll(newFinalTable)
    }

    override fun writeToStage(streamConfig: StreamConfig, suffix: String, data: List<InputRecord>) {
        rawTables[suffix]!!.addRecords(streamConfig.generationId, data)
    }
}

class TestStreamOperation(
    private val storageOperation: StorageOperation<List<InputRecord>>,
    destinationInitialStatus: DestinationInitialStatus<MinimumDestinationState.Impl>
) :
    AbstractStreamOperation<MinimumDestinationState.Impl, List<InputRecord>>(
        storageOperation,
        destinationInitialStatus,
    ) {
    override fun writeRecordsImpl(
        streamConfig: StreamConfig,
        suffix: String,
        stream: Stream<PartialAirbyteMessage>
    ) {
        storageOperation.writeToStage(
            streamConfig,
            suffix,
            stream
                .map {
                    InputRecord(
                        id = it.record!!.data!!.asInt(),
                        extractedAt = Instant.ofEpochMilli(it.record!!.emittedAt)
                    )
                }
                .toList()
        )
    }
}

fun sortAndMaybeDedupeRecords(importType: ImportType, records: List<Record>): List<Record> =
    if (importType == ImportType.DEDUPE) {
            records
                .groupBy { it.id }
                .mapValues { (_, recordsForId) -> recordsForId.maxBy { it.extractedAt } }
                .values
                .toList()
        } else {
            records.toList()
        }
        .sortedBy { it.id }
