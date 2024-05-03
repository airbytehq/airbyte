/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.test.source.stream

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.JsonNodeFactory
import io.airbyte.cdk.TestClockFactory
import io.airbyte.cdk.consumers.BufferingOutputConsumer
import io.airbyte.cdk.discover.ColumnMetadata
import io.airbyte.cdk.discover.LeafAirbyteType
import io.airbyte.cdk.discover.SystemType
import io.airbyte.cdk.discover.TableName
import io.airbyte.cdk.jdbc.H2TestFixture
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.jdbc.JdbcSelectQuerier
import io.airbyte.cdk.read.CdcInitialSyncCompleted
import io.airbyte.cdk.read.CdcResumableInitialSyncOngoing
import io.airbyte.cdk.read.CdcResumableInitialSyncStarting
import io.airbyte.cdk.read.CursorBasedIncrementalCompleted
import io.airbyte.cdk.read.CursorBasedIncrementalOngoing
import io.airbyte.cdk.read.CursorBasedResumableInitialSyncOngoing
import io.airbyte.cdk.read.CursorBasedResumableInitialSyncStarting
import io.airbyte.cdk.read.DataColumn
import io.airbyte.cdk.read.FullRefreshCompleted
import io.airbyte.cdk.read.FullRefreshResumableOngoing
import io.airbyte.cdk.read.FullRefreshResumableStarting
import io.airbyte.cdk.read.LimitState
import io.airbyte.cdk.read.ResumableSelectState
import io.airbyte.cdk.read.SerializableStreamState
import io.airbyte.cdk.read.StreamKey
import io.airbyte.cdk.read.WorkResult
import io.airbyte.cdk.read.stream.ResumableSelectWorker
import io.airbyte.cdk.read.stream.SelectQuerier
import io.airbyte.cdk.test.source.TestSourceConfiguration
import io.airbyte.cdk.test.source.TestSourceConfigurationFactory
import io.airbyte.cdk.test.source.TestSourceConfigurationJsonObject
import io.airbyte.cdk.test.source.TestSourceOperations
import io.airbyte.commons.jackson.MoreMappers
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.airbyte.protocol.models.v0.SyncMode
import java.sql.Types
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class ResumableSelectWorkerTest {

    val h2 = H2TestFixture()

    val idInRow1 = "bb3388f1-2fc9-4d97-b3c2-f1621d4aebd3"
    val tsInRow1 = "2024-04-28T00:00:00.000000-04:00"
    val idInRow2 = "cc449902-30da-5ea8-c4d3-02732e5bfce9"
    val tsInRow2 = "2024-04-29T00:00:00.000000-04:00"
    val idInRow3 = "dd55aa13-41eb-6fb4-d5e4-13843f6c0dfa"
    val tsInRow3 = "2024-04-30T00:00:00.000000-04:00"

    init {
        h2.execute(
            """CREATE TABLE eventlog (
            |id UUID PRIMARY KEY, 
            |ts TIMESTAMP WITH TIME ZONE NOT NULL,
            |msg VARCHAR(60))
            |"""
                .trimMargin()
                .replace('\n', ' ')
        )
        h2.execute(
            "INSERT INTO eventlog (id, ts, msg) VALUES " +
                "('%s', '%s', 'foo')," +
                "('%s', '%s', 'bar')," +
                "('%s', '%s', NULL);",
            idInRow1,
            tsInRow1,
            idInRow2,
            tsInRow2,
            idInRow3,
            tsInRow3
        )
    }

    val key =
        StreamKey(
            configuredStream =
                ConfiguredAirbyteStream()
                    .withStream(AirbyteStream().withName("EVENTLOG").withNamespace("PUBLIC")),
            table = TableName(schema = "PUBLIC", name = "EVENTLOG", type = ""),
            dataColumns =
                listOf(
                    DataColumn(
                        ColumnMetadata(
                            name = "id",
                            label = "id",
                            type = SystemType(typeCode = Types.VARCHAR)
                        ),
                        LeafAirbyteType.STRING
                    ),
                    DataColumn(
                        ColumnMetadata(
                            name = "ts",
                            label = "ts",
                            type = SystemType(typeCode = Types.TIMESTAMP_WITH_TIMEZONE)
                        ),
                        LeafAirbyteType.TIMESTAMP_WITH_TIMEZONE
                    ),
                    DataColumn(
                        ColumnMetadata(
                            name = "msg",
                            label = "msg",
                            type = SystemType(typeCode = Types.VARCHAR)
                        ),
                        LeafAirbyteType.STRING
                    ),
                ),
            primaryKeyCandidates = listOf(),
            cursorCandidates = listOf(),
            configuredSyncMode = SyncMode.INCREMENTAL,
            configuredPrimaryKey = null,
            configuredCursor = null
        )

    val pk =
        listOf(
            DataColumn(
                ColumnMetadata(
                    name = "id",
                    label = "id",
                    type = SystemType(typeCode = Types.VARCHAR)
                ),
                LeafAirbyteType.STRING
            )
        )
    val cursor = key.dataColumns.get(1)
    val expectedRow1 = """{"id":"$idInRow1","ts":"$tsInRow1","msg":"foo"}"""
    val expectedRow2 = """{"id":"$idInRow2","ts":"$tsInRow2","msg":"bar"}"""
    val expectedRow3 = """{"id":"$idInRow3","ts":"$tsInRow3","msg":null}"""

    @Test
    fun testFullRefresh() {
        runTest(
            FullRefreshResumableStarting(key, LimitState.minimum, pk),
            FullRefreshResumableOngoing(key, LimitState.minimum.up(), pk, listOf(json(idInRow1))),
            expectedRow1
        )
        runTest(
            FullRefreshResumableOngoing(key, LimitState.minimum.up(), pk, listOf(json(idInRow1))),
            FullRefreshResumableOngoing(
                key,
                LimitState.minimum.up().up(),
                pk,
                listOf(json(idInRow3))
            ),
            expectedRow2,
            expectedRow3
        )
        runTest(
            FullRefreshResumableOngoing(
                key,
                LimitState.minimum.up().up(),
                pk,
                listOf(json(idInRow3))
            ),
            FullRefreshCompleted(key)
        )
    }

    @Test
    fun testCursorBasedInitialSync() {
        runTest(
            CursorBasedResumableInitialSyncStarting(
                key,
                LimitState.minimum,
                pk,
                cursor,
                json(tsInRow2)
            ),
            CursorBasedResumableInitialSyncOngoing(
                key,
                LimitState.minimum.up(),
                pk,
                listOf(json(idInRow1)),
                cursor,
                json(tsInRow2),
            ),
            expectedRow1
        )
        runTest(
            CursorBasedResumableInitialSyncOngoing(
                key,
                LimitState.minimum.up(),
                pk,
                listOf(json(idInRow1)),
                cursor,
                json(tsInRow2)
            ),
            CursorBasedIncrementalCompleted(key, cursor, json(tsInRow2)),
            expectedRow2
        )
        runTest(
            CursorBasedIncrementalOngoing(
                key,
                LimitState.minimum.up(),
                cursor,
                json(tsInRow2),
                json(tsInRow3)
            ),
            CursorBasedIncrementalCompleted(key, cursor, json(tsInRow3)),
            expectedRow3
        )
    }

    @Test
    fun testCursorBasedIncremental() {
        runTest(
            CursorBasedIncrementalOngoing(
                key,
                LimitState.minimum,
                cursor,
                json(tsInRow1),
                json(tsInRow3)
            ),
            CursorBasedIncrementalOngoing(
                key,
                LimitState.minimum.up(),
                cursor,
                json(tsInRow2),
                json(tsInRow3)
            ),
            expectedRow2
        )
        runTest(
            CursorBasedIncrementalOngoing(
                key,
                LimitState.minimum.up(),
                cursor,
                json(tsInRow2),
                json(tsInRow3)
            ),
            CursorBasedIncrementalCompleted(key, cursor, json(tsInRow3)),
            expectedRow3
        )
    }

    @Test
    fun testCdc() {
        runTest(
            CdcResumableInitialSyncStarting(key, LimitState.minimum, pk),
            CdcResumableInitialSyncOngoing(
                key,
                LimitState.minimum.up(),
                pk,
                listOf(json(idInRow1))
            ),
            expectedRow1
        )
        runTest(
            CdcResumableInitialSyncOngoing(
                key,
                LimitState.minimum.up(),
                pk,
                listOf(json(idInRow1))
            ),
            CdcResumableInitialSyncOngoing(
                key,
                LimitState.minimum.up().up(),
                pk,
                listOf(json(idInRow3))
            ),
            expectedRow2,
            expectedRow3
        )
        runTest(
            CdcResumableInitialSyncOngoing(
                key,
                LimitState.minimum.up().up(),
                pk,
                listOf(json(idInRow3))
            ),
            CdcInitialSyncCompleted(key)
        )
    }

    private fun runTest(
        input: ResumableSelectState,
        expectedOutputState: SerializableStreamState,
        vararg expectedRecordValues: String
    ) {
        val configPojo: TestSourceConfigurationJsonObject =
            TestSourceConfigurationJsonObject().apply {
                port = h2.port
                database = h2.database
            }
        val config: TestSourceConfiguration = TestSourceConfigurationFactory().make(configPojo)
        val querier: SelectQuerier = JdbcSelectQuerier(JdbcConnectionFactory(config))
        val outputConsumer = BufferingOutputConsumer(TestClockFactory().fixed())
        val result: WorkResult<StreamKey, *, *> =
            ResumableSelectWorker(TestSourceOperations(), querier, outputConsumer, input).call()
        Assertions.assertEquals(expectedOutputState, result.output)
        Assertions.assertEquals(
            expectedRecordValues.toList().map { Jsons.deserialize(it) },
            outputConsumer.records().map { it.data }
        )
    }

    companion object {
        val nodeFactory: JsonNodeFactory = MoreMappers.initMapper().nodeFactory

        fun json(str: String): JsonNode = nodeFactory.textNode(str)
    }
}
