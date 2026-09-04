/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.typing_deduping.direct_load_tables

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.config.NamespaceDefinitionType
import io.airbyte.cdk.load.data.DateType
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectTypeWithoutSchema
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.TimestampTypeWithTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithoutTimezone
import io.airbyte.cdk.load.orchestration.db.ColumnNameMapping
import io.airbyte.integrations.destination.bigquery.spec.PartitioningGranularity
import io.airbyte.integrations.destination.bigquery.write.typing_deduping.direct_load_tables.BigqueryDirectLoadSqlGenerator
import kotlin.test.assertEquals
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows

class BigqueryDirectLoadSqlGeneratorTest {
    @Test
    fun testClusteringColumnsAppend() {
        val clusteringColumns =
            BigqueryDirectLoadSqlGenerator.clusteringColumns(
                DestinationStream(
                    "unused",
                    "unused",
                    Append,
                    ObjectType(
                        linkedMapOf(
                            "foo" to FieldType(IntegerType, nullable = true),
                            "bar" to FieldType(IntegerType, nullable = true),
                        )
                    ),
                    generationId = 42,
                    minimumGenerationId = 0,
                    syncId = 12,
                    namespaceMapper = NamespaceMapper(NamespaceDefinitionType.SOURCE),
                ),
                ColumnNameMapping(
                    mapOf(
                        "foo" to "mapped_foo",
                        "bar" to "mapped_bar",
                    )
                )
            )
        assertEquals(listOf("_airbyte_extracted_at"), clusteringColumns)
    }

    @Test
    fun testClusteringColumnsDedup() {
        val clusteringColumns =
            BigqueryDirectLoadSqlGenerator.clusteringColumns(
                DestinationStream(
                    "unused",
                    "unused",
                    Dedupe(
                        primaryKey = listOf(listOf("foo")),
                        cursor = listOf("bar"),
                    ),
                    ObjectType(
                        linkedMapOf(
                            "foo" to FieldType(IntegerType, nullable = true),
                            "bar" to FieldType(IntegerType, nullable = true),
                        )
                    ),
                    generationId = 42,
                    minimumGenerationId = 0,
                    syncId = 12,
                    namespaceMapper = NamespaceMapper(NamespaceDefinitionType.SOURCE),
                ),
                ColumnNameMapping(
                    mapOf(
                        "foo" to "mapped_foo",
                        "bar" to "mapped_bar",
                    )
                )
            )
        assertEquals(listOf("mapped_foo", "_airbyte_extracted_at"), clusteringColumns)
    }

    @Test
    fun testClusteringColumnsFailOnJsonType() {
        val e =
            assertThrows<ConfigErrorException> {
                BigqueryDirectLoadSqlGenerator.clusteringColumns(
                    DestinationStream(
                        "ns",
                        "n",
                        Dedupe(
                            primaryKey = listOf(listOf("foo")),
                            cursor = listOf("bar"),
                        ),
                        ObjectType(
                            linkedMapOf(
                                "foo" to FieldType(ObjectTypeWithoutSchema, nullable = true),
                                "bar" to FieldType(ObjectTypeWithoutSchema, nullable = true),
                            )
                        ),
                        generationId = 42,
                        minimumGenerationId = 0,
                        syncId = 12,
                        namespaceMapper = NamespaceMapper(NamespaceDefinitionType.SOURCE),
                    ),
                    ColumnNameMapping(
                        mapOf(
                            "foo" to "mapped_foo",
                            "bar" to "mapped_bar",
                        )
                    )
                )
            }
        // note: we used unmapped column names in the exception message
        assertEquals(
            "Stream ns.n: Primary key contains non-clusterable JSON-typed column [foo]",
            e.message
        )
    }

    @Test
    fun testConfiguredClusteringColumnsPreserveOrderAndMappedNames() {
        val stream =
            streamWithSchema(
                "customer_id" to IntegerType,
                "status" to StringType,
            )
        val clusteringColumns =
            BigqueryDirectLoadSqlGenerator.clusteringColumns(
                stream,
                ColumnNameMapping(
                    mapOf(
                        "customer_id" to "customer_id_mapped",
                        "status" to "status_mapped",
                    )
                ),
                configuredFields = listOf("status", "customer_id"),
            )

        assertEquals(listOf("status_mapped", "customer_id_mapped"), clusteringColumns)
    }

    @Test
    fun testConfiguredClusteringRejectsMissingField() {
        val stream = streamWithSchema("customer_id" to IntegerType)

        assertThrows<ConfigErrorException> {
            BigqueryDirectLoadSqlGenerator.clusteringColumns(
                stream,
                ColumnNameMapping(mapOf("customer_id" to "customer_id")),
                configuredFields = listOf("missing"),
            )
        }
    }

    @Test
    fun testPartitioningExpressionsForSupportedTemporalTypes() {
        val datePartition =
            BigqueryDirectLoadSqlGenerator.resolvePartitioning(
                streamWithSchema("event_date" to DateType),
                ColumnNameMapping(mapOf("event_date" to "mapped_event_date")),
                requestedField = "event_date",
                granularity = PartitioningGranularity.MONTH,
            )
        assertEquals("mapped_event_date", datePartition.field)
        assertEquals(
            "DATE_TRUNC(`mapped_event_date`, MONTH)",
            datePartition.expression,
        )

        val timestampPartition =
            BigqueryDirectLoadSqlGenerator.resolvePartitioning(
                streamWithSchema("created_at" to TimestampTypeWithTimezone),
                ColumnNameMapping(mapOf("created_at" to "created_at")),
                requestedField = "created_at",
                granularity = PartitioningGranularity.HOUR,
            )
        assertEquals(
            "TIMESTAMP_TRUNC(`created_at`, HOUR)",
            timestampPartition.expression,
        )

        val datetimePartition =
            BigqueryDirectLoadSqlGenerator.resolvePartitioning(
                streamWithSchema("local_time" to TimestampTypeWithoutTimezone),
                ColumnNameMapping(mapOf("local_time" to "local_time")),
                requestedField = "local_time",
                granularity = PartitioningGranularity.YEAR,
            )
        assertEquals(
            "DATETIME_TRUNC(`local_time`, YEAR)",
            datetimePartition.expression,
        )
    }

    @Test
    fun testHourlyPartitioningRejectsDateField() {
        assertThrows<ConfigErrorException> {
            BigqueryDirectLoadSqlGenerator.resolvePartitioning(
                streamWithSchema("event_date" to DateType),
                ColumnNameMapping(mapOf("event_date" to "event_date")),
                requestedField = "event_date",
                granularity = PartitioningGranularity.HOUR,
            )
        }
    }

    private fun streamWithSchema(
        vararg fields: Pair<String, io.airbyte.cdk.load.data.AirbyteType>
    ): DestinationStream =
        DestinationStream(
            "ns",
            "stream",
            importType = Append,
            schema =
                ObjectType(
                    linkedMapOf(
                        *fields
                            .map { (name, type) -> name to FieldType(type, nullable = true) }
                            .toTypedArray()
                    )
                ),
            generationId = 42,
            minimumGenerationId = 0,
            syncId = 12,
            namespaceMapper = NamespaceMapper(NamespaceDefinitionType.SOURCE),
        )
}
