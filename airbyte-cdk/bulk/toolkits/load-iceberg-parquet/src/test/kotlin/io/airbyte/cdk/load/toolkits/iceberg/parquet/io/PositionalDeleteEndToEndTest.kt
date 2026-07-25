/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.toolkits.iceberg.parquet.io

import java.nio.file.Files
import org.apache.hadoop.conf.Configuration
import org.apache.iceberg.FileContent
import org.apache.iceberg.FileFormat
import org.apache.iceberg.Schema
import org.apache.iceberg.TableProperties
import org.apache.iceberg.catalog.TableIdentifier
import org.apache.iceberg.data.IcebergGenerics
import org.apache.iceberg.data.GenericRecord
import org.apache.iceberg.hadoop.HadoopCatalog
import org.apache.iceberg.types.Types
import org.assertj.core.api.Assertions.assertThat
import org.junit.jupiter.api.Test

class PositionalDeleteEndToEndTest {
    @Test
    fun `dedupe update and delete produces positional deletes and expected read`() {
        val warehouse = Files.createTempDirectory("positional-delete-e2e")
        val catalog = HadoopCatalog(Configuration(), warehouse.toString())
        val tableId = TableIdentifier.of("db", "records")
        val schema =
            Schema(
                listOf(
                    Types.NestedField.required(1, "id", Types.IntegerType.get()),
                    Types.NestedField.required(2, "name", Types.StringType.get()),
                ),
                setOf(1),
            )
        catalog.createNamespace(tableId.namespace())
        val table =
            catalog
                .buildTable(tableId, schema)
                .withProperty(TableProperties.DEFAULT_FILE_FORMAT, FileFormat.PARQUET.name.lowercase())
                .create()
        val importType =
            io.airbyte.cdk.load.command.Dedupe(
                primaryKey = listOf(listOf("id")),
                cursor = emptyList(),
            )
        val writerFactory = IcebergTableWriterFactory()

        val initialWriter =
            writerFactory.create(
                table,
                "ab-generation-id-0-e",
                importType,
                schema,
            )
        initialWriter.write(record(schema, 1, "one"))
        initialWriter.write(record(schema, 2, "two"))
        val initialResult = initialWriter.complete()
        table
            .newAppend()
            .apply { initialResult.dataFiles().forEach(::appendFile) }
            .commit()

        val index =
            PositionalDeleteIndexBuilder().build(
                table = table,
                ref = "main",
                schema = schema,
                identifierFieldIds = schema.identifierFieldIds(),
            )
        val updateWriter =
            writerFactory.create(
                table,
                "ab-generation-id-1-e",
                importType,
                schema,
                index,
            )
        updateWriter.write(RecordWrapper(record(schema, 1, "one-updated"), Operation.UPDATE))
        updateWriter.write(RecordWrapper(record(schema, 2, "ignored"), Operation.DELETE))
        val updateResult = updateWriter.complete()
        table
            .newRowDelta()
            .apply {
                updateResult.dataFiles().forEach(::addRows)
                updateResult.deleteFiles().forEach(::addDeletes)
            }
            .commit()

        val deleteFiles =
            table.currentSnapshot()!!.addedDeleteFiles(table.io()).toList()
        assertThat(deleteFiles).isNotEmpty
        assertThat(deleteFiles.map { it.content() }.toSet())
            .containsOnly(FileContent.POSITION_DELETES)
        assertThat(deleteFiles).allMatch { it.content() != FileContent.EQUALITY_DELETES }

        val rows =
            IcebergGenerics.read(table).build().use { records ->
                records.map { it.getField("id") to it.getField("name") }.toSet()
            }
        assertThat(rows).containsExactlyInAnyOrder(1 to "one-updated")
    }

    private fun record(schema: Schema, id: Int, name: String): GenericRecord =
        GenericRecord.create(schema).apply {
            setField("id", id)
            setField("name", name)
        }
}
