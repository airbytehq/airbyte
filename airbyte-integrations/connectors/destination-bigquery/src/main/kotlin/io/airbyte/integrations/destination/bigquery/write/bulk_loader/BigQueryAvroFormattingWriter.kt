/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.write.bulk_loader

import com.google.cloud.bigquery.Field
import com.google.cloud.bigquery.StandardSQLTypeName
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.config.DataChannelFormat
import io.airbyte.cdk.load.data.csv.toCsvHeader
import io.airbyte.cdk.load.data.withAirbyteMeta
import io.airbyte.cdk.load.file.object_storage.ObjectStorageFormattingWriter
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.orchestration.db.ColumnNameMapping
import io.airbyte.integrations.destination.bigquery.BigQueryConsts
import io.airbyte.integrations.destination.bigquery.formatter.BigQueryRecordFormatter
import java.io.OutputStream
import java.math.BigDecimal
import java.math.BigInteger
import java.math.RoundingMode
import java.nio.ByteBuffer
import java.time.Instant
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.OffsetDateTime
import java.time.ZoneOffset
import java.time.ZonedDateTime
import org.apache.avro.JsonProperties
import org.apache.avro.LogicalTypes
import org.apache.avro.Schema
import org.apache.avro.file.CodecFactory
import org.apache.avro.file.DataFileWriter
import org.apache.avro.generic.GenericData
import org.apache.avro.generic.GenericDatumWriter

/**
 * Writes the rows of the CSV row generators as an Avro container file. Values, nulls and meta
 * changes are the CSV path's own; only the encoding differs.
 *
 * BigQuery matches Avro fields to the table's columns by name, and with use_avro_logical_types it
 * reads each field as the column's type when the Avro type is the one it maps to that type (see
 * [BigQueryAvro.fieldSchema]). A file whose field types differ is rejected as a schema change.
 *
 * @param columns the load schema's fields, in the order of the generated rows.
 */
class BigQueryAvroFormattingWriter(
    columns: List<Field>,
    outputStream: OutputStream,
    private val rows: (DestinationRecordRaw) -> List<Any>,
) : ObjectStorageFormattingWriter {
    private val schema: Schema = BigQueryAvro.recordSchema(columns)
    private val converters: Array<(Any) -> Any> =
        columns.map { BigQueryAvro.converter(it.type.standardType) }.toTypedArray()
    private val record = GenericData.Record(schema)
    private val writer =
        DataFileWriter(GenericDatumWriter<GenericData.Record>(schema)).apply {
            setCodec(CodecFactory.snappyCodec())
            create(schema, outputStream)
        }

    override fun accept(record: DestinationRecordRaw) {
        val row = rows(record)
        require(row.size == converters.size) {
            "row has ${row.size} values for ${converters.size} columns"
        }
        for (i in converters.indices) {
            val value = row[i]
            // Identity, not equality: the generators mark nulls with this very constant, and a
            // string value "\N" is data.
            this.record.put(
                i,
                if (value === BigQueryConsts.NULL_MARKER) null else converters[i](value),
            )
        }
        writer.append(this.record)
    }

    override fun flush() {
        writer.flush()
    }

    override fun close() {
        writer.close()
    }
}

/**
 * The Avro writer for [stream], fed by the CSV row generator of [dataChannelFormat]; its fields
 * take the names and types of the direct-load table's columns.
 */
fun bigQueryAvroFormattingWriter(
    stream: DestinationStream,
    columnNameMapping: ColumnNameMapping,
    dataChannelFormat: DataChannelFormat,
    outputStream: OutputStream,
): BigQueryAvroFormattingWriter {
    val finalSchema = stream.schema.withAirbyteMeta(true)
    val header = finalSchema.toCsvHeader()
    val columns =
        BigQueryRecordFormatter.getDirectLoadSchema(stream, columnNameMapping).fields.associateBy {
            it.name
        }
    val rowColumns = header.map { name ->
        val columnName = if (name in Meta.COLUMN_NAMES) name else columnNameMapping[name]!!
        columns[columnName]
            ?: throw IllegalStateException("no column $columnName in the load schema")
    }
    val rows: (DestinationRecordRaw) -> List<Any> =
        when (dataChannelFormat) {
            DataChannelFormat.PROTOBUF -> {
                val generator =
                    ProtoToBigQueryCSVRowGenerator(
                        header,
                        stream,
                        stream.airbyteValueProxyFieldAccessors,
                    )
                ({ record -> generator.generate(record).asList() })
            }
            else -> {
                val generator = BigQueryCSVRowGenerator()
                ({ record -> generator.generate(record, finalSchema) })
            }
        }
    return BigQueryAvroFormattingWriter(rowColumns, outputStream, rows)
}

object BigQueryAvro {
    private const val NUMERIC_PRECISION = 38
    private const val NUMERIC_SCALE = 9

    fun recordSchema(columns: List<Field>): Schema =
        Schema.createRecord(
            "airbyte_staging",
            null,
            null,
            false,
            columns.map { column ->
                val type = fieldSchema(column.type.standardType)
                if (column.mode == Field.Mode.REQUIRED) {
                    Schema.Field(column.name, type)
                } else {
                    Schema.Field(
                        column.name,
                        Schema.createUnion(Schema.create(Schema.Type.NULL), type),
                        null,
                        JsonProperties.NULL_VALUE,
                    )
                }
            },
        )

    /** The Avro type BigQuery reads as [type]. */
    fun fieldSchema(type: StandardSQLTypeName): Schema =
        when (type) {
            StandardSQLTypeName.STRING -> Schema.create(Schema.Type.STRING)
            // A string with sqlType JSON loads into a JSON column; a plain string does not.
            StandardSQLTypeName.JSON ->
                Schema.create(Schema.Type.STRING).apply { addProp("sqlType", "JSON") }
            StandardSQLTypeName.INT64 -> Schema.create(Schema.Type.LONG)
            StandardSQLTypeName.BOOL -> Schema.create(Schema.Type.BOOLEAN)
            StandardSQLTypeName.NUMERIC ->
                LogicalTypes.decimal(NUMERIC_PRECISION, NUMERIC_SCALE)
                    .addToSchema(Schema.create(Schema.Type.BYTES))
            StandardSQLTypeName.DATE ->
                LogicalTypes.date().addToSchema(Schema.create(Schema.Type.INT))
            StandardSQLTypeName.TIME ->
                LogicalTypes.timeMicros().addToSchema(Schema.create(Schema.Type.LONG))
            StandardSQLTypeName.TIMESTAMP ->
                LogicalTypes.timestampMicros().addToSchema(Schema.create(Schema.Type.LONG))
            StandardSQLTypeName.DATETIME ->
                LogicalTypes.localTimestampMicros().addToSchema(Schema.create(Schema.Type.LONG))
            else -> throw IllegalArgumentException("no Avro staging type for BigQuery type $type")
        }

    /**
     * Turns a value of the CSV row generators into the Avro datum of [type]. The generators hand
     * over native values or the text the CSV file would hold, depending on the record's path.
     */
    fun converter(type: StandardSQLTypeName): (Any) -> Any =
        when (type) {
            StandardSQLTypeName.STRING,
            StandardSQLTypeName.JSON -> { v ->
                v as? String ?: v.toString()
            }
            StandardSQLTypeName.INT64 -> { v ->
                toLong(v)
            }
            StandardSQLTypeName.BOOL -> { v ->
                v as? Boolean ?: v.toString().toBooleanStrict()
            }
            StandardSQLTypeName.NUMERIC -> { v ->
                toDecimalBytes(v)
            }
            StandardSQLTypeName.DATE -> { v ->
                toDate(v).toEpochDay().toInt()
            }
            StandardSQLTypeName.TIME -> { v ->
                toTime(v).toNanoOfDay() / 1_000
            }
            StandardSQLTypeName.TIMESTAMP -> { v ->
                micros(toInstant(v))
            }
            StandardSQLTypeName.DATETIME -> { v ->
                micros(toDateTime(v).toInstant(ZoneOffset.UTC))
            }
            else -> throw IllegalArgumentException("no Avro staging type for BigQuery type $type")
        }

    private fun toLong(v: Any): Long =
        when (v) {
            is Long -> v
            is Int -> v.toLong()
            is BigInteger -> v.longValueExact()
            is BigDecimal -> v.longValueExact()
            is Number -> v.toLong()
            else -> v.toString().toLong()
        }

    private fun toDecimalBytes(v: Any): ByteBuffer {
        val decimal =
            when (v) {
                is BigDecimal -> v
                is BigInteger -> BigDecimal(v)
                is Long -> BigDecimal.valueOf(v)
                is Int -> BigDecimal.valueOf(v.toLong())
                else -> BigDecimal(v.toString())
            }
        return ByteBuffer.wrap(
            decimal.setScale(NUMERIC_SCALE, RoundingMode.HALF_UP).unscaledValue().toByteArray(),
        )
    }

    private fun toDate(v: Any): LocalDate = v as? LocalDate ?: LocalDate.parse(v.toString())

    private fun toTime(v: Any): LocalTime = v as? LocalTime ?: LocalTime.parse(v.toString())

    private fun toDateTime(v: Any): LocalDateTime =
        v as? LocalDateTime ?: LocalDateTime.parse(v.toString())

    private fun toInstant(v: Any): Instant =
        when (v) {
            is Instant -> v
            is OffsetDateTime -> v.toInstant()
            is ZonedDateTime -> v.toInstant()
            // _airbyte_extracted_at of protobuf records: "2024-08-23 18:40:00.000000+00:00".
            else -> OffsetDateTime.parse(v.toString().replaceFirst(' ', 'T')).toInstant()
        }

    private fun micros(instant: Instant): Long =
        Math.addExact(Math.multiplyExact(instant.epochSecond, 1_000_000L), instant.nano / 1_000L)
}
