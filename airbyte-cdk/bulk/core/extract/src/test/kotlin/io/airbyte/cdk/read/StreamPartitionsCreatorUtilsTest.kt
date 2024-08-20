/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.read

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.TestClockFactory
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.fakesource.FakeSourceConfiguration
import io.airbyte.cdk.fakesource.FakeSourceConfigurationFactory
import io.airbyte.cdk.fakesource.FakeSourceConfigurationJsonObject
import io.airbyte.cdk.fakesource.FakeSourceOperations
import io.airbyte.cdk.h2.H2TestFixture
import io.airbyte.cdk.jdbc.IntFieldType
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.jdbc.StringFieldType
import io.airbyte.cdk.output.BufferingCatalogValidationFailureHandler
import io.airbyte.cdk.output.BufferingOutputConsumer
import io.airbyte.cdk.read.Sample.Kind
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.models.v0.SyncMode
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class StreamPartitionsCreatorUtilsTest {
    val h2 = H2TestFixture()

    init {
        h2.execute(
            """CREATE TABLE kv (
            |k INT PRIMARY KEY,
            |v VARCHAR(60))
            |
            """
                .trimMargin()
                .replace('\n', ' '),
        )
        h2.execute(
            "INSERT INTO kv (k, v) " +
                "VALUES (1, 'foo'), (2, 'bar'), (3, NULL), (4, 'baz'), (5, 'quux');",
        )
    }

    val k = Field("k", IntFieldType)
    val v = Field("v", StringFieldType)

    val stream =
        Stream(
            name = "kv",
            namespace = "public",
            fields = listOf(k, v),
            configuredSyncMode = SyncMode.FULL_REFRESH,
            configuredPrimaryKey = listOf(k),
            configuredCursor = null,
        )

    val querySpec =
        SelectQuerySpec(
            SelectColumns(listOf(k)),
            From("kv", "public"),
            orderBy = OrderBy(listOf(k)),
        )

    val testParameters =
        StreamPartitionsCreator.Parameters(
            preferParallelized = true,
            tableSampleSize = 2,
            throughputBytesPerSecond = 10L,
        )

    @Test
    fun testCollectSample() {
        val utils: StreamPartitionsCreatorUtils = createUtils(testParameters)
        val sample = utils.collectSample(querySpec) {}
        Assertions.assertEquals(Kind.SMALL, sample.kind)
    }

    @Test
    fun testCollectTinySample() {
        val utils: StreamPartitionsCreatorUtils =
            createUtils(testParameters.copy(tableSampleSize = 100))
        val sample = utils.collectSample(querySpec) {}
        Assertions.assertEquals(Kind.TINY, sample.kind)
    }

    @Test
    fun testCollectEmptySample() {
        h2.execute("TRUNCATE TABLE kv")
        val utils: StreamPartitionsCreatorUtils = createUtils(testParameters)
        val sample = utils.collectSample(querySpec) {}
        Assertions.assertEquals(Kind.EMPTY, sample.kind)
    }

    @Test
    fun testCollectSampleInLargeTable() {
        h2.execute("INSERT INTO kv(k, v) SELECT X, NULL FROM SYSTEM_RANGE(6, 100000)")
        val utils: StreamPartitionsCreatorUtils =
            createUtils(testParameters.copy(tableSampleSize = 100))
        val sample = utils.collectSample(querySpec) {}
        Assertions.assertEquals(Kind.SMALL, sample.kind)
    }

    @Test
    fun testCursorUpperBound() {
        val utils: StreamPartitionsCreatorUtils = createUtils(testParameters)
        utils.computeCursorUpperBound(k)
        Assertions.assertEquals(
            "5",
            utils.ctx.streamState.cursorUpperBound?.toString(),
        )
    }

    @Test
    fun testSplitPrimaryKey() {
        val utils: StreamPartitionsCreatorUtils = createUtils(testParameters)
        val input =
            StreamPartitionReader.SnapshotInput(
                primaryKey = listOf(k),
                primaryKeyLowerBound = null,
                primaryKeyUpperBound = null,
            )
        val splits: List<Pair<List<JsonNode>?, List<JsonNode>?>> =
            utils.split(input, input.primaryKeyLowerBound, input.primaryKeyUpperBound)
        val actual: String = splits.joinToString { (l, r) -> "]${l?.first()}, ${r?.first()}]" }
        Assertions.assertEquals("]null, 1], ]1, 2], ]2, null]", actual)
    }

    @Test
    fun testSplitCursor() {
        val utils: StreamPartitionsCreatorUtils = createUtils(testParameters)
        val input =
            StreamPartitionReader.CursorIncrementalInput(
                cursor = k,
                cursorLowerBound = Jsons.numberNode(1),
                isLowerBoundIncluded = false,
                cursorUpperBound = Jsons.numberNode(4),
            )
        val splits: List<Pair<List<JsonNode>?, List<JsonNode>?>> =
            utils.split(input, listOf(input.cursorLowerBound), listOf(input.cursorUpperBound))
        val actual: String = splits.joinToString { (l, r) -> "]${l?.first()}, ${r?.first()}]" }
        Assertions.assertEquals("]1, 2], ]2, 4]", actual)
    }

    private fun createUtils(
        params: StreamPartitionsCreator.Parameters,
    ): StreamPartitionsCreatorUtils {
        val configPojo: FakeSourceConfigurationJsonObject =
            FakeSourceConfigurationJsonObject().apply {
                port = h2.port
                database = h2.database
                timeout = "PT1S"
            }
        val config: FakeSourceConfiguration = FakeSourceConfigurationFactory().make(configPojo)
        val sharedState =
            DefaultJdbcSharedState(
                config,
                BufferingOutputConsumer(TestClockFactory().fixed()),
                JdbcSelectQuerier(JdbcConnectionFactory(config)),
                withSampling = true,
                maxSampleSize = 1024,
                expectedThroughputBytesPerSecond = 10 * 1024 * 1024,
                minFetchSize = 10,
                defaultFetchSize = 1_000,
                maxFetchSize = 10_000_000,
                memoryCapacityRatio = 0.6,
                estimatedRecordOverheadBytes = 16,
                estimatedFieldOverheadBytes = 16,
            )
        val ctxManager =
            StreamReadContextManager(
                sharedState,
                BufferingCatalogValidationFailureHandler(),
                FakeSourceOperations(),
            )
        val ctx = ctxManager[stream]
        ctx.resetStream()
        return StreamPartitionsCreatorUtils(ctx, params)
    }
}
