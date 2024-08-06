/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.read.streams

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.TestClockFactory
import io.airbyte.cdk.consumers.BufferingCatalogValidationFailureHandler
import io.airbyte.cdk.consumers.BufferingOutputConsumer
import io.airbyte.cdk.jdbc.H2TestFixture
import io.airbyte.cdk.jdbc.IntFieldType
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.jdbc.JdbcSelectQuerier
import io.airbyte.cdk.jdbc.StringFieldType
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.read.stream.MemoryFetchSizeEstimator
import io.airbyte.cdk.read.stream.MemoryFetchSizeEstimator.Companion.DEFAULT_FETCH_SIZE
import io.airbyte.cdk.read.stream.Sample
import io.airbyte.cdk.read.stream.Sample.Kind
import io.airbyte.cdk.read.stream.StreamPartitionReader
import io.airbyte.cdk.read.stream.StreamPartitionsCreator
import io.airbyte.cdk.read.stream.StreamPartitionsCreatorUtils
import io.airbyte.cdk.read.stream.StreamReadContextManager
import io.airbyte.cdk.source.Field
import io.airbyte.cdk.source.select.From
import io.airbyte.cdk.source.select.OrderBy
import io.airbyte.cdk.source.select.SelectColumns
import io.airbyte.cdk.source.select.SelectQuerySpec
import io.airbyte.cdk.test.source.FakeSourceConfiguration
import io.airbyte.cdk.test.source.FakeSourceConfigurationFactory
import io.airbyte.cdk.test.source.FakeSourceConfigurationJsonObject
import io.airbyte.cdk.test.source.FakeSourceOperations
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
            primaryKeyCandidates = listOf(listOf(k)),
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
    fun testMemoryFetchSizeEstimator() {
        Assertions.assertEquals(
            14000,
            MemoryFetchSizeEstimator(700_000, 1).apply(Sample(listOf(10, 20, 30), Kind.SMALL, 0L)),
        )
        Assertions.assertEquals(
            7000,
            MemoryFetchSizeEstimator(700_000, 2).apply(Sample(listOf(10, 20, 30), Kind.SMALL, 0L)),
        )
        Assertions.assertEquals(
            DEFAULT_FETCH_SIZE,
            MemoryFetchSizeEstimator(700_000, 2).apply(Sample(listOf(), Kind.MEDIUM, 0L)),
        )
    }

    @Test
    fun testCursorUpperBound() {
        val utils: StreamPartitionsCreatorUtils = createUtils(testParameters)
        utils.computeCursorUpperBound(k)
        Assertions.assertEquals(
            "5",
            utils.ctx.transientCursorUpperBoundState.get()?.toString(),
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
        val ctxManager =
            StreamReadContextManager(
                config,
                BufferingCatalogValidationFailureHandler(),
                FakeSourceOperations(),
                JdbcSelectQuerier(JdbcConnectionFactory(config)),
                BufferingOutputConsumer(TestClockFactory().fixed()),
            )
        val ctx = ctxManager[stream]
        ctx.resetStream()
        return StreamPartitionsCreatorUtils(ctx, params)
    }
}
