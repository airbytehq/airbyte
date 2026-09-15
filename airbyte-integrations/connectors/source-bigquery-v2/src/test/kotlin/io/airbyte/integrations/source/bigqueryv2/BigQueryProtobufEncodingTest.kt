/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.bigqueryv2

import com.fasterxml.jackson.databind.JsonNode
import com.google.cloud.bigquery.Field
import com.google.cloud.bigquery.StandardSQLTypeName
import io.airbyte.cdk.data.JsonEncoder
import io.airbyte.cdk.discover.EmittedField
import io.airbyte.cdk.discover.FieldType
import io.airbyte.cdk.jdbc.BigDecimalFieldType
import io.airbyte.cdk.jdbc.BytesFieldType
import io.airbyte.cdk.jdbc.DoubleFieldType
import io.airbyte.cdk.jdbc.JsonStringFieldType
import io.airbyte.cdk.jdbc.LongFieldType
import io.airbyte.cdk.jdbc.OffsetDateTimeFieldType
import io.airbyte.cdk.jdbc.PokemonFieldType
import io.airbyte.cdk.jdbc.StringFieldType
import io.airbyte.cdk.output.sockets.FieldValueEncoder
import io.airbyte.cdk.output.sockets.NativeRecordPayload
import io.airbyte.cdk.output.sockets.toJson
import io.airbyte.cdk.output.sockets.toProtobuf
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.protobuf.AirbyteRecordMessage.AirbyteRecordMessageProtobuf
import io.airbyte.protocol.protobuf.AirbyteRecordMessage.AirbyteValueProtobuf
import java.math.BigDecimal
import java.math.BigInteger
import java.nio.ByteBuffer
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.OffsetDateTime
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

/**
 * Every [FieldType] the connector assigns to a BigQuery column must be encodable on the protobuf
 * data channel (`DATA_CHANNEL_FORMAT=PROTOBUF`). The CDK encodes the native value held by a
 * [FieldValueEncoder] according to the field's `AirbyteSchemaType`; the connector-defined
 * [JsonNodeCodec] of `STRUCT`/`ARRAY` columns opts in through
 * `ProtobufAwareCustomConnectorJsonCodec`, the other types produce JVM values the CDK encodes
 * natively.
 */
class BigQueryProtobufEncodingTest {

    /** Encodes a one-column row with the CDK and decodes the protobuf value back. */
    private fun roundTrip(type: FieldType, value: Any?): Any? {
        val record: AirbyteRecordMessageProtobuf =
            encode(listOf(EmittedField("c", type)), mapOf("c" to value))
        return SpeedModeTestSupport.decode(record.getData(0))
    }

    private fun payload(
        fields: List<EmittedField>,
        values: Map<String, Any?>
    ): NativeRecordPayload =
        fields
            .associate { field ->
                @Suppress("UNCHECKED_CAST")
                field.id to
                    FieldValueEncoder(
                        values[field.id],
                        field.type.jsonEncoder as JsonEncoder<in Any?>
                    )
            }
            .toMutableMap()

    private fun encode(
        fields: List<EmittedField>,
        values: Map<String, Any?>
    ): AirbyteRecordMessageProtobuf {
        val builder: AirbyteRecordMessageProtobuf.Builder =
            AirbyteRecordMessageProtobuf.newBuilder()
        repeat(fields.size) { builder.addData(AirbyteValueProtobuf.newBuilder()) }
        return payload(fields, values)
            .toProtobuf(fields.toSet(), builder, AirbyteValueProtobuf.newBuilder())
            .build()
    }

    @Test
    fun testStructIsEncodedAsJsonText() {
        val type =
            BigQueryStructFieldType(
                fields =
                    listOf(
                        EmittedField("city", StringFieldType),
                        EmittedField("zip", LongFieldType)
                    )
            )
        val value: JsonNode = Jsons.readTree("""{"city":"Paris","zip":75001}""")
        val decoded: Any? = roundTrip(type, value)
        Assertions.assertInstanceOf(String::class.java, decoded)
        Assertions.assertEquals(value, Jsons.readTree(decoded as String))
    }

    @Test
    fun testArrayIsEncodedAsJsonText() {
        val type = BigQueryArrayFieldType(StringFieldType)
        val value: JsonNode = Jsons.readTree("""["a","b"]""")
        Assertions.assertEquals(value, Jsons.readTree(roundTrip(type, value) as String))
    }

    @Test
    fun testArrayOfStructsIsEncodedAsJsonText() {
        val type =
            BigQueryArrayFieldType(
                BigQueryStructFieldType(
                    fields =
                        listOf(
                            EmittedField("sku", StringFieldType),
                            EmittedField("qty", LongFieldType),
                            EmittedField("observed_at", BigQueryTimeFieldType),
                        )
                )
            )
        val value: JsonNode =
            Jsons.readTree("""[{"sku":"sku-1","qty":2,"observed_at":"08:00:00.000000"}]""")
        Assertions.assertEquals(value, Jsons.readTree(roundTrip(type, value) as String))
    }

    @Test
    fun testNullsAreEncodedAsProtobufNull() {
        Assertions.assertNull(roundTrip(BigQueryStructFieldType(fields = null), null))
        Assertions.assertNull(roundTrip(BigQueryStructFieldType(fields = null), Jsons.nullNode()))
        Assertions.assertNull(roundTrip(BigQueryArrayFieldType(LongFieldType), null))
        Assertions.assertNull(roundTrip(BigQueryDateFieldType, null))
        Assertions.assertNull(roundTrip(LongFieldType, null))
    }

    @Test
    fun testTextTemporalTypesKeepTheirPrecisionAndCalendar() {
        // Before the Gregorian cutover: the whole point of reading DATE/DATETIME as text.
        Assertions.assertEquals(
            LocalDate.of(1, 1, 1),
            roundTrip(BigQueryDateFieldType, LocalDate.of(1, 1, 1))
        )
        Assertions.assertEquals(
            LocalDate.parse("2021-10-20"),
            roundTrip(BigQueryDateFieldType, LocalDate.parse("2021-10-20"))
        )
        val dateTime = LocalDateTime.parse("2021-10-20T11:22:33.123456")
        Assertions.assertEquals(dateTime, roundTrip(BigQueryDateTimeFieldType, dateTime))
        // Microseconds, which the JDBC driver's java.sql.Time would have dropped.
        val time = LocalTime.parse("15:30:00.000001")
        Assertions.assertEquals(time, roundTrip(BigQueryTimeFieldType, time))
    }

    @Test
    fun testScalarTypesRoundTrip() {
        val timestamp = OffsetDateTime.parse("2021-10-20T11:22:33.123456Z")
        Assertions.assertEquals(timestamp, roundTrip(OffsetDateTimeFieldType, timestamp))
        Assertions.assertEquals(BigInteger.valueOf(42L), roundTrip(LongFieldType, 42L))
        Assertions.assertEquals(
            BigInteger.valueOf(Long.MIN_VALUE),
            roundTrip(LongFieldType, Long.MIN_VALUE)
        )
        Assertions.assertEquals(
            0,
            BigDecimal("0.25").compareTo(roundTrip(DoubleFieldType, 0.25) as BigDecimal)
        )
        Assertions.assertEquals(
            BigDecimal("12345678901234567890.123456789"),
            roundTrip(BigDecimalFieldType, BigDecimal("12345678901234567890.123456789"))
        )
        Assertions.assertEquals(true, roundTrip(BigQueryBooleanFieldType, true))
        Assertions.assertEquals("alice", roundTrip(StringFieldType, "alice"))
        Assertions.assertEquals("POINT(1 2)", roundTrip(PokemonFieldType, "POINT(1 2)"))
        // BYTES travel as base64 text, like on the STDIO channel.
        Assertions.assertEquals(
            "YWJj",
            roundTrip(BytesFieldType, ByteBuffer.wrap("abc".toByteArray()))
        )
        // JSON columns arrive from the driver as text and stay text on the wire.
        Assertions.assertEquals("""{"a":1}""", roundTrip(JsonStringFieldType, """{"a":1}"""))
    }

    /**
     * A row with every column kind of the emulator fixture's `all_types` table, typed with
     * [BigQueryFieldTypes.fromField] like at discovery: the protobuf channel must carry the same
     * values as the JSON channel, in catalog (alphabetical) field order.
     */
    @Test
    fun testFixtureRowMatchesJsonChannel() {
        fun field(name: String, type: StandardSQLTypeName, vararg sub: Field): Field =
            Field.newBuilder(name, type, *sub).setMode(Field.Mode.NULLABLE).build()
        fun repeated(name: String, type: StandardSQLTypeName, vararg sub: Field): Field =
            Field.newBuilder(name, type, *sub).setMode(Field.Mode.REPEATED).build()
        val schema: List<Field> =
            listOf(
                field("id", StandardSQLTypeName.INT64),
                field("name", StandardSQLTypeName.STRING),
                field("price", StandardSQLTypeName.NUMERIC),
                field("ratio", StandardSQLTypeName.FLOAT64),
                field("active", StandardSQLTypeName.BOOL),
                field("blob", StandardSQLTypeName.BYTES),
                field("day", StandardSQLTypeName.DATE),
                field("local_ts", StandardSQLTypeName.DATETIME),
                field("ts", StandardSQLTypeName.TIMESTAMP),
                field("tod", StandardSQLTypeName.TIME),
                field("geo", StandardSQLTypeName.GEOGRAPHY),
                field("doc", StandardSQLTypeName.JSON),
                field(
                    "address",
                    StandardSQLTypeName.STRUCT,
                    field("city", StandardSQLTypeName.STRING),
                    field(
                        "geo",
                        StandardSQLTypeName.STRUCT,
                        field("observed_at", StandardSQLTypeName.TIME)
                    ),
                ),
                repeated("tags", StandardSQLTypeName.STRING),
                repeated(
                    "line_items",
                    StandardSQLTypeName.STRUCT,
                    field("sku", StandardSQLTypeName.STRING),
                    field("qty", StandardSQLTypeName.INT64),
                ),
            )
        val fields: List<EmittedField> =
            schema.map { EmittedField(it.name, BigQueryFieldTypes.fromField(it)) }
        val values: Map<String, Any?> =
            mapOf(
                "id" to 1L,
                "name" to "alice",
                "price" to BigDecimal("1.5"),
                "ratio" to 0.25,
                "active" to true,
                "blob" to ByteBuffer.wrap("abc".toByteArray()),
                "day" to LocalDate.parse("2021-10-20"),
                "local_ts" to LocalDateTime.parse("2021-10-20T11:22:33"),
                "ts" to OffsetDateTime.parse("2021-10-20T11:22:33Z"),
                "tod" to LocalTime.parse("15:30:00"),
                "geo" to "POINT(1 2)",
                "doc" to """{"a":1}""",
                "address" to
                    Jsons.readTree("""{"city":"Paris","geo":{"observed_at":"08:00:00.000000"}}"""),
                "tags" to Jsons.readTree("""["a","b"]"""),
                "line_items" to null,
            )
        val record: AirbyteRecordMessageProtobuf = encode(fields, values)
        val expectedJson: JsonNode = payload(fields, values).toJson()

        val sorted: List<EmittedField> = fields.sortedBy { it.id }
        Assertions.assertEquals(sorted.size, record.dataCount)
        val actualJson = Jsons.objectNode()
        sorted.forEachIndexed { i, field ->
            actualJson.set<JsonNode>(
                field.id,
                SpeedModeTestSupport.protobufValueToJson(
                    SpeedModeTestSupport.decode(record.getData(i)),
                    BigQueryFieldTypes.jsonSchema(field.type),
                )
            )
        }
        Assertions.assertEquals(
            SpeedModeTestSupport.normalize(expectedJson),
            SpeedModeTestSupport.normalize(actualJson),
            actualJson.toString()
        )
    }
}
