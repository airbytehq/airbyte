/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.write.bulk_loader

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.config.DataChannelFormat
import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.ArrayType
import io.airbyte.cdk.load.data.ArrayTypeWithoutSchema
import io.airbyte.cdk.load.data.BooleanType
import io.airbyte.cdk.load.data.DateType
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.NumberType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectTypeWithEmptySchema
import io.airbyte.cdk.load.data.ObjectTypeWithoutSchema
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.TimeTypeWithTimezone
import io.airbyte.cdk.load.data.TimeTypeWithoutTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithoutTimezone
import io.airbyte.cdk.load.data.UnionType
import io.airbyte.cdk.load.data.UnknownType
import io.airbyte.cdk.load.message.DestinationRecordJsonSource
import io.airbyte.cdk.load.message.DestinationRecordProtobufSource
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.orchestration.db.ColumnNameMapping
import io.airbyte.cdk.load.util.Jsons
import io.airbyte.cdk.protocol.AirbyteValueProtobufEncoder
import io.airbyte.integrations.destination.bigquery.BigQuerySQLNameTransformer
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.airbyte.protocol.protobuf.AirbyteMessage.AirbyteMessageProtobuf
import io.airbyte.protocol.protobuf.AirbyteRecordMessage.AirbyteRecordMessageProtobuf
import java.math.BigDecimal
import java.math.BigInteger
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.OffsetDateTime
import java.time.OffsetTime
import java.util.UUID

/**
 * A stream with a column for every Airbyte type the destination maps to a BigQuery column type, and
 * records with typical values, nulls, and values at or past the edges of BigQuery's ranges.
 */
object AllAirbyteTypes {
    val schema =
        ObjectType(
            linkedMapOf(
                "id" to FieldType(IntegerType, nullable = true),
                "bool_col" to FieldType(BooleanType, nullable = true),
                "int_col" to FieldType(IntegerType, nullable = true),
                "num_col" to FieldType(NumberType, nullable = true),
                "str_col" to FieldType(StringType, nullable = true),
                // BigQuery names it Str_Col_2; Avro fields go by column name.
                "Str Col-2" to FieldType(StringType, nullable = true),
                "date_col" to FieldType(DateType, nullable = true),
                "time_tz_col" to FieldType(TimeTypeWithTimezone, nullable = true),
                "time_col" to FieldType(TimeTypeWithoutTimezone, nullable = true),
                "ts_tz_col" to FieldType(TimestampTypeWithTimezone, nullable = true),
                "ts_col" to FieldType(TimestampTypeWithoutTimezone, nullable = true),
                "array_col" to
                    FieldType(ArrayType(FieldType(StringType, nullable = true)), nullable = true),
                "array_untyped_col" to FieldType(ArrayTypeWithoutSchema, nullable = true),
                "obj_col" to
                    FieldType(
                        ObjectType(linkedMapOf("k" to FieldType(StringType, nullable = true))),
                        nullable = true,
                    ),
                "obj_empty_col" to FieldType(ObjectTypeWithEmptySchema, nullable = true),
                "obj_untyped_col" to FieldType(ObjectTypeWithoutSchema, nullable = true),
                "legacy_union_col" to
                    FieldType(
                        UnionType.of(StringType, IntegerType, isLegacyUnion = true),
                        nullable = true,
                    ),
                "union_col" to FieldType(UnionType.of(StringType, IntegerType), nullable = true),
                "unknown_col" to
                    FieldType(UnknownType(Jsons.readTree("""{"type":"mystery"}""")), true),
            ),
        )

    val columnNameMapping =
        ColumnNameMapping(
            schema.properties.keys.associateWith {
                BigQuerySQLNameTransformer().convertStreamName(it)
            },
        )

    /** Column values as the source would send them in a JSON record. */
    val rows: List<Map<String, String>> =
        listOf(
            mapOf(
                "id" to "1",
                "bool_col" to "true",
                "int_col" to "123",
                "num_col" to "12.5",
                "str_col" to "\"hello, \\\"world\\\"\\nsecond line\"",
                "Str Col-2" to "\"ünïcödé ✓\"",
                "date_col" to "\"2025-06-17\"",
                "time_tz_col" to "\"23:59:59.123456+02:00\"",
                "time_col" to "\"23:59:59.123456\"",
                "ts_tz_col" to "\"2025-06-17T23:59:59.123456+02:00\"",
                "ts_col" to "\"2025-06-17T23:59:59.123456\"",
                "array_col" to """["a","b"]""",
                "array_untyped_col" to """[1,"two",{"three":3}]""",
                "obj_col" to """{"k":"v"}""",
                "obj_empty_col" to """{}""",
                "obj_untyped_col" to """{"nested":{"deep":[1,2,{"x":null}]}}""",
                "legacy_union_col" to "\"text\"",
                "union_col" to "42",
                "unknown_col" to """{"anything":true}""",
            ),
            // Every column null.
            mapOf("id" to "2") +
                schema.properties.keys.filter { it != "id" }.associateWith { "null" },
            // At and past the edges of BigQuery's ranges.
            mapOf(
                "id" to "3",
                "bool_col" to "false",
                "int_col" to "9223372036854775807",
                "num_col" to "99999999999999999999999999999.999999999",
                // The CSV null marker, as data.
                "str_col" to "\"\\\\N\"",
                "Str Col-2" to "\"\"",
                "date_col" to "\"0001-01-01\"",
                "time_tz_col" to "\"00:00:00Z\"",
                "time_col" to "\"00:00:00\"",
                "ts_tz_col" to "\"0001-01-01T00:00:00Z\"",
                "ts_col" to "\"9999-12-31T23:59:59.999999\"",
                "array_col" to "[]",
                "array_untyped_col" to "[]",
                "obj_col" to "{}",
                "obj_empty_col" to "{}",
                "obj_untyped_col" to "{}",
                "legacy_union_col" to "7",
                "union_col" to "\"seven\"",
                "unknown_col" to "\"just a string\"",
            ),
            // Nulled or rounded with a meta change.
            mapOf(
                "id" to "4",
                "int_col" to "92233720368547758070",
                "num_col" to "1.0000000005",
                "date_col" to "\"9999-12-31\"",
                "ts_tz_col" to "\"9999-12-31T23:59:59.999999-08:00\"",
                "ts_col" to "\"0001-01-01T00:00:00\"",
                "time_col" to "\"12:00:00\"",
            ),
        )

    fun stream(): DestinationStream =
        DestinationStream(
            unmappedNamespace = "test_ns",
            unmappedName = "all_types",
            Append,
            schema,
            generationId = 7,
            minimumGenerationId = 0,
            syncId = 42,
            namespaceMapper = NamespaceMapper(),
        )

    fun rawId(row: Map<String, String>): UUID = UUID.nameUUIDFromBytes(row["id"]!!.toByteArray())

    fun records(stream: DestinationStream, format: DataChannelFormat): List<DestinationRecordRaw> =
        rows.map { row ->
            val source =
                when (format) {
                    DataChannelFormat.PROTOBUF -> protobufSource(stream, row)
                    else -> jsonSource(row)
                }
            DestinationRecordRaw(stream, source, 1000, airbyteRawId = rawId(row))
        }

    private const val EMITTED_AT_MS = 1_724_438_400_123L

    private fun jsonSource(row: Map<String, String>) =
        DestinationRecordJsonSource(
            AirbyteMessage()
                .withType(AirbyteMessage.Type.RECORD)
                .withRecord(
                    AirbyteRecordMessage()
                        .withStream("all_types")
                        .withNamespace("test_ns")
                        .withEmittedAt(EMITTED_AT_MS)
                        .withData(
                            Jsons.readTree(
                                row.entries.joinToString(",", "{", "}") { (k, v) ->
                                    "${Jsons.writeValueAsString(k)}:$v"
                                },
                            ),
                        ),
                ),
        )

    /** The values a socket source sends for the same JSON values, in accessor order. */
    private fun protobufSource(
        stream: DestinationStream,
        row: Map<String, String>,
    ): DestinationRecordProtobufSource {
        val encoder = AirbyteValueProtobufEncoder()
        val values =
            stream.airbyteValueProxyFieldAccessors
                .sortedBy { it.index }
                .map { accessor ->
                    val json = row[accessor.name]?.let { Jsons.readTree(it) }
                    protobufValue(encoder, accessor.type, json).build()
                }
        val record =
            AirbyteRecordMessageProtobuf.newBuilder()
                .setStreamName("all_types")
                .setStreamNamespace("test_ns")
                .setEmittedAtMs(EMITTED_AT_MS)
                .addAllData(values)
                .build()
        return DestinationRecordProtobufSource(
            AirbyteMessageProtobuf.newBuilder().setRecord(record).build(),
        )
    }

    private fun protobufValue(
        encoder: AirbyteValueProtobufEncoder,
        type: AirbyteType,
        json: JsonNode?,
    ) =
        if (json == null || json.isNull) {
            encoder.encode(null, LeafAirbyteSchemaType.STRING)
        } else {
            when (type) {
                BooleanType -> encoder.encode(json.booleanValue(), LeafAirbyteSchemaType.BOOLEAN)
                IntegerType ->
                    encoder.encode(BigInteger(json.asText()), LeafAirbyteSchemaType.INTEGER)
                NumberType ->
                    encoder.encode(BigDecimal(json.asText()), LeafAirbyteSchemaType.NUMBER)
                StringType -> encoder.encode(json.textValue(), LeafAirbyteSchemaType.STRING)
                DateType ->
                    encoder.encode(LocalDate.parse(json.textValue()), LeafAirbyteSchemaType.DATE)
                TimeTypeWithTimezone ->
                    encoder.encode(
                        OffsetTime.parse(json.textValue()),
                        LeafAirbyteSchemaType.TIME_WITH_TIMEZONE,
                    )
                TimeTypeWithoutTimezone ->
                    encoder.encode(
                        LocalTime.parse(json.textValue()),
                        LeafAirbyteSchemaType.TIME_WITHOUT_TIMEZONE,
                    )
                TimestampTypeWithTimezone ->
                    encoder.encode(
                        OffsetDateTime.parse(json.textValue()),
                        LeafAirbyteSchemaType.TIMESTAMP_WITH_TIMEZONE,
                    )
                TimestampTypeWithoutTimezone ->
                    encoder.encode(
                        LocalDateTime.parse(json.textValue()),
                        LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE,
                    )
                else ->
                    encoder.encode(
                        Jsons.writeValueAsBytes(json),
                        LeafAirbyteSchemaType.JSONB,
                    )
            }
        }
}
