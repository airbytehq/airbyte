/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.TestClockFactory
import io.airbyte.cdk.command.JdbcSourceConfiguration
import io.airbyte.cdk.output.BufferingOutputConsumer
import io.airbyte.cdk.ssh.SshConnectionOptions
import io.airbyte.cdk.ssh.SshTunnelMethodConfiguration
import io.airbyte.cdk.util.Jsons
import java.time.Duration
import org.junit.jupiter.api.Assertions

object TestFixtures {

    fun sharedState(
        global: Boolean = false,
        checkpointTargetInterval: Duration = Duration.ofMinutes(1),
        maxConcurrency: Int = 10,
        withSampling: Boolean = false,
        maxSampleSize: Int = DefaultJdbcSharedState.TABLE_SAMPLE_SIZE,
        expectedThroughputBytesPerSecond: Long = DefaultJdbcSharedState.THROUGHPUT_BYTES_PER_SECOND,
        minFetchSize: Int = DefaultJdbcSharedState.FETCH_SIZE_LOWER_BOUND,
        defaultFetchSize: Int = DefaultJdbcSharedState.DEFAULT_FETCH_SIZE,
        maxFetchSize: Int = DefaultJdbcSharedState.FETCH_SIZE_UPPER_BOUND,
        memoryCapacityRatio: Double = DefaultJdbcSharedState.MEM_CAPACITY_RATIO,
        estimatedRecordOverheadBytes: Long = DefaultJdbcSharedState.RECORD_OVERHEAD_BYTES,
        estimatedFieldOverheadBytes: Long = DefaultJdbcSharedState.FIELD_OVERHEAD_BYTES,
        maxMemoryBytesForTesting: Long = 1_000_000,
        vararg mockedQueries: MockedQuery,
    ) =
        DefaultJdbcSharedState(
            StubbedJdbcSourceConfiguration(global, checkpointTargetInterval, maxConcurrency),
            BufferingOutputConsumer(TestClockFactory().fixed()),
            MockSelectQuerier(ArrayDeque(mockedQueries.toList())),
            withSampling,
            maxSampleSize,
            expectedThroughputBytesPerSecond,
            minFetchSize,
            defaultFetchSize,
            maxFetchSize,
            memoryCapacityRatio,
            estimatedRecordOverheadBytes,
            estimatedFieldOverheadBytes,
            maxMemoryBytesForTesting,
        )

    fun SelectQuery.assertQueryEquals(expected: SelectQuerySpec) {
        Assertions.assertEquals(expected.toString(), this.sql)
    }

    fun JsonNode.assertJsonEquals(expected: String) {
        Assertions.assertEquals(expected, this.toString())
    }

    fun JsonNode.assertJsonEquals(expected: JsonNode) {
        Assertions.assertEquals(expected.toString(), this.toString())
    }

    class StubbedJdbcSourceConfiguration(
        override val global: Boolean,
        override val checkpointTargetInterval: Duration,
        override val maxConcurrency: Int,
    ) : JdbcSourceConfiguration {
        override val realHost: String
            get() = TODO("Not yet implemented")
        override val jdbcUrlFmt: String
            get() = TODO("Not yet implemented")
        override val jdbcProperties: Map<String, String>
            get() = TODO("Not yet implemented")
        override val schemas: Set<String>
            get() = TODO("Not yet implemented")
        override val realPort: Int
            get() = TODO("Not yet implemented")
        override val sshTunnel: SshTunnelMethodConfiguration
            get() = TODO("Not yet implemented")
        override val sshConnectionOptions: SshConnectionOptions
            get() = TODO("Not yet implemented")
        override val resourceAcquisitionHeartbeat: Duration
            get() = TODO("Not yet implemented")
    }

    class MockSelectQuerier(val mockedQueries: ArrayDeque<MockedQuery>) : SelectQuerier {

        override fun executeQuery(
            q: SelectQuery,
            parameters: SelectQuerier.Parameters
        ): SelectQuerier.Result {
            val mockedQuery: MockedQuery? = mockedQueries.removeFirstOrNull()
            Assertions.assertNotNull(mockedQuery, q.sql)
            Assertions.assertEquals(q.sql, mockedQuery!!.expectedQuerySpec.toString())
            Assertions.assertEquals(parameters, mockedQuery.expectedParameters, q.sql)
            return object : SelectQuerier.Result {
                val wrapped: Iterator<ObjectNode> = mockedQuery.results.iterator()
                override fun hasNext(): Boolean = wrapped.hasNext()
                override fun next(): ObjectNode = wrapped.next()
                override fun close() {}
            }
        }
    }

    data class MockedQuery(
        val expectedQuerySpec: SelectQuerySpec,
        val expectedParameters: SelectQuerier.Parameters,
        val results: List<ObjectNode>
    ) {
        constructor(
            expectedQuerySpec: SelectQuerySpec,
            expectedParameters: SelectQuerier.Parameters,
            vararg rows: String,
        ) : this(
            expectedQuerySpec,
            expectedParameters,
            rows.map { Jsons.readTree(it) as ObjectNode },
        )
    }
}
