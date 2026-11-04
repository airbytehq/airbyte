/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.write.storage_write

import com.google.cloud.bigquery.StandardSQLTypeName
import com.google.cloud.bigquery.storage.v1.ProtoSchema
import com.google.protobuf.ByteString
import com.google.protobuf.CodedOutputStream
import com.google.protobuf.DescriptorProtos.DescriptorProto
import com.google.protobuf.DescriptorProtos.FieldDescriptorProto
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.integrations.destination.bigquery.BigQueryConsts
import io.airbyte.integrations.destination.bigquery.write.bulk_loader.BigQueryLoadRows
import io.airbyte.integrations.destination.bigquery.write.bulk_loader.BigQueryLoadValues
import java.time.format.DateTimeFormatter

/**
 * Encodes the rows of [BigQueryLoadRows] as the protocol buffer messages the Storage Write API
 * reads as the table's columns. Values, nulls and meta changes are the CSV path's own; only the
 * encoding differs.
 *
 * Each column is an optional field named after it and numbered in column order; a null value is an
 * absent field. The Storage Write API matches fields to columns by name and converts each field
 * from its wire type to the column's type (see [fieldType]).
 */
class BigQueryProtoRows(private val rows: BigQueryLoadRows) {
    val schema: ProtoSchema =
        ProtoSchema.newBuilder()
            .setProtoDescriptor(
                DescriptorProto.newBuilder()
                    .setName("airbyte_row")
                    .addAllField(
                        rows.columns.mapIndexed { i, column ->
                            FieldDescriptorProto.newBuilder()
                                .setName(column.name)
                                .setNumber(i + 1)
                                .setLabel(FieldDescriptorProto.Label.LABEL_OPTIONAL)
                                .setType(fieldType(column.type.standardType))
                                .build()
                        },
                    )
                    .build(),
            )
            .build()

    private val writers: Array<FieldWriter> =
        rows.columns.map { fieldWriter(it.type.standardType) }.toTypedArray()

    fun encode(record: DestinationRecordRaw): ByteString {
        val values = rows.generate(record)
        require(values.size == writers.size) {
            "row has ${values.size} values for ${writers.size} columns"
        }
        val out = ByteString.newOutput()
        val coded = CodedOutputStream.newInstance(out)
        for (i in writers.indices) {
            val value = values[i]
            // Identity, not equality: the generators mark nulls with this very constant, and a
            // string value "\N" is data.
            if (value !== BigQueryConsts.NULL_MARKER) {
                writers[i].write(coded, i + 1, value)
            }
        }
        coded.flush()
        return out.toByteString()
    }

    private fun interface FieldWriter {
        fun write(out: CodedOutputStream, field: Int, value: Any)
    }

    companion object {
        private val TIME: DateTimeFormatter = DateTimeFormatter.ofPattern("HH:mm:ss.SSSSSS")
        private val DATETIME: DateTimeFormatter =
            DateTimeFormatter.ofPattern("uuuu-MM-dd HH:mm:ss.SSSSSS")

        /**
         * The wire type of a column of [type]. NUMERIC, TIME and DATETIME go as their SQL literals;
         * the alternatives are bit-packed encodings of the client library's encoders.
         */
        fun fieldType(type: StandardSQLTypeName): FieldDescriptorProto.Type =
            when (type) {
                StandardSQLTypeName.STRING,
                StandardSQLTypeName.JSON,
                StandardSQLTypeName.NUMERIC,
                StandardSQLTypeName.TIME,
                StandardSQLTypeName.DATETIME -> FieldDescriptorProto.Type.TYPE_STRING
                StandardSQLTypeName.INT64,
                StandardSQLTypeName.TIMESTAMP -> FieldDescriptorProto.Type.TYPE_INT64
                StandardSQLTypeName.BOOL -> FieldDescriptorProto.Type.TYPE_BOOL
                StandardSQLTypeName.DATE -> FieldDescriptorProto.Type.TYPE_INT32
                else ->
                    throw IllegalArgumentException(
                        "no Storage Write API type for BigQuery type $type",
                    )
            }

        private fun fieldWriter(type: StandardSQLTypeName): FieldWriter =
            when (type) {
                StandardSQLTypeName.STRING,
                StandardSQLTypeName.JSON ->
                    FieldWriter { out, field, v ->
                        out.writeString(field, v as? String ?: v.toString())
                    }
                StandardSQLTypeName.INT64 ->
                    FieldWriter { out, field, v ->
                        out.writeInt64(field, BigQueryLoadValues.toLong(v))
                    }
                StandardSQLTypeName.BOOL ->
                    FieldWriter { out, field, v ->
                        out.writeBool(field, v as? Boolean ?: v.toString().toBooleanStrict())
                    }
                StandardSQLTypeName.NUMERIC ->
                    FieldWriter { out, field, v ->
                        out.writeString(field, BigQueryLoadValues.toNumeric(v).toPlainString())
                    }
                // Days since the epoch.
                StandardSQLTypeName.DATE ->
                    FieldWriter { out, field, v ->
                        out.writeInt32(
                            field,
                            Math.toIntExact(BigQueryLoadValues.toDate(v).toEpochDay()),
                        )
                    }
                StandardSQLTypeName.TIME ->
                    FieldWriter { out, field, v ->
                        out.writeString(field, TIME.format(BigQueryLoadValues.toTime(v)))
                    }
                // Microseconds since the epoch.
                StandardSQLTypeName.TIMESTAMP ->
                    FieldWriter { out, field, v ->
                        out.writeInt64(
                            field,
                            BigQueryLoadValues.micros(BigQueryLoadValues.toInstant(v)),
                        )
                    }
                StandardSQLTypeName.DATETIME ->
                    FieldWriter { out, field, v ->
                        out.writeString(field, DATETIME.format(BigQueryLoadValues.toDateTime(v)))
                    }
                else ->
                    throw IllegalArgumentException(
                        "no Storage Write API type for BigQuery type $type",
                    )
            }
    }
}
