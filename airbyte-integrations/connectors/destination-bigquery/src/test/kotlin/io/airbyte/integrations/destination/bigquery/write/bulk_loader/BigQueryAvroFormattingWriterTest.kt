/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.write.bulk_loader

import com.google.cloud.bigquery.Field
import com.google.cloud.bigquery.StandardSQLTypeName
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.config.DataChannelFormat
import io.airbyte.cdk.load.file.object_storage.ObjectStorageFormattingWriter
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.util.Jsons
import io.airbyte.integrations.destination.bigquery.BigQueryConsts
import io.airbyte.integrations.destination.bigquery.formatter.BigQueryRecordFormatter
import java.io.ByteArrayInputStream
import java.io.ByteArrayOutputStream
import java.math.BigDecimal
import java.math.BigInteger
import java.nio.ByteBuffer
import java.time.Instant
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.OffsetDateTime
import java.time.ZoneOffset
import java.time.temporal.ChronoUnit
import org.apache.avro.LogicalTypes
import org.apache.avro.Schema
import org.apache.avro.file.DataFileStream
import org.apache.avro.generic.GenericDatumReader
import org.apache.avro.generic.GenericRecord
import org.apache.commons.csv.CSVFormat
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.EnumSource

/**
 * The Avro staging file of every Airbyte type holds what the CSV staging file holds, in the Avro
 * types BigQuery reads as the columns' types.
 */
class BigQueryAvroFormattingWriterTest {

    @ParameterizedTest
    @EnumSource(DataChannelFormat::class, names = ["JSONL", "PROTOBUF"])
    fun `Avro staging carries every Airbyte type as the CSV staging does`(
        format: DataChannelFormat,
    ) {
        val stream = AllAirbyteTypes.stream()
        val columns = loadSchema(stream)
        val csv = csvRows(stream, format)
        val avro = avroRecords(stream, format)

        assertEquals(columns.map { it.name }, avro.schema.fields.map { it.name() })
        columns.forEach { column ->
            assertFieldType(column, avro.schema.getField(column.name).schema())
        }

        assertEquals(csv.size, avro.records.size)
        csv.zip(avro.records).forEach { (csvRow, avroRecord) ->
            columns.forEachIndexed { i, column ->
                assertSameValue(column, csvRow[i], avroRecord.get(column.name))
            }
        }
    }

    @ParameterizedTest
    @EnumSource(DataChannelFormat::class, names = ["JSONL", "PROTOBUF"])
    fun `Avro values are BigQuery's encoding of the record's values`(format: DataChannelFormat) {
        val stream = AllAirbyteTypes.stream()
        val records = avroRecords(stream, format).records.associateBy { (it.get("id") as Long) }

        val typical = records.getValue(1)
        assertEquals(true, typical.get("bool_col"))
        assertEquals(123L, typical.get("int_col"))
        assertEquals(BigDecimal("12.500000000"), decimal(typical.get("num_col")))
        assertEquals("hello, \"world\"\nsecond line", typical.get("str_col").toString())
        assertEquals("ünïcödé ✓", typical.get("Str_Col_2").toString())
        assertEquals(LocalDate.of(2025, 6, 17).toEpochDay().toInt(), typical.get("date_col"))
        assertEquals("23:59:59.123456+02:00", typical.get("time_tz_col").toString())
        assertEquals(
            LocalTime.of(23, 59, 59, 123_456_000).toNanoOfDay() / 1000,
            typical.get("time_col"),
        )
        assertEquals(
            micros(Instant.parse("2025-06-17T21:59:59.123456Z")),
            typical.get("ts_tz_col"),
        )
        assertEquals(
            micros(LocalDateTime.parse("2025-06-17T23:59:59.123456").toInstant(ZoneOffset.UTC)),
            typical.get("ts_col"),
        )
        assertEquals(Jsons.readTree("""["a","b"]"""), json(typical.get("array_col")))
        assertEquals(Jsons.readTree("""{"k":"v"}"""), json(typical.get("obj_col")))
        assertEquals(
            Jsons.readTree("""{"nested":{"deep":[1,2,{"x":null}]}}"""),
            json(typical.get("obj_untyped_col")),
        )
        assertEquals("text", typical.get("legacy_union_col").toString())
        assertEquals(Jsons.readTree("42"), json(typical.get("union_col")))
        assertEquals(
            micros(Instant.ofEpochMilli(1_724_438_400_123L)),
            typical.get(Meta.COLUMN_NAME_AB_EXTRACTED_AT),
        )
        assertEquals(7L, typical.get(Meta.COLUMN_NAME_AB_GENERATION_ID))
        assertEquals(
            AllAirbyteTypes.rawId(mapOf("id" to "1")).toString(),
            typical.get(Meta.COLUMN_NAME_AB_RAW_ID).toString(),
        )

        val nulls = records.getValue(2)
        AllAirbyteTypes.schema.properties.keys
            .filter { it != "id" }
            .map { AllAirbyteTypes.columnNameMapping[it]!! }
            .forEach { assertNull(nulls.get(it), it) }

        val edges = records.getValue(3)
        assertEquals(Long.MAX_VALUE, edges.get("int_col"))
        assertEquals(
            BigDecimal("99999999999999999999999999999.999999999"),
            decimal(edges.get("num_col")),
        )
        // In a CSV file this value is the null marker; in Avro it stays the string it is.
        assertEquals(BigQueryConsts.NULL_MARKER, edges.get("str_col").toString())
        assertEquals("", edges.get("Str_Col_2").toString())
        assertEquals(LocalDate.of(1, 1, 1).toEpochDay().toInt(), edges.get("date_col"))
        assertEquals(micros(Instant.parse("0001-01-01T00:00:00Z")), edges.get("ts_tz_col"))
        assertEquals(
            micros(LocalDateTime.parse("9999-12-31T23:59:59.999999").toInstant(ZoneOffset.UTC)),
            edges.get("ts_col"),
        )
        assertEquals(0L, edges.get("time_col"))

        val limited = records.getValue(4)
        assertNull(limited.get("int_col"))
        assertNull(limited.get("ts_tz_col"))
        assertEquals(BigDecimal("1.000000001"), decimal(limited.get("num_col")))
        val changes =
            json(limited.get(Meta.COLUMN_NAME_AB_META))["changes"].associate {
                it["field"].textValue() to it["change"].textValue()
            }
        assertEquals("NULLED", changes["int_col"])
        assertEquals("NULLED", changes["ts_tz_col"])
        assertEquals("TRUNCATED", changes["num_col"])
    }

    private class AvroFile(val schema: Schema, val records: List<GenericRecord>)

    private fun loadSchema(stream: DestinationStream): List<Field> =
        BigQueryRecordFormatter.getDirectLoadSchema(stream, AllAirbyteTypes.columnNameMapping)
            .fields
            .toList()

    private fun write(
        writer: ObjectStorageFormattingWriter,
        stream: DestinationStream,
        format: DataChannelFormat,
    ) {
        AllAirbyteTypes.records(stream, format).forEach { writer.accept(it) }
        writer.flush()
        writer.close()
    }

    private fun csvRows(stream: DestinationStream, format: DataChannelFormat): List<List<String>> {
        val out = ByteArrayOutputStream()
        val writer =
            when (format) {
                DataChannelFormat.PROTOBUF ->
                    ProtoToBigQueryObjectStorageFormattingWriter(stream, out)
                else -> BigQueryObjectStorageFormattingWriter(stream, out)
            }
        write(writer, stream, format)
        return CSVFormat.DEFAULT.parse(out.toString(Charsets.UTF_8).reader()).records.drop(1).map {
            it.toList()
        }
    }

    private fun avroRecords(stream: DestinationStream, format: DataChannelFormat): AvroFile {
        val out = ByteArrayOutputStream()
        val writer =
            bigQueryAvroFormattingWriter(stream, AllAirbyteTypes.columnNameMapping, format, out)
        write(writer, stream, format)
        DataFileStream(ByteArrayInputStream(out.toByteArray()), GenericDatumReader<GenericRecord>())
            .use { file ->
                return AvroFile(file.schema, file.toList())
            }
    }

    private fun assertFieldType(column: Field, fieldSchema: Schema) {
        val schema =
            if (column.mode == Field.Mode.REQUIRED) {
                fieldSchema
            } else {
                assertEquals(Schema.Type.UNION, fieldSchema.type, column.name)
                assertEquals(Schema.Type.NULL, fieldSchema.types[0].type, column.name)
                fieldSchema.types[1]
            }
        val expected: Pair<Schema.Type, String?> =
            when (column.type.standardType) {
                StandardSQLTypeName.STRING -> Schema.Type.STRING to null
                StandardSQLTypeName.JSON -> Schema.Type.STRING to null
                StandardSQLTypeName.INT64 -> Schema.Type.LONG to null
                StandardSQLTypeName.BOOL -> Schema.Type.BOOLEAN to null
                StandardSQLTypeName.NUMERIC -> Schema.Type.BYTES to "decimal"
                StandardSQLTypeName.DATE -> Schema.Type.INT to "date"
                StandardSQLTypeName.TIME -> Schema.Type.LONG to "time-micros"
                StandardSQLTypeName.TIMESTAMP -> Schema.Type.LONG to "timestamp-micros"
                StandardSQLTypeName.DATETIME -> Schema.Type.LONG to "local-timestamp-micros"
                else -> throw AssertionError("unexpected column type ${column.type}")
            }
        assertEquals(expected, schema.type to schema.logicalType?.name, column.name)
        if (column.type.standardType == StandardSQLTypeName.JSON) {
            assertEquals("JSON", schema.getProp("sqlType"), column.name)
        }
        if (column.type.standardType == StandardSQLTypeName.NUMERIC) {
            val decimal = schema.logicalType as LogicalTypes.Decimal
            assertEquals(38 to 9, decimal.precision to decimal.scale)
        }
    }

    private fun assertSameValue(column: Field, csv: String, avro: Any?) {
        val name = column.name
        if (csv == BigQueryConsts.NULL_MARKER) {
            // The string "\N" is indistinguishable from the null marker in CSV only.
            if (avro?.toString() != BigQueryConsts.NULL_MARKER) assertNull(avro, name)
            return
        }
        assertNotNull(avro, name)
        when (column.type.standardType) {
            StandardSQLTypeName.STRING -> assertEquals(csv, avro.toString(), name)
            StandardSQLTypeName.JSON -> assertEquals(Jsons.readTree(csv), json(avro), name)
            StandardSQLTypeName.INT64 -> assertEquals(csv.toLong(), avro, name)
            StandardSQLTypeName.BOOL -> assertEquals(csv.toBooleanStrict(), avro, name)
            StandardSQLTypeName.NUMERIC ->
                assertEquals(0, BigDecimal(csv).compareTo(decimal(avro)), "$name: $csv")
            StandardSQLTypeName.DATE ->
                assertEquals(LocalDate.parse(csv).toEpochDay().toInt(), avro, name)
            StandardSQLTypeName.TIME ->
                assertEquals(LocalTime.parse(csv).toNanoOfDay() / 1000, avro, name)
            StandardSQLTypeName.TIMESTAMP ->
                assertEquals(
                    micros(OffsetDateTime.parse(csv.replaceFirst(' ', 'T')).toInstant()),
                    avro,
                    "$name: $csv",
                )
            StandardSQLTypeName.DATETIME ->
                assertEquals(
                    micros(LocalDateTime.parse(csv).toInstant(ZoneOffset.UTC)),
                    avro,
                    "$name: $csv",
                )
            else -> throw AssertionError("unexpected column type ${column.type}")
        }
    }

    private fun micros(instant: Instant): Long = ChronoUnit.MICROS.between(Instant.EPOCH, instant)

    private fun decimal(avro: Any?): BigDecimal {
        val buffer = (avro as ByteBuffer).duplicate()
        val bytes = ByteArray(buffer.remaining()).also { buffer.get(it) }
        return BigDecimal(BigInteger(bytes), 9)
    }

    private fun json(avro: Any?) =
        Jsons.readTree(avro.toString()).also { assertTrue(!it.isMissingNode) }
}
