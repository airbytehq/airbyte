/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.debezium

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import com.google.common.collect.*
import io.airbyte.cdk.integrations.base.Source
import io.airbyte.cdk.testutils.TestDatabase
import io.airbyte.commons.json.Jsons
import io.airbyte.commons.util.AutoCloseableIterators
import io.airbyte.protocol.models.Field
import io.airbyte.protocol.models.JsonSchemaType
import io.airbyte.protocol.models.v0.*
import java.util.*
import java.util.function.Consumer
import java.util.stream.Collectors
import java.util.stream.Stream
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.slf4j.Logger
import org.slf4j.LoggerFactory

abstract class CdcSourceTest<S : Source, T : TestDatabase<*, T, *>> {
    @JvmField protected var testdb: T = createTestDatabase()

    protected open fun createTableSqlFmt(): String {
        return "CREATE TABLE %s.%s(%s);"
    }

    protected open fun createSchemaSqlFmt(): String {
        return "CREATE SCHEMA %s;"
    }

    protected open fun modelsSchema(): String {
        return "models_schema"
    }

    /** The schema of a random table which is used as a new table in snapshot test */
    protected open fun randomSchema(): String {
        return "models_schema_random"
    }

    protected val catalog: AirbyteCatalog
        get() =
            AirbyteCatalog()
                .withStreams(
                    java.util.List.of(
                        CatalogHelpers.createAirbyteStream(
                                MODELS_STREAM_NAME,
                                modelsSchema(),
                                Field.of(COL_ID, JsonSchemaType.INTEGER),
                                Field.of(COL_MAKE_ID, JsonSchemaType.INTEGER),
                                Field.of(COL_MODEL, JsonSchemaType.STRING)
                            )
                            .withSupportedSyncModes(
                                Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL)
                            )
                            .withSourceDefinedPrimaryKey(
                                java.util.List.of(java.util.List.of(COL_ID))
                            )
                    )
                )

    protected val configuredCatalog: ConfiguredAirbyteCatalog
        get() {
            val configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(catalog)
            configuredCatalog.streams.forEach(
                Consumer { s: ConfiguredAirbyteStream -> s.syncMode = SyncMode.INCREMENTAL }
            )
            return configuredCatalog
        }

    protected abstract fun createTestDatabase(): T

    protected abstract fun source(): S

    protected abstract fun config(): JsonNode?

    protected abstract fun cdcLatestTargetPosition(): CdcTargetPosition<*>

    protected abstract fun extractPosition(record: JsonNode?): CdcTargetPosition<*>?

    protected abstract fun assertNullCdcMetaData(data: JsonNode?)

    protected abstract fun assertCdcMetaData(data: JsonNode?, deletedAtNull: Boolean)

    protected abstract fun removeCDCColumns(data: ObjectNode?)

    protected abstract fun addCdcMetadataColumns(stream: AirbyteStream?)

    protected abstract fun addCdcDefaultCursorField(stream: AirbyteStream?)

    protected abstract fun assertExpectedStateMessages(stateMessages: List<AirbyteStateMessage>)

    // TODO: this assertion should be added into test cases in this class, we will need to implement
    // corresponding iterator for other connectors before
    // doing so.
    protected open fun assertExpectedStateMessageCountMatches(
        stateMessages: List<AirbyteStateMessage>,
        totalCount: Long
    ) {
        // Do nothing.
    }

    @BeforeEach
    protected open fun setup() {
        testdb = createTestDatabase()
        createTables()
        populateTables()
    }

    protected fun createTables() {
        // create and populate actual table
        val actualColumns =
            ImmutableMap.of(COL_ID, "INTEGER", COL_MAKE_ID, "INTEGER", COL_MODEL, "VARCHAR(200)")
        testdb
            .with(createSchemaSqlFmt(), modelsSchema())
            .with(
                createTableSqlFmt(),
                modelsSchema(),
                MODELS_STREAM_NAME,
                columnClause(actualColumns, Optional.of(COL_ID))
            )

        // Create random table.
        // This table is not part of Airbyte sync. It is being created just to make sure the schemas
        // not
        // being synced by Airbyte are not causing issues with our debezium logic.
        val randomColumns =
            ImmutableMap.of(
                COL_ID + "_random",
                "INTEGER",
                COL_MAKE_ID + "_random",
                "INTEGER",
                COL_MODEL + "_random",
                "VARCHAR(200)"
            )
        if (randomSchema() != modelsSchema()) {
            testdb!!.with(createSchemaSqlFmt(), randomSchema())
        }
        testdb!!.with(
            createTableSqlFmt(),
            randomSchema(),
            RANDOM_TABLE_NAME,
            columnClause(randomColumns, Optional.of(COL_ID + "_random"))
        )
    }

    protected fun populateTables() {
        for (recordJson in MODEL_RECORDS) {
            writeModelRecord(recordJson)
        }

        for (recordJson in MODEL_RECORDS_RANDOM) {
            writeRecords(
                recordJson,
                randomSchema(),
                RANDOM_TABLE_NAME,
                COL_ID + "_random",
                COL_MAKE_ID + "_random",
                COL_MODEL + "_random"
            )
        }
    }

    @AfterEach
    protected open fun tearDown() {
        try {
            testdb!!.close()
        } catch (e: Throwable) {
            LOGGER.error("exception during teardown", e)
        }
    }

    protected open fun columnClause(
        columnsWithDataType: Map<String, String>,
        primaryKey: Optional<String>
    ): String {
        val columnClause = StringBuilder()
        var i = 0
        for ((key, value) in columnsWithDataType) {
            columnClause.append(key)
            columnClause.append(" ")
            columnClause.append(value)
            if (i < (columnsWithDataType.size - 1)) {
                columnClause.append(",")
                columnClause.append(" ")
            }
            i++
        }
        primaryKey.ifPresent { s: String? ->
            columnClause.append(", PRIMARY KEY (").append(s).append(")")
        }

        return columnClause.toString()
    }

    protected fun writeModelRecord(recordJson: JsonNode) {
        writeRecords(recordJson, modelsSchema(), MODELS_STREAM_NAME, COL_ID, COL_MAKE_ID, COL_MODEL)
    }

    protected open fun writeRecords(
        recordJson: JsonNode,
        dbName: String?,
        streamName: String?,
        idCol: String?,
        makeIdCol: String?,
        modelCol: String?
    ) {
        testdb!!.with(
            "INSERT INTO %s.%s (%s, %s, %s) VALUES (%s, %s, '%s');",
            dbName,
            streamName,
            idCol,
            makeIdCol,
            modelCol,
            recordJson[idCol].asInt(),
            recordJson[makeIdCol].asInt(),
            recordJson[modelCol].asText()
        )
    }

    protected open fun deleteMessageOnIdCol(streamName: String?, idCol: String?, idValue: Int) {
        testdb!!.with("DELETE FROM %s.%s WHERE %s = %s", modelsSchema(), streamName, idCol, idValue)
    }

    protected open fun deleteCommand(streamName: String?) {
        testdb!!.with("DELETE FROM %s.%s", modelsSchema(), streamName)
    }

    protected open fun updateCommand(
        streamName: String?,
        modelCol: String?,
        modelVal: String?,
        idCol: String?,
        idValue: Int
    ) {
        testdb!!.with(
            "UPDATE %s.%s SET %s = '%s' WHERE %s = %s",
            modelsSchema(),
            streamName,
            modelCol,
            modelVal,
            COL_ID,
            11
        )
    }

    protected fun extractRecordMessages(messages: List<AirbyteMessage>): Set<AirbyteRecordMessage> {
        val recordsPerStream = extractRecordMessagesStreamWise(messages)
        val consolidatedRecords: MutableSet<AirbyteRecordMessage> = HashSet()
        recordsPerStream.values.forEach(
            Consumer { c: Set<AirbyteRecordMessage>? -> consolidatedRecords.addAll(c!!) }
        )
        return consolidatedRecords
    }

    protected fun extractRecordMessagesStreamWise(
        messages: List<AirbyteMessage>
    ): Map<String, Set<AirbyteRecordMessage>> {
        val recordsPerStream: MutableMap<String, MutableList<AirbyteRecordMessage>> = HashMap()
        for (message in messages) {
            if (message.type == AirbyteMessage.Type.RECORD) {
                val recordMessage = message.record
                recordsPerStream
                    .computeIfAbsent(recordMessage.stream) { c: String? -> ArrayList() }
                    .add(recordMessage)
            }
        }

        val recordsPerStreamWithNoDuplicates: MutableMap<String, Set<AirbyteRecordMessage>> =
            HashMap()
        for ((streamName, records) in recordsPerStream) {
            val recordMessageSet: Set<AirbyteRecordMessage> = HashSet(records)
            Assertions.assertEquals(
                records.size,
                recordMessageSet.size,
                "Expected no duplicates in airbyte record message output for a single sync."
            )
            recordsPerStreamWithNoDuplicates[streamName] = recordMessageSet
        }

        return recordsPerStreamWithNoDuplicates
    }

    protected fun extractStateMessages(messages: List<AirbyteMessage>): List<AirbyteStateMessage> {
        return messages
            .stream()
            .filter { r: AirbyteMessage -> r.type == AirbyteMessage.Type.STATE }
            .map { obj: AirbyteMessage -> obj.state }
            .collect(Collectors.toList())
    }

    protected fun assertExpectedRecords(
        expectedRecords: Set<JsonNode>,
        actualRecords: Set<AirbyteRecordMessage>
    ) {
        // assume all streams are cdc.
        assertExpectedRecords(
            expectedRecords,
            actualRecords,
            actualRecords
                .stream()
                .map { obj: AirbyteRecordMessage -> obj.stream }
                .collect(Collectors.toSet())
        )
    }

    private fun assertExpectedRecords(
        expectedRecords: Set<JsonNode>,
        actualRecords: Set<AirbyteRecordMessage>,
        cdcStreams: Set<String>
    ) {
        assertExpectedRecords(
            expectedRecords,
            actualRecords,
            cdcStreams,
            STREAM_NAMES,
            modelsSchema()
        )
    }

    protected fun assertExpectedRecords(
        expectedRecords: Set<JsonNode>?,
        actualRecords: Set<AirbyteRecordMessage>,
        cdcStreams: Set<String>,
        streamNames: Set<String?>,
        namespace: String?
    ) {
        val actualData =
            actualRecords
                .stream()
                .map<JsonNode> { recordMessage: AirbyteRecordMessage ->
                    Assertions.assertTrue(streamNames.contains(recordMessage.stream))
                    Assertions.assertNotNull(recordMessage.emittedAt)

                    Assertions.assertEquals(namespace, recordMessage.namespace)

                    val data = recordMessage.data

                    if (cdcStreams.contains(recordMessage.stream)) {
                        assertCdcMetaData(data, true)
                    } else {
                        assertNullCdcMetaData(data)
                    }

                    removeCDCColumns(data as ObjectNode)
                    data
                }
                .collect(Collectors.toSet())

        Assertions.assertEquals(expectedRecords, actualData)
    }

    @Test
    @Throws(Exception::class)
    fun testExistingData() {
        val targetPosition = cdcLatestTargetPosition()
        val read = source()!!.read(config()!!, configuredCatalog, null)
        val actualRecords = AutoCloseableIterators.toListAndClose(read)

        val recordMessages = extractRecordMessages(actualRecords)
        val stateMessages = extractStateMessages(actualRecords)

        Assertions.assertNotNull(targetPosition)
        recordMessages.forEach(
            Consumer { record: AirbyteRecordMessage ->
                compareTargetPositionFromTheRecordsWithTargetPostionGeneratedBeforeSync(
                    targetPosition,
                    record
                )
            }
        )

        assertExpectedRecords(HashSet(MODEL_RECORDS), recordMessages)
        assertExpectedStateMessages(stateMessages)
        assertExpectedStateMessageCountMatches(stateMessages, MODEL_RECORDS.size.toLong())
    }

    protected open fun compareTargetPositionFromTheRecordsWithTargetPostionGeneratedBeforeSync(
        targetPosition: CdcTargetPosition<*>?,
        record: AirbyteRecordMessage
    ) {
        Assertions.assertEquals(extractPosition(record.data), targetPosition)
    }

    @Test // When a record is deleted, produces a deletion record.
    @Throws(Exception::class)
    fun testDelete() {
        val read1 = source().read(config()!!, configuredCatalog, null)
        val actualRecords1 = AutoCloseableIterators.toListAndClose(read1)
        val stateMessages1 = extractStateMessages(actualRecords1)
        assertExpectedStateMessages(stateMessages1)

        deleteMessageOnIdCol(MODELS_STREAM_NAME, COL_ID, 11)
        waitForCdcRecords(modelsSchema(), MODELS_STREAM_NAME, 1)

        val state = Jsons.jsonNode(listOf(stateMessages1[stateMessages1.size - 1]))
        val read2 = source().read(config()!!, configuredCatalog, state)
        val actualRecords2 = AutoCloseableIterators.toListAndClose(read2)
        val recordMessages2: List<AirbyteRecordMessage> =
            ArrayList(extractRecordMessages(actualRecords2))
        val stateMessages2 = extractStateMessages(actualRecords2)
        assertExpectedStateMessagesFromIncrementalSync(stateMessages2)
        assertExpectedStateMessageCountMatches(stateMessages2, 1)
        Assertions.assertEquals(1, recordMessages2.size)
        Assertions.assertEquals(11, recordMessages2[0].data[COL_ID].asInt())
        assertCdcMetaData(recordMessages2[0].data, false)
    }

    protected open fun assertExpectedStateMessagesFromIncrementalSync(
        stateMessages: List<AirbyteStateMessage>
    ) {
        assertExpectedStateMessages(stateMessages)
    }

    @Test // When a record is updated, produces an update record.
    @Throws(Exception::class)
    fun testUpdate() {
        val updatedModel = "Explorer"
        val read1 = source().read(config()!!, configuredCatalog, null)
        val actualRecords1 = AutoCloseableIterators.toListAndClose(read1)
        val stateMessages1 = extractStateMessages(actualRecords1)
        assertExpectedStateMessages(stateMessages1)

        updateCommand(MODELS_STREAM_NAME, COL_MODEL, updatedModel, COL_ID, 11)
        waitForCdcRecords(modelsSchema(), MODELS_STREAM_NAME, 1)

        val state = Jsons.jsonNode(listOf(stateMessages1[stateMessages1.size - 1]))
        val read2 = source().read(config()!!, configuredCatalog, state)
        val actualRecords2 = AutoCloseableIterators.toListAndClose(read2)
        val recordMessages2: List<AirbyteRecordMessage> =
            ArrayList(extractRecordMessages(actualRecords2))
        val stateMessages2 = extractStateMessages(actualRecords2)
        assertExpectedStateMessagesFromIncrementalSync(stateMessages2)
        Assertions.assertEquals(1, recordMessages2.size)
        Assertions.assertEquals(11, recordMessages2[0].data[COL_ID].asInt())
        Assertions.assertEquals(updatedModel, recordMessages2[0].data[COL_MODEL].asText())
        assertCdcMetaData(recordMessages2[0].data, true)
        assertExpectedStateMessageCountMatches(stateMessages2, 1)
    }

    @Test // Verify that when data is inserted into the database while a sync is happening and after
    // the first
    // sync, it all gets replicated.
    @Throws(Exception::class)
    protected fun testRecordsProducedDuringAndAfterSync() {
        val recordsCreatedBeforeTestCount = MODEL_RECORDS.size
        var expectedRecords = recordsCreatedBeforeTestCount
        var expectedRecordsInCdc = 0
        val recordsToCreate = 20
        // first batch of records. 20 created here and 6 created in setup method.
        for (recordsCreated in 0 until recordsToCreate) {
            val record =
                Jsons.jsonNode(
                    ImmutableMap.of(
                        COL_ID,
                        100 + recordsCreated,
                        COL_MAKE_ID,
                        1,
                        COL_MODEL,
                        "F-$recordsCreated"
                    )
                )
            writeModelRecord(record)
            expectedRecords++
            expectedRecordsInCdc++
        }
        waitForCdcRecords(modelsSchema(), MODELS_STREAM_NAME, expectedRecordsInCdc)

        val firstBatchIterator = source().read(config()!!, configuredCatalog, null)
        val dataFromFirstBatch = AutoCloseableIterators.toListAndClose(firstBatchIterator)
        val stateAfterFirstBatch = extractStateMessages(dataFromFirstBatch)
        assertExpectedStateMessagesForRecordsProducedDuringAndAfterSync(stateAfterFirstBatch)
        val recordsFromFirstBatch = extractRecordMessages(dataFromFirstBatch)
        Assertions.assertEquals(expectedRecords, recordsFromFirstBatch.size)

        // second batch of records again 20 being created
        for (recordsCreated in 0 until recordsToCreate) {
            val record =
                Jsons.jsonNode(
                    ImmutableMap.of(
                        COL_ID,
                        200 + recordsCreated,
                        COL_MAKE_ID,
                        1,
                        COL_MODEL,
                        "F-$recordsCreated"
                    )
                )
            writeModelRecord(record)
            expectedRecords++
            expectedRecordsInCdc++
        }
        waitForCdcRecords(modelsSchema(), MODELS_STREAM_NAME, expectedRecordsInCdc)

        val state = Jsons.jsonNode(listOf(stateAfterFirstBatch[stateAfterFirstBatch.size - 1]))
        val secondBatchIterator = source().read(config()!!, configuredCatalog, state)
        val dataFromSecondBatch = AutoCloseableIterators.toListAndClose(secondBatchIterator)

        val stateAfterSecondBatch = extractStateMessages(dataFromSecondBatch)
        assertExpectedStateMessagesFromIncrementalSync(stateAfterSecondBatch)

        val recordsFromSecondBatch = extractRecordMessages(dataFromSecondBatch)
        Assertions.assertEquals(
            recordsToCreate,
            recordsFromSecondBatch.size,
            "Expected 20 records to be replicated in the second sync."
        )

        // sometimes there can be more than one of these at the end of the snapshot and just before
        // the
        // first incremental.
        val recordsFromFirstBatchWithoutDuplicates = removeDuplicates(recordsFromFirstBatch)
        val recordsFromSecondBatchWithoutDuplicates = removeDuplicates(recordsFromSecondBatch)

        Assertions.assertTrue(
            recordsCreatedBeforeTestCount < recordsFromFirstBatchWithoutDuplicates.size,
            "Expected first sync to include records created while the test was running."
        )
        Assertions.assertEquals(
            expectedRecords,
            recordsFromFirstBatchWithoutDuplicates.size +
                recordsFromSecondBatchWithoutDuplicates.size
        )
    }

    protected open fun assertExpectedStateMessagesForRecordsProducedDuringAndAfterSync(
        stateAfterFirstBatch: List<AirbyteStateMessage>
    ) {
        assertExpectedStateMessages(stateAfterFirstBatch)
    }

    @Test // When both incremental CDC and full refresh are configured for different streams in a
    // sync, the
    // data is replicated as expected.
    @Throws(Exception::class)
    fun testCdcAndFullRefreshInSameSync() {
        val configuredCatalog = Jsons.clone(configuredCatalog)

        val MODEL_RECORDS_2: List<JsonNode> =
            ImmutableList.of(
                Jsons.jsonNode(ImmutableMap.of(COL_ID, 110, COL_MAKE_ID, 1, COL_MODEL, "Fiesta-2")),
                Jsons.jsonNode(ImmutableMap.of(COL_ID, 120, COL_MAKE_ID, 1, COL_MODEL, "Focus-2")),
                Jsons.jsonNode(ImmutableMap.of(COL_ID, 130, COL_MAKE_ID, 1, COL_MODEL, "Ranger-2")),
                Jsons.jsonNode(ImmutableMap.of(COL_ID, 140, COL_MAKE_ID, 2, COL_MODEL, "GLA-2")),
                Jsons.jsonNode(ImmutableMap.of(COL_ID, 150, COL_MAKE_ID, 2, COL_MODEL, "A 220-2")),
                Jsons.jsonNode(ImmutableMap.of(COL_ID, 160, COL_MAKE_ID, 2, COL_MODEL, "E 350-2"))
            )

        val columns =
            ImmutableMap.of(COL_ID, "INTEGER", COL_MAKE_ID, "INTEGER", COL_MODEL, "VARCHAR(200)")
        testdb!!.with(
            createTableSqlFmt(),
            modelsSchema(),
            MODELS_STREAM_NAME + "_2",
            columnClause(columns, Optional.of(COL_ID))
        )

        for (recordJson in MODEL_RECORDS_2) {
            writeRecords(
                recordJson,
                modelsSchema(),
                MODELS_STREAM_NAME + "_2",
                COL_ID,
                COL_MAKE_ID,
                COL_MODEL
            )
        }

        val airbyteStream =
            ConfiguredAirbyteStream()
                .withStream(
                    CatalogHelpers.createAirbyteStream(
                            MODELS_STREAM_NAME + "_2",
                            modelsSchema(),
                            Field.of(COL_ID, JsonSchemaType.INTEGER),
                            Field.of(COL_MAKE_ID, JsonSchemaType.INTEGER),
                            Field.of(COL_MODEL, JsonSchemaType.STRING)
                        )
                        .withSupportedSyncModes(
                            Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL)
                        )
                        .withSourceDefinedPrimaryKey(java.util.List.of(java.util.List.of(COL_ID)))
                )
        airbyteStream.syncMode = SyncMode.FULL_REFRESH

        val streams = configuredCatalog.streams
        streams.add(airbyteStream)
        configuredCatalog.withStreams(streams)

        val read1 = source().read(config()!!, configuredCatalog, null)
        val actualRecords1 = AutoCloseableIterators.toListAndClose(read1)

        val recordMessages1 = extractRecordMessages(actualRecords1)
        val stateMessages1 = extractStateMessages(actualRecords1)
        val names = HashSet(STREAM_NAMES)
        names.add(MODELS_STREAM_NAME + "_2")
        assertExpectedStateMessages(stateMessages1)
        // Full refresh does not get any state messages.
        assertExpectedStateMessageCountMatches(stateMessages1, MODEL_RECORDS_2.size.toLong())
        assertExpectedRecords(
            Streams.concat(MODEL_RECORDS_2.stream(), MODEL_RECORDS.stream())
                .collect(Collectors.toSet()),
            recordMessages1,
            setOf(MODELS_STREAM_NAME),
            names,
            modelsSchema()
        )

        val puntoRecord =
            Jsons.jsonNode(ImmutableMap.of(COL_ID, 100, COL_MAKE_ID, 3, COL_MODEL, "Punto"))
        writeModelRecord(puntoRecord)
        waitForCdcRecords(modelsSchema(), MODELS_STREAM_NAME, 1)

        val state = Jsons.jsonNode(listOf(stateMessages1[stateMessages1.size - 1]))
        val read2 = source().read(config()!!, configuredCatalog, state)
        val actualRecords2 = AutoCloseableIterators.toListAndClose(read2)

        val recordMessages2 = extractRecordMessages(actualRecords2)
        val stateMessages2 = extractStateMessages(actualRecords2)
        assertExpectedStateMessagesFromIncrementalSync(stateMessages2)
        assertExpectedStateMessageCountMatches(stateMessages2, 1)
        assertExpectedRecords(
            Streams.concat(MODEL_RECORDS_2.stream(), Stream.of(puntoRecord))
                .collect(Collectors.toSet()),
            recordMessages2,
            setOf(MODELS_STREAM_NAME),
            names,
            modelsSchema()
        )
    }

    @Test // When no records exist, no records are returned.
    @Throws(Exception::class)
    fun testNoData() {
        deleteCommand(MODELS_STREAM_NAME)
        waitForCdcRecords(modelsSchema(), MODELS_STREAM_NAME, MODEL_RECORDS.size)
        val read = source()!!.read(config()!!, configuredCatalog, null)
        val actualRecords = AutoCloseableIterators.toListAndClose(read)

        val recordMessages = extractRecordMessages(actualRecords)
        val stateMessages = extractStateMessages(actualRecords)
        assertExpectedRecords(emptySet(), recordMessages)
        assertExpectedStateMessagesForNoData(stateMessages)
        assertExpectedStateMessageCountMatches(stateMessages, 0)
    }

    protected open fun assertExpectedStateMessagesForNoData(
        stateMessages: List<AirbyteStateMessage>
    ) {
        assertExpectedStateMessages(stateMessages)
    }

    @Test // When no changes have been made to the database since the previous sync, no records are
    // returned.
    @Throws(Exception::class)
    fun testNoDataOnSecondSync() {
        val read1 = source().read(config()!!, configuredCatalog, null)
        val actualRecords1 = AutoCloseableIterators.toListAndClose(read1)
        val stateMessagesFromFirstSync = extractStateMessages(actualRecords1)
        val state =
            Jsons.jsonNode(listOf(stateMessagesFromFirstSync[stateMessagesFromFirstSync.size - 1]))

        val read2 = source().read(config()!!, configuredCatalog, state)
        val actualRecords2 = AutoCloseableIterators.toListAndClose(read2)

        val recordMessages2 = extractRecordMessages(actualRecords2)
        val stateMessages2 = extractStateMessages(actualRecords2)

        assertExpectedRecords(emptySet(), recordMessages2)
        assertExpectedStateMessagesFromIncrementalSync(stateMessages2)
        assertExpectedStateMessageCountMatches(stateMessages2, 0)
    }

    @Test
    @Throws(Exception::class)
    fun testCheck() {
        val status = source()!!.check(config()!!)
        Assertions.assertEquals(status!!.status, AirbyteConnectionStatus.Status.SUCCEEDED)
    }

    @Test
    @Throws(Exception::class)
    fun testDiscover() {
        val expectedCatalog = expectedCatalogForDiscover()
        val actualCatalog = source()!!.discover(config()!!)

        Assertions.assertEquals(
            expectedCatalog.streams
                .stream()
                .sorted(Comparator.comparing { obj: AirbyteStream -> obj.name })
                .collect(Collectors.toList()),
            actualCatalog!!
                .streams
                .stream()
                .sorted(Comparator.comparing { obj: AirbyteStream -> obj.name })
                .collect(Collectors.toList())
        )
    }

    @Test
    @Throws(Exception::class)
    open fun newTableSnapshotTest() {
        val firstBatchIterator = source().read(config()!!, configuredCatalog, null)
        val dataFromFirstBatch = AutoCloseableIterators.toListAndClose(firstBatchIterator)
        val recordsFromFirstBatch = extractRecordMessages(dataFromFirstBatch)
        val stateAfterFirstBatch = extractStateMessages(dataFromFirstBatch)
        assertExpectedStateMessages(stateAfterFirstBatch)
        assertExpectedStateMessageCountMatches(stateAfterFirstBatch, MODEL_RECORDS.size.toLong())

        val stateMessageEmittedAfterFirstSyncCompletion =
            stateAfterFirstBatch[stateAfterFirstBatch.size - 1]
        Assertions.assertEquals(
            AirbyteStateMessage.AirbyteStateType.GLOBAL,
            stateMessageEmittedAfterFirstSyncCompletion.type
        )
        Assertions.assertNotNull(stateMessageEmittedAfterFirstSyncCompletion.global.sharedState)
        val streamsInStateAfterFirstSyncCompletion =
            stateMessageEmittedAfterFirstSyncCompletion.global.streamStates
                .stream()
                .map { obj: AirbyteStreamState -> obj.streamDescriptor }
                .collect(Collectors.toSet())
        Assertions.assertEquals(1, streamsInStateAfterFirstSyncCompletion.size)
        Assertions.assertTrue(
            streamsInStateAfterFirstSyncCompletion.contains(
                StreamDescriptor().withName(MODELS_STREAM_NAME).withNamespace(modelsSchema())
            )
        )
        Assertions.assertNotNull(stateMessageEmittedAfterFirstSyncCompletion.data)

        Assertions.assertEquals((MODEL_RECORDS.size), recordsFromFirstBatch.size)
        assertExpectedRecords(HashSet(MODEL_RECORDS), recordsFromFirstBatch)

        val state = stateAfterFirstBatch[stateAfterFirstBatch.size - 1].data

        val newTables =
            CatalogHelpers.toDefaultConfiguredCatalog(
                AirbyteCatalog()
                    .withStreams(
                        java.util.List.of(
                            CatalogHelpers.createAirbyteStream(
                                    RANDOM_TABLE_NAME,
                                    randomSchema(),
                                    Field.of(COL_ID + "_random", JsonSchemaType.NUMBER),
                                    Field.of(COL_MAKE_ID + "_random", JsonSchemaType.NUMBER),
                                    Field.of(COL_MODEL + "_random", JsonSchemaType.STRING)
                                )
                                .withSupportedSyncModes(
                                    Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL)
                                )
                                .withSourceDefinedPrimaryKey(
                                    java.util.List.of(java.util.List.of(COL_ID + "_random"))
                                )
                        )
                    )
            )

        newTables.streams.forEach(
            Consumer { s: ConfiguredAirbyteStream -> s.syncMode = SyncMode.INCREMENTAL }
        )
        val combinedStreams: MutableList<ConfiguredAirbyteStream> = ArrayList()
        combinedStreams.addAll(configuredCatalog.streams)
        combinedStreams.addAll(newTables.streams)

        val updatedCatalog = ConfiguredAirbyteCatalog().withStreams(combinedStreams)

        /*
         * Write 20 records to the existing table
         */
        val recordsWritten: MutableSet<JsonNode> = HashSet()
        for (recordsCreated in 0..19) {
            val record =
                Jsons.jsonNode(
                    ImmutableMap.of(
                        COL_ID,
                        100 + recordsCreated,
                        COL_MAKE_ID,
                        1,
                        COL_MODEL,
                        "F-$recordsCreated"
                    )
                )
            recordsWritten.add(record)
            writeModelRecord(record)
        }

        val secondBatchIterator = source().read(config()!!, updatedCatalog, state)
        val dataFromSecondBatch = AutoCloseableIterators.toListAndClose(secondBatchIterator)

        val stateAfterSecondBatch = extractStateMessages(dataFromSecondBatch)
        assertStateMessagesForNewTableSnapshotTest(
            stateAfterSecondBatch,
            stateMessageEmittedAfterFirstSyncCompletion
        )

        val recordsStreamWise = extractRecordMessagesStreamWise(dataFromSecondBatch)
        Assertions.assertTrue(recordsStreamWise.containsKey(MODELS_STREAM_NAME))
        Assertions.assertTrue(recordsStreamWise.containsKey(RANDOM_TABLE_NAME))

        val recordsForModelsStreamFromSecondBatch = recordsStreamWise[MODELS_STREAM_NAME]!!
        val recordsForModelsRandomStreamFromSecondBatch = recordsStreamWise[RANDOM_TABLE_NAME]!!

        Assertions.assertEquals(
            (MODEL_RECORDS_RANDOM.size),
            recordsForModelsRandomStreamFromSecondBatch.size
        )
        Assertions.assertEquals(20, recordsForModelsStreamFromSecondBatch.size)
        assertExpectedRecords(
            HashSet(MODEL_RECORDS_RANDOM),
            recordsForModelsRandomStreamFromSecondBatch,
            recordsForModelsRandomStreamFromSecondBatch
                .stream()
                .map { obj: AirbyteRecordMessage -> obj.stream }
                .collect(Collectors.toSet()),
            Sets.newHashSet(RANDOM_TABLE_NAME),
            randomSchema()
        )
        assertExpectedRecords(recordsWritten, recordsForModelsStreamFromSecondBatch)

        /*
         * Write 20 records to both the tables
         */
        val recordsWrittenInRandomTable: MutableSet<JsonNode> = HashSet()
        recordsWritten.clear()
        for (recordsCreated in 30..49) {
            val record =
                Jsons.jsonNode(
                    ImmutableMap.of(
                        COL_ID,
                        100 + recordsCreated,
                        COL_MAKE_ID,
                        1,
                        COL_MODEL,
                        "F-$recordsCreated"
                    )
                )
            writeModelRecord(record)
            recordsWritten.add(record)

            val record2 =
                Jsons.jsonNode(
                    ImmutableMap.of(
                        COL_ID + "_random",
                        11000 + recordsCreated,
                        COL_MAKE_ID + "_random",
                        1 + recordsCreated,
                        COL_MODEL + "_random",
                        "Fiesta-random$recordsCreated"
                    )
                )
            writeRecords(
                record2,
                randomSchema(),
                RANDOM_TABLE_NAME,
                COL_ID + "_random",
                COL_MAKE_ID + "_random",
                COL_MODEL + "_random"
            )
            recordsWrittenInRandomTable.add(record2)
        }

        val state2 = stateAfterSecondBatch[stateAfterSecondBatch.size - 1].data
        val thirdBatchIterator = source().read(config()!!, updatedCatalog, state2)
        val dataFromThirdBatch = AutoCloseableIterators.toListAndClose(thirdBatchIterator)

        val stateAfterThirdBatch = extractStateMessages(dataFromThirdBatch)
        Assertions.assertTrue(stateAfterThirdBatch.size >= 1)

        val stateMessageEmittedAfterThirdSyncCompletion =
            stateAfterThirdBatch[stateAfterThirdBatch.size - 1]
        Assertions.assertEquals(
            AirbyteStateMessage.AirbyteStateType.GLOBAL,
            stateMessageEmittedAfterThirdSyncCompletion.type
        )
        Assertions.assertNotEquals(
            stateMessageEmittedAfterThirdSyncCompletion.global.sharedState,
            stateAfterSecondBatch[stateAfterSecondBatch.size - 1].global.sharedState
        )
        val streamsInSyncCompletionStateAfterThirdSync =
            stateMessageEmittedAfterThirdSyncCompletion.global.streamStates
                .stream()
                .map { obj: AirbyteStreamState -> obj.streamDescriptor }
                .collect(Collectors.toSet())
        Assertions.assertTrue(
            streamsInSyncCompletionStateAfterThirdSync.contains(
                StreamDescriptor().withName(RANDOM_TABLE_NAME).withNamespace(randomSchema())
            )
        )
        Assertions.assertTrue(
            streamsInSyncCompletionStateAfterThirdSync.contains(
                StreamDescriptor().withName(MODELS_STREAM_NAME).withNamespace(modelsSchema())
            )
        )
        Assertions.assertNotNull(stateMessageEmittedAfterThirdSyncCompletion.data)

        val recordsStreamWiseFromThirdBatch = extractRecordMessagesStreamWise(dataFromThirdBatch)
        Assertions.assertTrue(recordsStreamWiseFromThirdBatch.containsKey(MODELS_STREAM_NAME))
        Assertions.assertTrue(recordsStreamWiseFromThirdBatch.containsKey(RANDOM_TABLE_NAME))

        val recordsForModelsStreamFromThirdBatch =
            recordsStreamWiseFromThirdBatch[MODELS_STREAM_NAME]!!
        val recordsForModelsRandomStreamFromThirdBatch =
            recordsStreamWiseFromThirdBatch[RANDOM_TABLE_NAME]!!

        Assertions.assertEquals(20, recordsForModelsStreamFromThirdBatch.size)
        Assertions.assertEquals(20, recordsForModelsRandomStreamFromThirdBatch.size)
        assertExpectedRecords(recordsWritten, recordsForModelsStreamFromThirdBatch)
        assertExpectedRecords(
            recordsWrittenInRandomTable,
            recordsForModelsRandomStreamFromThirdBatch,
            recordsForModelsRandomStreamFromThirdBatch
                .stream()
                .map { obj: AirbyteRecordMessage -> obj.stream }
                .collect(Collectors.toSet()),
            Sets.newHashSet(RANDOM_TABLE_NAME),
            randomSchema()
        )
    }

    protected open fun assertStateMessagesForNewTableSnapshotTest(
        stateMessages: List<AirbyteStateMessage>,
        stateMessageEmittedAfterFirstSyncCompletion: AirbyteStateMessage
    ) {
        Assertions.assertEquals(2, stateMessages.size)
        val stateMessageEmittedAfterSnapshotCompletionInSecondSync = stateMessages[0]
        Assertions.assertEquals(
            AirbyteStateMessage.AirbyteStateType.GLOBAL,
            stateMessageEmittedAfterSnapshotCompletionInSecondSync.type
        )
        Assertions.assertEquals(
            stateMessageEmittedAfterFirstSyncCompletion.global.sharedState,
            stateMessageEmittedAfterSnapshotCompletionInSecondSync.global.sharedState
        )
        val streamsInSnapshotState =
            stateMessageEmittedAfterSnapshotCompletionInSecondSync.global.streamStates
                .stream()
                .map { obj: AirbyteStreamState -> obj.streamDescriptor }
                .collect(Collectors.toSet())
        Assertions.assertEquals(2, streamsInSnapshotState.size)
        Assertions.assertTrue(
            streamsInSnapshotState.contains(
                StreamDescriptor().withName(RANDOM_TABLE_NAME).withNamespace(randomSchema())
            )
        )
        Assertions.assertTrue(
            streamsInSnapshotState.contains(
                StreamDescriptor().withName(MODELS_STREAM_NAME).withNamespace(modelsSchema())
            )
        )
        Assertions.assertNotNull(stateMessageEmittedAfterSnapshotCompletionInSecondSync.data)

        val stateMessageEmittedAfterSecondSyncCompletion = stateMessages[1]
        Assertions.assertEquals(
            AirbyteStateMessage.AirbyteStateType.GLOBAL,
            stateMessageEmittedAfterSecondSyncCompletion.type
        )
        Assertions.assertNotEquals(
            stateMessageEmittedAfterFirstSyncCompletion.global.sharedState,
            stateMessageEmittedAfterSecondSyncCompletion.global.sharedState
        )
        val streamsInSyncCompletionState =
            stateMessageEmittedAfterSecondSyncCompletion.global.streamStates
                .stream()
                .map { obj: AirbyteStreamState -> obj.streamDescriptor }
                .collect(Collectors.toSet())
        Assertions.assertEquals(2, streamsInSnapshotState.size)
        Assertions.assertTrue(
            streamsInSyncCompletionState.contains(
                StreamDescriptor().withName(RANDOM_TABLE_NAME).withNamespace(randomSchema())
            )
        )
        Assertions.assertTrue(
            streamsInSyncCompletionState.contains(
                StreamDescriptor().withName(MODELS_STREAM_NAME).withNamespace(modelsSchema())
            )
        )
        Assertions.assertNotNull(stateMessageEmittedAfterSecondSyncCompletion.data)
    }

    protected fun expectedCatalogForDiscover(): AirbyteCatalog {
        val expectedCatalog = Jsons.clone(catalog)

        val columns =
            ImmutableMap.of(COL_ID, "INTEGER", COL_MAKE_ID, "INTEGER", COL_MODEL, "VARCHAR(200)")
        testdb!!.with(
            createTableSqlFmt(),
            modelsSchema(),
            MODELS_STREAM_NAME + "_2",
            columnClause(columns, Optional.empty())
        )

        val streams = expectedCatalog.streams
        // stream with PK
        streams[0].sourceDefinedCursor = true
        addCdcMetadataColumns(streams[0])
        addCdcDefaultCursorField(streams[0])

        val streamWithoutPK =
            CatalogHelpers.createAirbyteStream(
                MODELS_STREAM_NAME + "_2",
                modelsSchema(),
                Field.of(COL_ID, JsonSchemaType.INTEGER),
                Field.of(COL_MAKE_ID, JsonSchemaType.INTEGER),
                Field.of(COL_MODEL, JsonSchemaType.STRING)
            )
        streamWithoutPK.sourceDefinedPrimaryKey = emptyList()
        streamWithoutPK.supportedSyncModes = java.util.List.of(SyncMode.FULL_REFRESH)
        addCdcDefaultCursorField(streamWithoutPK)
        addCdcMetadataColumns(streamWithoutPK)

        val randomStream =
            CatalogHelpers.createAirbyteStream(
                    RANDOM_TABLE_NAME,
                    randomSchema(),
                    Field.of(COL_ID + "_random", JsonSchemaType.INTEGER),
                    Field.of(COL_MAKE_ID + "_random", JsonSchemaType.INTEGER),
                    Field.of(COL_MODEL + "_random", JsonSchemaType.STRING)
                )
                .withSourceDefinedCursor(true)
                .withSupportedSyncModes(
                    Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL)
                )
                .withSourceDefinedPrimaryKey(
                    java.util.List.of(java.util.List.of(COL_ID + "_random"))
                )

        addCdcDefaultCursorField(randomStream)
        addCdcMetadataColumns(randomStream)

        streams.add(streamWithoutPK)
        streams.add(randomStream)
        expectedCatalog.withStreams(streams)
        return expectedCatalog
    }

    @Throws(Exception::class)
    protected open fun waitForCdcRecords(
        schemaName: String?,
        tableName: String?,
        recordCount: Int
    ) {}

    companion object {
        private val LOGGER: Logger = LoggerFactory.getLogger(CdcSourceTest::class.java)

        const val MODELS_STREAM_NAME: String = "models"
        @JvmField val STREAM_NAMES: Set<String?> = java.util.Set.of(MODELS_STREAM_NAME)
        protected const val COL_ID: String = "id"
        protected const val COL_MAKE_ID: String = "make_id"
        protected const val COL_MODEL: String = "model"

        @JvmField
        val MODEL_RECORDS: List<JsonNode> =
            ImmutableList.of(
                Jsons.jsonNode(ImmutableMap.of(COL_ID, 11, COL_MAKE_ID, 1, COL_MODEL, "Fiesta")),
                Jsons.jsonNode(ImmutableMap.of(COL_ID, 12, COL_MAKE_ID, 1, COL_MODEL, "Focus")),
                Jsons.jsonNode(ImmutableMap.of(COL_ID, 13, COL_MAKE_ID, 1, COL_MODEL, "Ranger")),
                Jsons.jsonNode(ImmutableMap.of(COL_ID, 14, COL_MAKE_ID, 2, COL_MODEL, "GLA")),
                Jsons.jsonNode(ImmutableMap.of(COL_ID, 15, COL_MAKE_ID, 2, COL_MODEL, "A 220")),
                Jsons.jsonNode(ImmutableMap.of(COL_ID, 16, COL_MAKE_ID, 2, COL_MODEL, "E 350"))
            )

        protected const val RANDOM_TABLE_NAME: String = MODELS_STREAM_NAME + "_random"

        @JvmField
        val MODEL_RECORDS_RANDOM: List<JsonNode> =
            MODEL_RECORDS.stream()
                .map { r: JsonNode ->
                    Jsons.jsonNode(
                        ImmutableMap.of(
                            COL_ID + "_random",
                            r[COL_ID].asInt() * 1000,
                            COL_MAKE_ID + "_random",
                            r[COL_MAKE_ID],
                            COL_MODEL + "_random",
                            r[COL_MODEL].asText() + "-random"
                        )
                    )
                }
                .toList()

        @JvmStatic
        protected fun removeDuplicates(
            messages: Set<AirbyteRecordMessage>
        ): Set<AirbyteRecordMessage> {
            val existingDataRecordsWithoutUpdated: MutableSet<JsonNode> = HashSet()
            val output: MutableSet<AirbyteRecordMessage> = HashSet()

            for (message in messages) {
                val node = message.data.deepCopy<ObjectNode>()
                node.remove("_ab_cdc_updated_at")

                if (existingDataRecordsWithoutUpdated.contains(node)) {
                    LOGGER.info("Removing duplicate node: $node")
                } else {
                    output.add(message)
                    existingDataRecordsWithoutUpdated.add(node)
                }
            }

            return output
        }
    }
}
