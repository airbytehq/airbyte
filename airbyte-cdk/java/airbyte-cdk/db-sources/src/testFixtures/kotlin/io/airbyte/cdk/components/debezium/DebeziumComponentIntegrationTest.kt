/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.components.debezium

import io.airbyte.cdk.components.ComponentRunner
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.Field
import io.airbyte.protocol.models.JsonSchemaType
import io.airbyte.protocol.models.v0.*
import java.time.Duration
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

/** Test framework for testing [DebeziumProducer] against real relational databases. */
abstract class DebeziumComponentIntegrationTest(private val lsnMapper: LsnMapper<*>) {

    @JvmField
    val catalog: AirbyteCatalog =
        AirbyteCatalog()
            .withStreams(
                listOf(
                    CatalogHelpers.createAirbyteStream(
                            "kv",
                            "public",
                            Field.of("k", JsonSchemaType.INTEGER),
                            Field.of("v", JsonSchemaType.STRING)
                        )
                        .withSupportedSyncModes(listOf(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
                        .withSourceDefinedPrimaryKey(listOf(listOf("v"))),
                    CatalogHelpers.createAirbyteStream(
                            "eventlog",
                            "public",
                            Field.of("id", JsonSchemaType.STRING),
                            Field.of("entry", JsonSchemaType.STRING)
                        )
                        .withSupportedSyncModes(listOf(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
                        .withSourceDefinedPrimaryKey(listOf(listOf("id")))
                )
            )

    @JvmField
    val configuredCatalog: ConfiguredAirbyteCatalog =
        CatalogHelpers.toDefaultConfiguredCatalog(catalog).apply {
            streams.forEach { it.syncMode = SyncMode.INCREMENTAL }
        }

    /** Applies the list of changes to the source database tables. */
    abstract fun applyToSource(changes: List<Change>)

    /** Bulk-inserts rows into the KV table in the source database. */
    abstract fun bulkInsertSourceKVTable(numRows: Long)

    /** Debezium state with the current LSN. */
    abstract fun currentSourceState(): DebeziumState

    /** Producer builder, all set up except for the bound checker. */
    abstract fun producerBuilder(): DebeziumProducer.Builder

    fun collectRepeatedly(
        input: DebeziumState,
        consumerBuilder: DebeziumConsumer.Builder = DebeziumConsumer.Builder(),
        maxTime: Duration = Duration.ofSeconds(1L),
        upperBound: DebeziumState = currentSourceState(),
    ): Pair<Sequence<DebeziumRecord>, DebeziumState> {
        val runner = runner(consumerBuilder, maxTime, upperBound)
        val output = runner.collectRepeatedly(input, upperBound).toList()
        return Pair(output.flatMap { it.first }.asSequence(), output.last().second)
    }

    fun runner(
        consumerBuilder: DebeziumConsumer.Builder = DebeziumConsumer.Builder(),
        maxTime: Duration = Duration.ofSeconds(1L),
        upperBound: DebeziumState = currentSourceState(),
    ): ComponentRunner<DebeziumRecord, DebeziumState> {
        val builderCopy =
            DebeziumConsumer.Builder(
                maxRecords = Math.min(100_000L, consumerBuilder.maxRecords),
                maxRecordBytes = Math.min(1_000_000_000L, consumerBuilder.maxRecordBytes),
            )
        return ComponentRunner(
            "debezium",
            producerBuilder().withBoundChecker(lsnMapper, upperBound),
            builderCopy,
            maxTime,
            lsnMapper.comparator()
        )
    }

    @JvmRecord
    data class Change(val table: Table, val oldValue: Value?, val newValue: Value?) {
        enum class Table(val valueColumnName: String) {
            KV("v"),
            EVENTLOG("entry")
        }

        enum class Value {
            FOO,
            BAR,
            BAZ,
            QUUX,
            XYZZY
        }

        enum class Kind {
            INSERT,
            UPDATE,
            DELETE
        }

        fun kind(): Kind {
            if (oldValue == null) {
                return Kind.INSERT
            }
            if (newValue == null) {
                return Kind.DELETE
            }
            return Kind.UPDATE
        }
    }

    fun insert(table: Change.Table, newValue: Change.Value): Change {
        return Change(table, null, newValue)
    }

    fun delete(table: Change.Table, oldValue: Change.Value): Change {
        return Change(table, oldValue, null)
    }

    fun update(table: Change.Table, oldValue: Change.Value, newValue: Change.Value): Change {
        return Change(table, oldValue, newValue)
    }

    val initialInsert: List<Change> =
        listOf(
            insert(Change.Table.KV, Change.Value.FOO),
            insert(Change.Table.KV, Change.Value.BAR),
            insert(Change.Table.EVENTLOG, Change.Value.FOO),
            insert(Change.Table.EVENTLOG, Change.Value.BAR)
        )

    val updateKV: List<Change> =
        listOf(
            update(Change.Table.KV, Change.Value.FOO, Change.Value.QUUX),
            update(Change.Table.KV, Change.Value.BAR, Change.Value.XYZZY)
        )

    val deleteEventLog: List<Change> =
        listOf(
            delete(Change.Table.EVENTLOG, Change.Value.FOO),
            delete(Change.Table.EVENTLOG, Change.Value.BAR)
        )

    val subsequentInsert: List<Change> =
        listOf(
            insert(Change.Table.KV, Change.Value.BAZ),
            insert(Change.Table.EVENTLOG, Change.Value.BAZ)
        )

    @Test
    fun testNoProgress() {
        applyToSource(initialInsert)
        val state1: DebeziumState = currentSourceState()
        val output1 = collectRepeatedly(state1)
        assertNoProgress(state1, output1)
    }

    @Test
    fun testHeartbeatsProgress() {
        val numRows = 10_000L

        val state0: DebeziumState = currentSourceState()
        // Insert just one record.
        // We need this or Debezium will never actually start firing heartbeats.
        applyToSource(initialInsert.take(1))
        // Consume the WAL from right before the insert to right after it.
        val state1: DebeziumState = currentSourceState()
        // Make sure there's more entries in the WAL after the insert.
        bulkInsertSourceKVTable(numRows)
        val (records2, state2) = collectRepeatedly(state0, upperBound = state1)
        assertProgress(state0, state1)
        assertProgress(state0, state2)
        assertDataCountWithinBounds(1, records2, numRows)
    }

    @Test
    fun testCRUD() {
        val state0: DebeziumState = currentSourceState()

        applyToSource(initialInsert)
        val (records1, state1) = collectRepeatedly(state0)
        assertProgress(state0, state1)
        assertData(records1, initialInsert)

        applyToSource(deleteEventLog)
        val (records2, state2) = collectRepeatedly(state1)
        assertProgress(state1, state2)
        assertData(records2, deleteEventLog)

        applyToSource(updateKV)
        val (records3, state3) = collectRepeatedly(state2)
        assertProgress(state2, state3)
        assertData(records3, updateKV)

        applyToSource(subsequentInsert)
        val (records4, state4) = collectRepeatedly(state3)
        assertProgress(state3, state4)
        assertData(records4, subsequentInsert)
    }

    @Test
    fun testCompletesWithEnoughRecords() {
        val numRows = 10_000L
        val maxRecords = 10L
        val state0: DebeziumState = currentSourceState()

        bulkInsertSourceKVTable(numRows)
        val (records1, state1) =
            runner(consumerBuilder = DebeziumConsumer.Builder(maxRecords = maxRecords))
                .collect(state0)
        assertProgress(state0, state1)
        // We actually get more than we bargained for, but that's OK.
        assertDataCountWithinBounds(maxRecords + 1, records1, numRows)

        val (records2, state2) = collectRepeatedly(state0)
        assertProgress(state0, state2)
        Assertions.assertEquals(numRows, records2.toList().size.toLong())
    }

    @Test
    fun testCompletesWhenOutOfBounds() {
        val numRowsInBatch = 10_000L
        val state0: DebeziumState = currentSourceState()

        bulkInsertSourceKVTable(numRowsInBatch)
        val state1: DebeziumState = currentSourceState()

        bulkInsertSourceKVTable(numRowsInBatch)
        val (output2, state2) = collectRepeatedly(state0, upperBound = state1)
        assertProgress(state0, state2)
        assertDataCountWithinBounds(numRowsInBatch, output2, 2 * numRowsInBatch)
    }

    @Test
    fun testCheckpointing() {
        val numRowsInBatch = 10_000L
        val numBatches = 4

        val state0: DebeziumState = currentSourceState()

        for (i in 1..numBatches) {
            bulkInsertSourceKVTable(numRowsInBatch)
        }

        val (records1, _) =
            collectRepeatedly(state0, consumerBuilder = DebeziumConsumer.Builder(maxRecords = 1))
        Assertions.assertEquals(numBatches * numRowsInBatch, records1.count().toLong())
    }

    fun assertNoProgress(
        input: Pair<Sequence<DebeziumRecord>, DebeziumState>,
        output: Pair<Sequence<DebeziumRecord>, DebeziumState>
    ) {
        assertNoProgress(input.second, output)
    }

    fun assertNoProgress(
        input: DebeziumState,
        output: Pair<Sequence<DebeziumRecord>, DebeziumState>
    ) {
        assertNoProgress(input, output.second)
        Assertions.assertEquals(0, output.first.count())
    }

    @Suppress("UNCHECKED_CAST")
    fun assertNoProgress(input: DebeziumState, output: DebeziumState) {
        val inputLsn = lsnMapper.get(input.offset) as Comparable<Any>
        val outputLsn = lsnMapper.get(output.offset) as Comparable<Any>
        Assertions.assertEquals(
            0,
            inputLsn.compareTo(outputLsn),
            "$inputLsn not equal to $outputLsn"
        )
    }

    fun assertProgress(
        input: Pair<Sequence<DebeziumRecord>, DebeziumState>,
        output: Pair<Sequence<DebeziumRecord>, DebeziumState>
    ) {
        assertProgress(input.second, output)
    }

    fun assertProgress(
        input: DebeziumState,
        output: Pair<Sequence<DebeziumRecord>, DebeziumState>
    ) {
        assertProgress(input, output.second)
        Assertions.assertNotEquals(0, output.first.count())
    }

    @Suppress("UNCHECKED_CAST")
    fun assertProgress(input: DebeziumState, output: DebeziumState) {
        Assertions.assertNotEquals(
            Jsons.serialize(Jsons.jsonNode(input.offset.debeziumOffset)),
            Jsons.serialize(Jsons.jsonNode(output.offset.debeziumOffset))
        )
        val inputLsn = lsnMapper.get(input.offset) as Comparable<Any>
        val outputLsn = lsnMapper.get(output.offset) as Comparable<Any>
        Assertions.assertTrue(inputLsn < outputLsn, "expected $inputLsn to precede $outputLsn")
    }

    @SafeVarargs
    fun assertData(records: Sequence<DebeziumRecord>, vararg expected: List<Change>) {
        val expectedAsInsertsOrDeletes =
            expected
                .flatMap { it }
                .map {
                    if (it.kind() == Change.Kind.UPDATE) insert(it.table, it.newValue!!) else it
                }
        val actualAsInsertsOrDeletes: List<Change> =
            records
                .map { r ->
                    val table = Change.Table.valueOf(r.source()["table"].asText().uppercase())
                    val before =
                        r.before()[table.valueColumnName]?.asText()?.uppercase()?.let {
                            Change.Value.valueOf(it)
                        }
                    val after =
                        r.after()[table.valueColumnName]?.asText()?.uppercase()?.let {
                            Change.Value.valueOf(it)
                        }
                    Change(table, if (after == null) before else null, after)
                }
                .toList()
        Assertions.assertEquals(expectedAsInsertsOrDeletes, actualAsInsertsOrDeletes)
    }

    fun assertDataCountWithinBounds(
        lowerBoundInclusive: Long,
        records: Sequence<DebeziumRecord>,
        upperBoundExclusive: Long,
    ) {
        val n = records.toList().size.toLong()
        Assertions.assertTrue(
            n >= lowerBoundInclusive,
            "expected no less than $lowerBoundInclusive records, obtained $n"
        )
        Assertions.assertTrue(
            n < upperBoundExclusive,
            "expected less than $upperBoundExclusive records, obtained $n"
        )
    }
}
