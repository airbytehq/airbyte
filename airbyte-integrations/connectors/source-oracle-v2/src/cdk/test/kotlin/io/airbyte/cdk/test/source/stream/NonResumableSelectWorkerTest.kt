/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.test.source.stream

import com.fasterxml.jackson.databind.node.JsonNodeFactory
import io.airbyte.cdk.TestClockFactory
import io.airbyte.cdk.consumers.BufferingOutputConsumer
import io.airbyte.cdk.discover.IntFieldType
import io.airbyte.cdk.discover.StringFieldType
import io.airbyte.cdk.discover.TableName
import io.airbyte.cdk.jdbc.H2TestFixture
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.jdbc.JdbcSelectQuerier
import io.airbyte.cdk.read.CdcInitialSyncCompleted
import io.airbyte.cdk.read.CdcNonResumableInitialSyncStarting
import io.airbyte.cdk.read.CursorBasedIncrementalCompleted
import io.airbyte.cdk.read.CursorBasedNonResumableInitialSyncStarting
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.read.FullRefreshCompleted
import io.airbyte.cdk.read.FullRefreshNonResumableStarting
import io.airbyte.cdk.read.NonResumableBackfillState
import io.airbyte.cdk.read.SerializableStreamState
import io.airbyte.cdk.read.StreamKey
import io.airbyte.cdk.read.WorkResult
import io.airbyte.cdk.read.stream.NonResumableSelectWorker
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
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class NonResumableSelectWorkerTest {

    val h2 = H2TestFixture()

    init {
        h2.execute(
            """CREATE TABLE kv (
            |k INT PRIMARY KEY, 
            |v VARCHAR(60))
            |"""
                .trimMargin()
                .replace('\n', ' ')
        )
        h2.execute("INSERT INTO kv (k, v) VALUES (1, 'foo'), (2, 'bar'), (3, NULL);")
    }

    val key =
        StreamKey(
            configuredStream =
                ConfiguredAirbyteStream()
                    .withStream(AirbyteStream().withName("KV").withNamespace("PUBLIC")),
            table = TableName(schema = "PUBLIC", name = "KV", type = ""),
            fields =
                listOf(
                    Field("k", IntFieldType),
                    Field("v", StringFieldType),
                ),
            primaryKeyCandidates = listOf(),
            cursorCandidates = listOf(),
            configuredSyncMode = SyncMode.INCREMENTAL,
            configuredPrimaryKey = null,
            configuredCursor = null
        )

    val cursor = key.fields.first()

    @Test
    fun testFullRefresh() {
        runTest(
            FullRefreshNonResumableStarting(key),
            FullRefreshCompleted(key),
            """{"k":1,"v":"foo"}""",
            """{"k":2,"v":"bar"}""",
            """{"k":3,"v":null}"""
        )
    }

    @Test
    fun testCursorBased() {
        runTest(
            CursorBasedNonResumableInitialSyncStarting(key, cursor, nodeFactory.numberNode(2)),
            CursorBasedIncrementalCompleted(key, cursor, nodeFactory.numberNode(2)),
            """{"k":1,"v":"foo"}""",
            """{"k":2,"v":"bar"}"""
        )
    }

    @Test
    fun testCdc() {
        runTest(
            CdcNonResumableInitialSyncStarting(key),
            CdcInitialSyncCompleted(key),
            """{"k":1,"v":"foo"}""",
            """{"k":2,"v":"bar"}""",
            """{"k":3,"v":null}"""
        )
    }

    private fun runTest(
        input: NonResumableBackfillState,
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
            NonResumableSelectWorker(TestSourceOperations(), querier, outputConsumer, input)
                .call()
        Assertions.assertEquals(expectedOutputState, result.output)
        Assertions.assertEquals(
            expectedRecordValues.toList().map { Jsons.deserialize(it) },
            outputConsumer.records().map { it.data }
        )
    }

    companion object {
        val nodeFactory: JsonNodeFactory = MoreMappers.initMapper().nodeFactory
    }
}
