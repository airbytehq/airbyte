/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.write.storage_write

import com.google.cloud.bigquery.Field
import com.google.cloud.bigquery.StandardSQLTypeName
import com.google.protobuf.DescriptorProtos.FieldDescriptorProto
import com.google.protobuf.DescriptorProtos.FileDescriptorProto
import com.google.protobuf.Descriptors
import com.google.protobuf.DynamicMessage
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.config.DataChannelFormat
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.util.Jsons
import io.airbyte.integrations.destination.bigquery.BigQueryConsts
import io.airbyte.integrations.destination.bigquery.write.bulk_loader.AllAirbyteTypes
import io.airbyte.integrations.destination.bigquery.write.bulk_loader.BigQueryLoadRows
import io.airbyte.integrations.destination.bigquery.write.bulk_loader.BigQueryObjectStorageFormattingWriter
import io.airbyte.integrations.destination.bigquery.write.bulk_loader.ProtoToBigQueryObjectStorageFormattingWriter
import java.io.ByteArrayOutputStream
import java.math.BigDecimal
import java.time.Instant
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.OffsetDateTime
import java.time.temporal.ChronoUnit
import org.apache.commons.csv.CSVFormat
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.EnumSource

/**
 * The Storage Write API rows of every Airbyte type hold what the CSV staging file holds, in the
 * wire types the API converts to the columns' types.
 */
class BigQueryProtoRowsTest {

    @ParameterizedTest
    @EnumSource(DataChannelFormat::class, names = ["JSONL", "PROTOBUF"])
    fun `Storage Write API rows carry every Airbyte type as the CSV staging does`(
        format: DataChannelFormat,
    ) {
        val stream = AllAirbyteTypes.stream()
        val loadRows = BigQueryLoadRows.of(stream, AllAirbyteTypes.columnNameMapping, format)
        val protoRows = BigQueryProtoRows(loadRows)
        val descriptor = descriptor(protoRows)
        val csv = csvRows(stream, format)
        val messages =
            AllAirbyteTypes.records(stream, format).map {
                DynamicMessage.parseFrom(descriptor, protoRows.encode(it))
            }

        assertEquals(loadRows.columns.map { it.name }, descriptor.fields.map { it.name })
        loadRows.columns.zip(descriptor.fields).forEach { (column, field) ->
            assertEquals(expectedType(column), field.toProto().type, column.name)
            assertEquals(FieldDescriptorProto.Label.LABEL_OPTIONAL, field.toProto().label)
        }

        assertEquals(csv.size, messages.size)
        csv.zip(messages).forEach { (csvRow, message) ->
            loadRows.columns.forEachIndexed { i, column ->
                assertSameValue(column, csvRow[i], message, descriptor.fields[i])
            }
        }
    }

    @ParameterizedTest
    @EnumSource(DataChannelFormat::class, names = ["JSONL", "PROTOBUF"])
    fun `Storage Write API values are BigQuery's encoding of the record's values`(
        format: DataChannelFormat,
    ) {
        val stream = AllAirbyteTypes.stream()
        val protoRows =
            BigQueryProtoRows(
                BigQueryLoadRows.of(stream, AllAirbyteTypes.columnNameMapping, format),
            )
        val descriptor = descriptor(protoRows)
        val rows =
            AllAirbyteTypes.records(stream, format)
                .map { DynamicMessage.parseFrom(descriptor, protoRows.encode(it)) }
                .associateBy { it.value(descriptor, "id") as Long }

        val typical = rows.getValue(1)
        assertEquals(true, typical.value(descriptor, "bool_col"))
        assertEquals("12.500000000", typical.value(descriptor, "num_col"))
        assertEquals("hello, \"world\"\nsecond line", typical.value(descriptor, "str_col"))
        assertEquals("ünïcödé ✓", typical.value(descriptor, "Str_Col_2"))
        assertEquals(
            LocalDate.of(2025, 6, 17).toEpochDay().toInt(),
            typical.value(descriptor, "date_col"),
        )
        assertEquals("23:59:59.123456", typical.value(descriptor, "time_col"))
        assertEquals(
            micros(Instant.parse("2025-06-17T21:59:59.123456Z")),
            typical.value(descriptor, "ts_tz_col"),
        )
        assertEquals("2025-06-17 23:59:59.123456", typical.value(descriptor, "ts_col"))
        assertEquals(
            micros(Instant.ofEpochMilli(1_724_438_400_123L)),
            typical.value(descriptor, Meta.COLUMN_NAME_AB_EXTRACTED_AT),
        )

        val nulls = rows.getValue(2)
        AllAirbyteTypes.schema.properties.keys
            .filter { it != "id" }
            .map { AllAirbyteTypes.columnNameMapping[it]!! }
            .forEach { assertFalse(nulls.hasField(descriptor.findFieldByName(it)), it) }

        val edges = rows.getValue(3)
        assertEquals(Long.MAX_VALUE, edges.value(descriptor, "int_col"))
        assertEquals(
            "99999999999999999999999999999.999999999",
            edges.value(descriptor, "num_col"),
        )
        // In a CSV file this value is the null marker; here it stays the string it is.
        assertEquals(BigQueryConsts.NULL_MARKER, edges.value(descriptor, "str_col"))
        assertEquals("", edges.value(descriptor, "Str_Col_2"))
        assertEquals(
            LocalDate.of(1, 1, 1).toEpochDay().toInt(),
            edges.value(descriptor, "date_col"),
        )
        assertEquals("00:00:00.000000", edges.value(descriptor, "time_col"))
        assertEquals("9999-12-31 23:59:59.999999", edges.value(descriptor, "ts_col"))

        val limited = rows.getValue(4)
        assertFalse(limited.hasField(descriptor.findFieldByName("int_col")))
        assertEquals("1.000000001", limited.value(descriptor, "num_col"))
        assertEquals("0001-01-01 00:00:00.000000", limited.value(descriptor, "ts_col"))
    }

    private fun DynamicMessage.value(descriptor: Descriptors.Descriptor, field: String): Any? =
        getField(descriptor.findFieldByName(field))

    private fun descriptor(rows: BigQueryProtoRows): Descriptors.Descriptor =
        Descriptors.FileDescriptor.buildFrom(
                FileDescriptorProto.newBuilder()
                    .setName("airbyte_row.proto")
                    .addMessageType(rows.schema.protoDescriptor)
                    .build(),
                emptyArray(),
            )
            .messageTypes
            .single()

    private fun csvRows(stream: DestinationStream, format: DataChannelFormat): List<List<String>> {
        val out = ByteArrayOutputStream()
        val writer =
            when (format) {
                DataChannelFormat.PROTOBUF ->
                    ProtoToBigQueryObjectStorageFormattingWriter(stream, out)
                else -> BigQueryObjectStorageFormattingWriter(stream, out)
            }
        AllAirbyteTypes.records(stream, format).forEach { writer.accept(it) }
        writer.flush()
        writer.close()
        return CSVFormat.DEFAULT.parse(out.toString(Charsets.UTF_8).reader()).records.drop(1).map {
            it.toList()
        }
    }

    private fun expectedType(column: Field): FieldDescriptorProto.Type =
        when (column.type.standardType) {
            StandardSQLTypeName.STRING,
            StandardSQLTypeName.JSON,
            StandardSQLTypeName.NUMERIC,
            StandardSQLTypeName.TIME,
            StandardSQLTypeName.DATETIME -> FieldDescriptorProto.Type.TYPE_STRING
            StandardSQLTypeName.INT64,
            StandardSQLTypeName.TIMESTAMP -> FieldDescriptorProto.Type.TYPE_INT64
            StandardSQLTypeName.BOOL -> FieldDescriptorProto.Type.TYPE_BOOL
            StandardSQLTypeName.DATE -> FieldDescriptorProto.Type.TYPE_INT32
            else -> throw AssertionError("unexpected column type ${column.type}")
        }

    private fun assertSameValue(
        column: Field,
        csv: String,
        message: DynamicMessage,
        field: Descriptors.FieldDescriptor,
    ) {
        val name = column.name
        if (csv == BigQueryConsts.NULL_MARKER) {
            // The string "\N" is indistinguishable from the null marker in CSV only.
            if (message.hasField(field)) {
                assertEquals(BigQueryConsts.NULL_MARKER, message.getField(field), name)
            }
            return
        }
        assertTrue(message.hasField(field), name)
        val value = message.getField(field)
        assertNotNull(value, name)
        when (column.type.standardType) {
            StandardSQLTypeName.STRING -> assertEquals(csv, value, name)
            StandardSQLTypeName.JSON ->
                assertEquals(Jsons.readTree(csv), Jsons.readTree(value as String), name)
            StandardSQLTypeName.INT64 -> assertEquals(csv.toLong(), value, name)
            StandardSQLTypeName.BOOL -> assertEquals(csv.toBooleanStrict(), value, name)
            StandardSQLTypeName.NUMERIC ->
                assertEquals(0, BigDecimal(csv).compareTo(BigDecimal(value as String)), name)
            StandardSQLTypeName.DATE ->
                assertEquals(LocalDate.parse(csv).toEpochDay().toInt(), value, name)
            StandardSQLTypeName.TIME ->
                assertEquals(LocalTime.parse(csv), LocalTime.parse(value as String), name)
            StandardSQLTypeName.TIMESTAMP ->
                assertEquals(
                    micros(OffsetDateTime.parse(csv.replaceFirst(' ', 'T')).toInstant()),
                    value,
                    "$name: $csv",
                )
            StandardSQLTypeName.DATETIME ->
                assertEquals(
                    LocalDateTime.parse(csv),
                    LocalDateTime.parse((value as String).replaceFirst(' ', 'T')),
                    "$name: $csv",
                )
            else -> throw AssertionError("unexpected column type ${column.type}")
        }
    }

    private fun micros(instant: Instant): Long = ChronoUnit.MICROS.between(Instant.EPOCH, instant)
}
