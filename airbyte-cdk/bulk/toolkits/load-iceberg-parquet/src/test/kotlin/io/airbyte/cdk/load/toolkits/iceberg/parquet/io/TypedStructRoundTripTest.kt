/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.toolkits.iceberg.parquet.io

import io.airbyte.cdk.load.command.Append
import java.nio.file.Files
import org.apache.hadoop.conf.Configuration
import org.apache.iceberg.FileFormat
import org.apache.iceberg.Schema
import org.apache.iceberg.TableProperties
import org.apache.iceberg.catalog.TableIdentifier
import org.apache.iceberg.data.GenericRecord
import org.apache.iceberg.data.IcebergGenerics
import org.apache.iceberg.data.Record
import org.apache.iceberg.hadoop.HadoopCatalog
import org.apache.iceberg.types.Types
import org.assertj.core.api.Assertions.assertThat
import org.junit.jupiter.api.Test

class TypedStructRoundTripTest {
    @Test
    fun `writes and reads nested structs and list of structs`() {
        val warehouse = Files.createTempDirectory("typed-struct-round-trip")
        try {
            val catalog = HadoopCatalog(Configuration(), warehouse.toString())
            val tableIdentifier = TableIdentifier.of("db", "typed_records")
            val userType =
                Types.StructType.of(
                    Types.NestedField.optional(2, "id", Types.IntegerType.get()),
                    Types.NestedField.optional(3, "login", Types.StringType.get()),
                )
            val labelType =
                Types.StructType.of(
                    Types.NestedField.optional(6, "id", Types.IntegerType.get()),
                    Types.NestedField.optional(7, "name", Types.StringType.get()),
                )
            val schema =
                Schema(
                    listOf(
                        Types.NestedField.optional(1, "user", userType),
                        Types.NestedField.optional(
                            4,
                            "labels",
                            Types.ListType.ofOptional(5, labelType),
                        ),
                    ),
                )
            catalog.createNamespace(tableIdentifier.namespace())
            val table =
                catalog
                    .buildTable(tableIdentifier, schema)
                    .withProperty(
                        TableProperties.DEFAULT_FILE_FORMAT,
                        FileFormat.PARQUET.name.lowercase(),
                    )
                    .create()
            val writerSchema = table.schema()
            val writerUserType = writerSchema.findField("user")!!.type().asStructType()
            val writerLabelType =
                writerSchema
                    .findField("labels")!!
                    .type()
                    .asListType()
                    .elementType()
                    .asStructType()
            val record =
                GenericRecord.create(writerSchema).apply {
                    setField(
                        "user",
                        GenericRecord.create(writerUserType).apply {
                            setField("id", 42)
                            setField("login", "octocat")
                        },
                    )
                    setField(
                        "labels",
                        listOf(
                            GenericRecord.create(writerLabelType).apply {
                                setField("id", 5)
                                setField("name", "bug")
                            },
                        ),
                    )
                }
            val writer =
                IcebergTableWriterFactory()
                    .create(table, "ab-generation-id-0-e", Append, writerSchema)
            writer.write(record)
            val writeResult = writer.complete()
            table.newAppend().apply { writeResult.dataFiles().forEach(::appendFile) }.commit()

            val row = IcebergGenerics.read(table).build().use { it.single() }
            assertThat(row.getField("user")).isInstanceOf(Record::class.java)
            val user = row.getField("user") as Record
            assertThat(user.getField("id")).isEqualTo(42)
            assertThat(user.getField("login")).isEqualTo("octocat")

            @Suppress("UNCHECKED_CAST")
            val labels = row.getField("labels") as List<Record>
            assertThat(labels).hasSize(1)
            assertThat(labels.single().getField("id")).isEqualTo(5)
            assertThat(labels.single().getField("name")).isEqualTo("bug")
        } finally {
            warehouse.toFile().deleteRecursively()
        }
    }
}
