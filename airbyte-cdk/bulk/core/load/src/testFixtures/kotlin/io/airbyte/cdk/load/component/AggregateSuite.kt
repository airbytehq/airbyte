/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.component

import io.airbyte.cdk.load.component.TableOperationsFixtures.createAppendStream
import io.airbyte.cdk.load.component.TableOperationsFixtures.reverseColumnNameMapping
import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.TimestampWithTimezoneValue
import io.airbyte.cdk.load.dataflow.aggregate.AggregateFactory
import io.airbyte.cdk.load.dataflow.state.PartitionKey
import io.airbyte.cdk.load.dataflow.transform.RecordDTO
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_EXTRACTED_AT
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_GENERATION_ID
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_META
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_RAW_ID
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.cdk.load.write.StreamStateStore
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import kotlin.test.assertEquals
import kotlinx.coroutines.test.runTest

@MicronautTest(environments = ["component"])
interface AggregateSuite {
    val airbyteMetaColumnMapping: Map<String, String>
        get() = Meta.COLUMN_NAMES.associateWith { it }
    val columnNameMapping: ColumnNameMapping
        get() = ColumnNameMapping(mapOf("test" to "test"))

    val opsClient: TableOperationsClient
    val testClient: TestTableOperationsClient

    val aggregateFactory: AggregateFactory
    val streamStateStore: StreamStateStore<DirectLoadTableExecutionConfig>
    fun testAggregate(columnNameMapping: ColumnNameMapping) = runTest {
        val testNamespace = TableOperationsFixtures.generateTestNamespace("test")
        val tableName =
            TableOperationsFixtures.generateTestTableName("table-test-table", testNamespace)
        val schema = ObjectType(linkedMapOf("test" to FieldType(IntegerType, nullable = true)))
        val stream =
            createAppendStream(
                tableName.namespace,
                tableName.name,
                schema,
            )
        streamStateStore.put(stream.mappedDescriptor, DirectLoadTableExecutionConfig(tableName))
        opsClient.createNamespace(testNamespace)
        opsClient.createTable(stream, tableName, columnNameMapping, replace = false)

        val aggregate = aggregateFactory.create(stream.mappedDescriptor)
        aggregate.accept(
            RecordDTO(
                mapOf(
                    COLUMN_NAME_AB_RAW_ID to StringValue("b7feae2b-6137-4ec5-8f07-fb33dc9175cc"),
                    COLUMN_NAME_AB_EXTRACTED_AT to
                        TimestampWithTimezoneValue("1970-01-01T00:00:42Z"),
                    COLUMN_NAME_AB_META to
                        ObjectValue(linkedMapOf("changes" to ArrayValue(emptyList()))),
                    COLUMN_NAME_AB_GENERATION_ID to IntegerValue(1),
                    columnNameMapping["test"]!! to IntegerValue(42),
                ),
                PartitionKey("test-partition"),
                sizeBytes = 0,
                emittedAtMs = 42,
            )
        )
        aggregate.flush()

        val actualRecords =
            testClient
                .readTable(tableName)
                .reverseColumnNameMapping(columnNameMapping, airbyteMetaColumnMapping)
        assertEquals(
            listOf(
                mapOf(
                    COLUMN_NAME_AB_RAW_ID to "b7feae2b-6137-4ec5-8f07-fb33dc9175cc",
                    COLUMN_NAME_AB_EXTRACTED_AT to "1970-01-01T00:00:42Z",
                    COLUMN_NAME_AB_META to linkedMapOf("changes" to emptyList<Any?>()),
                    COLUMN_NAME_AB_GENERATION_ID to 1,
                    columnNameMapping["test"]!! to 42,
                )
            ),
            actualRecords,
        )
    }
}
