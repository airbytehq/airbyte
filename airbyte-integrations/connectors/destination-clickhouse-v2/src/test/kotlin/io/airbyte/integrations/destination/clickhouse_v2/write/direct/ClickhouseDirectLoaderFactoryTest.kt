/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse_v2.write.direct

import com.clickhouse.client.api.Client
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableExecutionConfig
import io.airbyte.cdk.load.write.StreamStateStore
import io.airbyte.integrations.destination.clickhouse_v2.write.RecordMunger
import io.mockk.every
import io.mockk.impl.annotations.MockK
import io.mockk.junit5.MockKExtension
import kotlin.test.assertEquals
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.extension.ExtendWith
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.Arguments
import org.junit.jupiter.params.provider.MethodSource

@ExtendWith(MockKExtension::class)
class ClickhouseDirectLoaderFactoryTest {
    @MockK(relaxed = true) lateinit var clickhouseClient: Client

    @MockK lateinit var stateStore: StreamStateStore<DirectLoadTableExecutionConfig>

    @MockK lateinit var munger: RecordMunger

    private lateinit var factory: ClickhouseDirectLoaderFactory

    @BeforeEach
    fun setup() {
        factory = ClickhouseDirectLoaderFactory(clickhouseClient, stateStore, munger)
    }

    @ParameterizedTest
    @MethodSource("streamDescriptors")
    fun `creates loader with buffer and correctly mapped table name`(
        stream: DestinationStream.Descriptor,
        table: TableName
    ) {
        every { stateStore.get(stream) } returns DirectLoadTableExecutionConfig(table)

        val result = factory.create(stream, 0) // part isn't used

        assertEquals(table, result.buffer.tableName)
        assertEquals(munger, result.munger)
    }

    companion object {
        // these values wrap a `value` field
        @JvmStatic
        fun streamDescriptors() =
            listOf(
                Arguments.of(Fixtures.desc1, Fixtures.table1),
                Arguments.of(Fixtures.desc2, Fixtures.table2),
                Arguments.of(Fixtures.desc3, Fixtures.table3),
                Arguments.of(Fixtures.desc4, Fixtures.table2),
                Arguments.of(Fixtures.desc5, Fixtures.table1),
                Arguments.of(Fixtures.desc3, Fixtures.table1),
                Arguments.of(Fixtures.desc5, Fixtures.table2),
                Arguments.of(Fixtures.desc2, Fixtures.table3),
            )
    }

    object Fixtures {
        val desc1 = DestinationStream.Descriptor("namespace 1", "name 1")
        val desc2 = DestinationStream.Descriptor(null, "name 2")
        val desc3 = DestinationStream.Descriptor("namespace 3", "name 2")
        val desc4 = DestinationStream.Descriptor("namespace 4", "name 3")
        val desc5 = DestinationStream.Descriptor(null, "name 5")

        val table1 = TableName("munged namespace 1", "munged 1")
        val table2 = TableName("munged namespace 2", "munged 2")
        val table3 = TableName("munged namespace 3", "munged 3")
    }
}
