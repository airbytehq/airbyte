/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.ClockFactory
import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.command.JdbcSourceConfiguration
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.discover.MetaField
import io.airbyte.cdk.discover.MetaFieldDecorator
import io.airbyte.cdk.jdbc.DefaultJdbcConstants
import io.airbyte.cdk.jdbc.IntFieldType
import io.airbyte.cdk.jdbc.LocalDateFieldType
import io.airbyte.cdk.jdbc.StringFieldType
import io.airbyte.cdk.output.BufferingCatalogValidationFailureHandler
import io.airbyte.cdk.output.BufferingOutputConsumer
import io.airbyte.cdk.output.CatalogValidationFailure
import io.airbyte.cdk.ssh.SshConnectionOptions
import io.airbyte.cdk.ssh.SshTunnelMethodConfiguration
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.models.v0.StreamDescriptor
import java.time.Duration
import java.time.LocalDate
import java.time.OffsetDateTime
import org.junit.jupiter.api.Assertions

object TestFixtures {

    val id = Field("id", IntFieldType)
    val ts = Field("ts", LocalDateFieldType)
    val msg = Field("msg", StringFieldType)

    fun stream(
        withPK: Boolean = true,
        withCursor: Boolean = true,
    ) =
        Stream(
            id = StreamIdentifier.from(StreamDescriptor().withNamespace("test").withName("events")),
            schema = setOf(id, ts, msg),
            configuredSyncMode =
                if (withCursor) ConfiguredSyncMode.INCREMENTAL else ConfiguredSyncMode.FULL_REFRESH,
            configuredPrimaryKey = listOf(id).takeIf { withPK },
            configuredCursor = ts.takeIf { withCursor },
        )

    fun opaqueStateValue(
        pk: Int? = null,
        cursor: LocalDate? = null,
    ): OpaqueStateValue =
        Jsons.readTree(
            listOf(
                    """"primary_key":""" + if (pk == null) "{}" else """{"${id.id}":$pk }""",
                    """"cursors":""" + if (cursor == null) "{}" else """{"${ts.id}":"$cursor"} """,
                )
                .joinToString(",", "{", "}")
        )

    fun record(
        pk: Int? = null,
        cursor: LocalDate? = null,
    ): ObjectNode =
        Jsons.readTree(
            listOfNotNull(
                    """ "${id.id}" : $pk """.takeIf { pk != null },
                    """ "${ts.id}" : "$cursor" """.takeIf { cursor != null },
                )
                .joinToString(",", "{", "}")
        ) as ObjectNode

    fun sharedState(
        global: Boolean = false,
        checkpointTargetInterval: Duration = Duration.ofMinutes(1),
        maxConcurrency: Int = 10,
        maxMemoryBytesForTesting: Long = 1_000_000L,
        constants: DefaultJdbcConstants = DefaultJdbcConstants(),
        maxSnapshotReadTime: Duration? = null,
        vararg mockedQueries: MockedQuery,
    ): DefaultJdbcSharedState {
        val configuration =
            StubbedJdbcSourceConfiguration(
                global,
                checkpointTargetInterval,
                maxConcurrency,
                maxSnapshotReadTime
            )
        return DefaultJdbcSharedState(
            configuration,
            MockSelectQuerier(ArrayDeque(mockedQueries.toList())),
            constants.copy(maxMemoryBytesForTesting = maxMemoryBytesForTesting),
            ConcurrencyResource(configuration),
        )
    }

    fun DefaultJdbcSharedState.factory() =
        DefaultJdbcPartitionFactory(
            this,
            BufferingCatalogValidationFailureHandler(),
            MockSelectQueryGenerator
        )

    fun DefaultJdbcPartitionFactory.assertFailures(vararg failures: CatalogValidationFailure) {
        Assertions.assertIterableEquals(
            failures.toList(),
            (handler as BufferingCatalogValidationFailureHandler).get(),
        )
    }

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
        override val maxSnapshotReadDuration: Duration?,
    ) : JdbcSourceConfiguration {
        override val realHost: String
            get() = TODO("Not yet implemented")
        override val jdbcUrlFmt: String
            get() = TODO("Not yet implemented")
        override val jdbcProperties: Map<String, String>
            get() = TODO("Not yet implemented")
        override val namespaces: Set<String>
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
                override fun next(): SelectQuerier.ResultRow =
                    object : SelectQuerier.ResultRow {
                        override val data: ObjectNode = wrapped.next()
                        override val changes: Map<Field, FieldValueChange> = emptyMap()
                    }
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

    object MockSelectQueryGenerator : SelectQueryGenerator {
        override fun generate(ast: SelectQuerySpec): SelectQuery =
            SelectQuery(ast.toString(), listOf(), listOf())
    }

    object MockMetaFieldDecorator : MetaFieldDecorator {
        override val globalCursor: MetaField? = null
        override val globalMetaFields: Set<MetaField> = emptySet()

        override fun decorateRecordData(
            timestamp: OffsetDateTime,
            globalStateValue: OpaqueStateValue?,
            stream: Stream,
            recordData: ObjectNode
        ) {}
    }

    fun Stream.bootstrap(opaqueStateValue: OpaqueStateValue?): StreamFeedBootstrap =
        StreamFeedBootstrap(
            outputConsumer = BufferingOutputConsumer(ClockFactory().fixed()),
            metaFieldDecorator = MockMetaFieldDecorator,
            stateManager = StateManager(initialStreamStates = mapOf(this to opaqueStateValue)),
            stream = this
        )
}
