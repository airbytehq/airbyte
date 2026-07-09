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
import kotlin.test.assertTrue
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
    fun testUpsertTableUsesNullSafePrimaryKeyMatching() {
        // Regression test for oncall#13078: composite primary keys whose component columns can
        // contain NULLs must still dedupe. The MERGE ON clause must treat two NULL PK-component
        // values as equal, otherwise the row falls through to INSERT and is duplicated on every
        // sync (NULL = NULL is UNKNOWN in SQL three-valued logic).
        val stream =
            DestinationStream(
                "ns",
                "n",
                Dedupe(
                    primaryKey = listOf(listOf("id"), listOf("org_id")),
                    cursor = emptyList(),
                ),
                ObjectType(
                    linkedMapOf(
                        "id" to FieldType(StringType, nullable = false),
                        "org_id" to FieldType(StringType, nullable = true),
                        "value" to FieldType(IntegerType, nullable = true),
                    )
                ),
                generationId = 42,
                minimumGenerationId = 0,
                syncId = 12,
                namespaceMapper = NamespaceMapper(NamespaceDefinitionType.SOURCE),
            )
        val columnNameMapping =
            ColumnNameMapping(
                mapOf(
                    "id" to "id",
                    "org_id" to "org_id",
                    "value" to "value",
                )
            )

        val generator =
            BigqueryDirectLoadSqlGenerator(
                projectId = "project",
                cdcDeletionMode = CdcDeletionMode.HARD_DELETE,
            )
        val sql =
            generator.upsertTable(
                stream,
                columnNameMapping,
                TableName(namespace = "ns", name = "source"),
                TableName(namespace = "ns", name = "target"),
            )

        val rendered = sql.transactions.flatten().joinToString("\n")
        val expectedOnClause =
            """ON (target_table.`id` = new_record.`id` OR (target_table.`id` IS NULL AND new_record.`id` IS NULL)) AND (target_table.`org_id` = new_record.`org_id` OR (target_table.`org_id` IS NULL AND new_record.`org_id` IS NULL))"""
        assertTrue(
            rendered.contains(expectedOnClause),
            "MERGE ON clause must use NULL-safe matching for every composite PK component; got:\n$rendered"
        )
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
