/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.typing_deduping.direct_load_tables

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.config.NamespaceDefinitionType
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectTypeWithoutSchema
import io.airbyte.cdk.load.table.ColumnNameMapping
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
}
