/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data.iceberg.parquet

import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectTypeWithoutSchema
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringValue
import java.nio.file.Files
import org.apache.iceberg.Files as IcebergFiles
import org.apache.iceberg.data.GenericRecord
import org.apache.iceberg.data.Record
import org.apache.iceberg.data.parquet.GenericParquetReaders
import org.apache.iceberg.data.parquet.GenericParquetWriter
import org.apache.iceberg.parquet.Parquet
import org.apache.iceberg.types.Types
import org.apache.iceberg.variants.Variant
import org.apache.iceberg.variants.VariantObject
import org.apache.iceberg.variants.VariantPrimitive
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

/**
 * Guards the assumption the variant mapping rests on: Iceberg's generic (non-Spark) Parquet writer
 * can round-trip a variant column.
 */
class IcebergVariantRoundTripTest {

    private val converter = AirbyteValueToIcebergRecord()

    @Test
    fun `writes and reads a variant column with the generic parquet writer`() {
        val schema =
            ObjectType(linkedMapOf("payload" to FieldType(ObjectTypeWithoutSchema, true)))
                .toIcebergSchema(primaryKeys = emptyList(), useVariant = true)

        assertEquals(Types.VariantType.get(), schema.findField("payload").type())

        val payload =
            ObjectValue(
                linkedMapOf(
                    "name" to StringValue("airbyte"),
                    "count" to IntegerValue(42),
                ),
            )
        val record = GenericRecord.create(schema)
        record.setField("payload", converter.convert(payload, Types.VariantType.get()))

        val file = Files.createTempDirectory("variant-round-trip").resolve("data.parquet").toFile()
        Parquet.write(IcebergFiles.localOutput(file))
            .schema(schema)
            .createWriterFunc(GenericParquetWriter::create)
            .build<Record>()
            .use { it.add(record) }

        val readBack =
            Parquet.read(IcebergFiles.localInput(file))
                .project(schema)
                .createReaderFunc { fileSchema ->
                    GenericParquetReaders.buildReader(schema, fileSchema)
                }
                .build<Record>()
                .use { it.toList() }

        assertEquals(1, readBack.size)
        val variant = readBack.single().getField("payload") as Variant
        val obj = variant.value() as VariantObject
        assertEquals("airbyte", (obj.get("name") as VariantPrimitive<*>).get())
        assertEquals(42L, (obj.get("count") as VariantPrimitive<*>).get())
    }
}
