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
import io.airbyte.cdk.load.data.ArrayType
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectTypeWithoutSchema
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.orchestration.db.ColumnNameMapping
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.integrations.destination.bigquery.spec.CdcDeletionMode
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
            "Stream ns.n: Primary key contains JSON-typed column [foo] (arrays, objects, and unions are stored as JSON in BigQuery, which cannot be used for deduplication). Remove this field from the primary key, or use a non-deduplicating sync mode.",
            e.message
        )
    }

    @Test
    fun testClusteringColumnsFailOnJsonTypeBeyondClusteringLimit() {
        val e =
            assertThrows<ConfigErrorException> {
                BigqueryDirectLoadSqlGenerator.clusteringColumns(
                    DestinationStream(
                        "ns",
                        "sitemaps",
                        Dedupe(
                            primaryKey =
                                listOf(listOf("a"), listOf("b"), listOf("c"), listOf("contents")),
                            cursor = emptyList(),
                        ),
                        ObjectType(
                            linkedMapOf(
                                "a" to FieldType(IntegerType, nullable = true),
                                "b" to FieldType(IntegerType, nullable = true),
                                "c" to FieldType(IntegerType, nullable = true),
                                "contents" to
                                    FieldType(
                                        ArrayType(FieldType(StringType, nullable = true)),
                                        nullable = true
                                    ),
                            )
                        ),
                        generationId = 42,
                        minimumGenerationId = 0,
                        syncId = 12,
                        namespaceMapper = NamespaceMapper(NamespaceDefinitionType.SOURCE),
                    ),
                    ColumnNameMapping(
                        mapOf(
                            "a" to "mapped_a",
                            "b" to "mapped_b",
                            "c" to "mapped_c",
                            "contents" to "mapped_contents",
                        )
                    )
                )
            }
        assertEquals(
            "Stream ns.sitemaps: Primary key contains JSON-typed column [contents] (arrays, objects, and unions are stored as JSON in BigQuery, which cannot be used for deduplication). Remove this field from the primary key, or use a non-deduplicating sync mode.",
            e.message
        )
    }

    @Test
    fun testClusteringColumnsDedupLimitsToThreePkColumns() {
        val clusteringColumns =
            BigqueryDirectLoadSqlGenerator.clusteringColumns(
                DestinationStream(
                    "ns",
                    "sitemaps",
                    Dedupe(
                        primaryKey = listOf(listOf("a"), listOf("b"), listOf("c"), listOf("d")),
                        cursor = emptyList(),
                    ),
                    ObjectType(
                        linkedMapOf(
                            "a" to FieldType(IntegerType, nullable = true),
                            "b" to FieldType(IntegerType, nullable = true),
                            "c" to FieldType(IntegerType, nullable = true),
                            "d" to FieldType(IntegerType, nullable = true),
                        )
                    ),
                    generationId = 42,
                    minimumGenerationId = 0,
                    syncId = 12,
                    namespaceMapper = NamespaceMapper(NamespaceDefinitionType.SOURCE),
                ),
                ColumnNameMapping(
                    mapOf(
                        "a" to "mapped_a",
                        "b" to "mapped_b",
                        "c" to "mapped_c",
                        "d" to "mapped_d",
                    )
                )
            )
        assertEquals(
            listOf("mapped_a", "mapped_b", "mapped_c", "_airbyte_extracted_at"),
            clusteringColumns
        )
    }

    @Test
    fun testCreateTableFailsOnJsonPkBeyondClusteringLimit() {
        val generator = BigqueryDirectLoadSqlGenerator("proj", CdcDeletionMode.HARD_DELETE)
        val stream =
            DestinationStream(
                "ns",
                "sitemaps",
                Dedupe(
                    primaryKey = listOf(listOf("a"), listOf("b"), listOf("c"), listOf("contents")),
                    cursor = emptyList(),
                ),
                ObjectType(
                    linkedMapOf(
                        "a" to FieldType(IntegerType, nullable = true),
                        "b" to FieldType(IntegerType, nullable = true),
                        "c" to FieldType(IntegerType, nullable = true),
                        "contents" to
                            FieldType(
                                ArrayType(FieldType(StringType, nullable = true)),
                                nullable = true
                            ),
                    )
                ),
                generationId = 42,
                minimumGenerationId = 0,
                syncId = 12,
                namespaceMapper = NamespaceMapper(NamespaceDefinitionType.SOURCE),
            )
        assertThrows<ConfigErrorException> {
            generator.createTable(
                stream,
                TableName("ns", "sitemaps"),
                ColumnNameMapping(
                    mapOf(
                        "a" to "mapped_a",
                        "b" to "mapped_b",
                        "c" to "mapped_c",
                        "contents" to "mapped_contents",
                    )
                ),
                replace = false,
            )
        }
    }
}
