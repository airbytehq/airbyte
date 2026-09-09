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
import io.airbyte.cdk.load.orchestration.db.ColumnNameMapping
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.integrations.destination.bigquery.spec.CdcDeletionMode
import io.airbyte.integrations.destination.bigquery.write.typing_deduping.direct_load_tables.BigqueryDirectLoadSqlGenerator
import kotlin.test.assertEquals
import kotlin.test.assertFalse
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
    fun testCopyTableAliasesSourceToAvoidColumnNameCollision() {
        // Regression test for https://github.com/airbytehq/oncall/issues/10671.
        // When a source table name matches one of its column names, BigQuery resolves the
        // unqualified identifier in the SELECT list to the row STRUCT instead of the column.
        // copyTable must alias the source table and qualify every column reference.
        val collidingName = "customer_journey_summary"
        val generator = BigqueryDirectLoadSqlGenerator("proj", CdcDeletionMode.SOFT_DELETE)
        val sql =
            generator.copyTable(
                columnNameMapping =
                    ColumnNameMapping(
                        mapOf(
                            collidingName to collidingName,
                            "order_id" to "order_id",
                        ),
                    ),
                sourceTableName = TableName("ds", collidingName),
                targetTableName = TableName("ds", "${collidingName}_tmp"),
            )
        val stmt = sql.transactions.flatten().joinToString("\n")

        assertTrue(
            stmt.contains("FROM `ds`.`$collidingName` AS src"),
            "Source table must be aliased 'src', got:\n$stmt",
        )
        assertTrue(
            stmt.contains("src.`$collidingName`"),
            "SELECT list must reference src.`$collidingName`, got:\n$stmt",
        )
        assertTrue(
            stmt.contains("src._airbyte_raw_id"),
            "Airbyte meta columns must be qualified with src., got:\n$stmt",
        )
        // The colliding identifier must never appear in the SELECT list without the src. prefix.
        val selectClause = stmt.substringAfter("SELECT").substringBefore("FROM")
        assertFalse(
            Regex("(?<!src\\.)`$collidingName`").containsMatchIn(selectClause),
            "Unqualified reference to `$collidingName` leaked into SELECT list:\n$selectClause",
        )
    }

    @Test
    fun testUpsertTableAliasesSourceToAvoidColumnNameCollision() {
        // Regression test for https://github.com/airbytehq/oncall/issues/10671.
        // The `records` CTE inside upsertTable reads from the source table; every column
        // reference there must be qualified with the source-table alias so an unqualified
        // identifier can never collide with the source table's own name.
        val collidingName = "customer_journey_summary"
        val generator = BigqueryDirectLoadSqlGenerator("proj", CdcDeletionMode.SOFT_DELETE)
        val stream =
            DestinationStream(
                "ds",
                collidingName,
                Dedupe(
                    primaryKey = listOf(listOf("order_id")),
                    cursor = listOf("updated_at"),
                ),
                ObjectType(
                    linkedMapOf(
                        "order_id" to FieldType(IntegerType, nullable = true),
                        "updated_at" to FieldType(IntegerType, nullable = true),
                        collidingName to FieldType(ObjectTypeWithoutSchema, nullable = true),
                    )
                ),
                generationId = 0,
                minimumGenerationId = 0,
                syncId = 0,
                namespaceMapper = NamespaceMapper(NamespaceDefinitionType.SOURCE),
            )
        val columnNameMapping =
            ColumnNameMapping(
                mapOf(
                    "order_id" to "order_id",
                    "updated_at" to "updated_at",
                    collidingName to collidingName,
                ),
            )

        val sql =
            generator.upsertTable(
                stream = stream,
                columnNameMapping = columnNameMapping,
                sourceTableName = TableName("ds", collidingName),
                targetTableName = TableName("ds", "${collidingName}_final"),
            )
        val stmt = sql.transactions.flatten().joinToString("\n")

        // The records CTE aliases the source and qualifies all column refs.
        assertTrue(
            stmt.contains("AS src"),
            "Source table in records CTE must be aliased 'src', got:\n$stmt",
        )
        assertTrue(
            stmt.contains("src.`$collidingName`"),
            "records CTE must reference src.`$collidingName`, got:\n$stmt",
        )
        assertTrue(
            stmt.contains("src._airbyte_meta") && stmt.contains("src._airbyte_raw_id"),
            "records CTE must qualify airbyte meta columns with src., got:\n$stmt",
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
