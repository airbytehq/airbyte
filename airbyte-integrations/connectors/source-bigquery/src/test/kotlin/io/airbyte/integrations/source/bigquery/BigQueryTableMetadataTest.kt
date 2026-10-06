/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.bigquery

import com.google.cloud.bigquery.Field
import com.google.cloud.bigquery.PrimaryKey
import com.google.cloud.bigquery.Schema
import com.google.cloud.bigquery.StandardSQLTypeName
import com.google.cloud.bigquery.StandardTableDefinition
import com.google.cloud.bigquery.TableConstraints
import com.google.cloud.bigquery.TableId
import com.google.cloud.bigquery.TableInfo
import com.google.cloud.bigquery.ViewDefinition
import io.airbyte.cdk.discover.EmittedField
import io.airbyte.cdk.jdbc.StringFieldType
import io.airbyte.integrations.source.bigquery.BigQuerySourceMetadataQuerier.TableMetadata
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

/**
 * [TableMetadata] is all that discovery keeps of a `tables.get` response: the mapped columns and
 * the primary key, not the tens of KiB of the full table object.
 */
class BigQueryTableMetadataTest {

    private val tableId = TableId.of("project", "dataset", "table")

    @Test
    fun testColumnsAndPrimaryKeyAreKept() {
        val schema =
            Schema.of(
                Field.newBuilder("id", StandardSQLTypeName.INT64)
                    .setMode(Field.Mode.REQUIRED)
                    .build(),
                Field.newBuilder("name", StandardSQLTypeName.STRING)
                    .setDescription("not part of the catalog")
                    .build(),
                Field.newBuilder("tags", StandardSQLTypeName.STRING)
                    .setMode(Field.Mode.REPEATED)
                    .build(),
                Field.newBuilder(
                        "address",
                        StandardSQLTypeName.STRUCT,
                        Field.of("city", StandardSQLTypeName.STRING),
                    )
                    .build(),
            )
        val table: TableInfo =
            TableInfo.newBuilder(tableId, StandardTableDefinition.of(schema))
                .setDescription("not part of the catalog either")
                .setTableConstraints(
                    TableConstraints.newBuilder()
                        .setPrimaryKey(PrimaryKey.newBuilder().setColumns(listOf("id")).build())
                        .build()
                )
                .build()

        val metadata: TableMetadata = TableMetadata.from(table)

        Assertions.assertEquals(
            listOf(
                EmittedField("id", BigQueryLongFieldType),
                EmittedField("name", StringFieldType),
                EmittedField("tags", BigQueryArrayFieldType(StringFieldType)),
                EmittedField(
                    "address",
                    BigQueryStructFieldType(listOf(EmittedField("city", StringFieldType))),
                ),
            ),
            metadata.fields,
        )
        Assertions.assertEquals(listOf(listOf("id")), metadata.primaryKey)
    }

    @Test
    fun testTableWithoutSchemaOrPrimaryKeyIsEmpty() {
        val view: TableInfo = TableInfo.of(tableId, ViewDefinition.of("SELECT 1"))

        val metadata: TableMetadata = TableMetadata.from(view)

        Assertions.assertEquals(emptyList<EmittedField>(), metadata.fields)
        Assertions.assertEquals(emptyList<List<String>>(), metadata.primaryKey)
    }
}
