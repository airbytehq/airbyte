/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.bigquery.readapi

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.data.JsonEncoder
import io.airbyte.cdk.discover.EmittedField
import io.airbyte.cdk.jdbc.BigDecimalFieldType
import io.airbyte.cdk.jdbc.BytesFieldType
import io.airbyte.cdk.jdbc.JsonStringFieldType
import io.airbyte.cdk.jdbc.OffsetDateTimeFieldType
import io.airbyte.cdk.jdbc.StringFieldType
import io.airbyte.cdk.output.sockets.FieldValueEncoder
import io.airbyte.cdk.output.sockets.NativeRecordPayload
import io.airbyte.cdk.output.sockets.toJson
import io.airbyte.cdk.read.FieldValueChange
import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.source.bigquery.BigQueryArrayFieldType
import io.airbyte.integrations.source.bigquery.BigQueryBigNumericFieldType
import io.airbyte.integrations.source.bigquery.BigQueryBooleanFieldType
import io.airbyte.integrations.source.bigquery.BigQueryDateFieldType
import io.airbyte.integrations.source.bigquery.BigQueryDateTimeFieldType
import io.airbyte.integrations.source.bigquery.BigQueryDoubleFieldType
import io.airbyte.integrations.source.bigquery.BigQueryLongFieldType
import io.airbyte.integrations.source.bigquery.BigQueryStructFieldType
import io.airbyte.integrations.source.bigquery.BigQueryTimeFieldType
import io.airbyte.integrations.source.bigquery.BigQueryValues
import java.io.ByteArrayOutputStream
import java.math.BigDecimal
import java.nio.ByteBuffer
import java.nio.channels.Channels
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.OffsetDateTime
import org.apache.arrow.compression.CommonsCompressionFactory
import org.apache.arrow.memory.RootAllocator
import org.apache.arrow.vector.BigIntVector
import org.apache.arrow.vector.BitVector
import org.apache.arrow.vector.DateDayVector
import org.apache.arrow.vector.Decimal256Vector
import org.apache.arrow.vector.DecimalVector
import org.apache.arrow.vector.Float8Vector
import org.apache.arrow.vector.IntervalMonthDayNanoVector
import org.apache.arrow.vector.TimeMicroVector
import org.apache.arrow.vector.TimeStampMicroTZVector
import org.apache.arrow.vector.TimeStampMicroVector
import org.apache.arrow.vector.VarBinaryVector
import org.apache.arrow.vector.VarCharVector
import org.apache.arrow.vector.VectorLoader
import org.apache.arrow.vector.VectorSchemaRoot
import org.apache.arrow.vector.VectorUnloader
import org.apache.arrow.vector.complex.ListVector
import org.apache.arrow.vector.complex.StructVector
import org.apache.arrow.vector.compression.CompressionUtil
import org.apache.arrow.vector.ipc.ReadChannel
import org.apache.arrow.vector.ipc.WriteChannel
import org.apache.arrow.vector.ipc.message.ArrowRecordBatch
import org.apache.arrow.vector.ipc.message.MessageSerializer
import org.apache.arrow.vector.types.DateUnit
import org.apache.arrow.vector.types.FloatingPointPrecision
import org.apache.arrow.vector.types.IntervalUnit
import org.apache.arrow.vector.types.TimeUnit
import org.apache.arrow.vector.types.pojo.ArrowType
import org.apache.arrow.vector.types.pojo.Field
import org.apache.arrow.vector.types.pojo.FieldType
import org.apache.arrow.vector.types.pojo.Schema
import org.apache.arrow.vector.util.ByteArrayReadableSeekableByteChannel
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

/**
 * The Arrow decoding must produce, for every BigQuery type, the same value objects the JDBC path
 * produces, so that both paths serialize identically. The Arrow types and metadata here are the
 * ones the Storage Read API returned for the seeded typed table on the real service (2026-09-21);
 * the expected values are what the JDBC driver returns from the REST API for the same rows.
 */
class BigQueryArrowRecordDecoderTest {

    private val allocator = RootAllocator()

    @AfterEach
    fun close() {
        allocator.close()
    }

    private fun field(
        name: String,
        type: ArrowType,
        children: List<Field> = emptyList(),
        metadata: Map<String, String>? = null,
        nullable: Boolean = true,
    ): Field = Field(name, FieldType(nullable, type, null, metadata), children)

    private val int64 = ArrowType.Int(64, true)
    private val utf8 = ArrowType.Utf8()
    private val float64 = ArrowType.FloatingPoint(FloatingPointPrecision.DOUBLE)
    private val dateDay = ArrowType.Date(DateUnit.DAY)
    private val timeMicro = ArrowType.Time(TimeUnit.MICROSECOND, 64)
    private val datetimeMeta = mapOf("ARROW:extension:name" to "google:sqlType:datetime")
    private val jsonMeta = mapOf("ARROW:extension:name" to "google:sqlType:json")
    private val geoMeta =
        mapOf(
            "ARROW:extension:name" to "google:sqlType:geography",
            "ARROW:extension:metadata" to """{"encoding": "WKT"}"""
        )
    private val intervalMeta = mapOf("ARROW:extension:name" to "google:sqlType:interval")
    private val rangeMeta = mapOf("google:sqlType" to "range")

    private fun encode(fields: List<EmittedField>, values: Map<String, Any?>): JsonNode {
        val payload: NativeRecordPayload = mutableMapOf()
        for (f in fields) {
            @Suppress("UNCHECKED_CAST")
            payload[f.id] =
                FieldValueEncoder(values[f.id], f.type.jsonEncoder as JsonEncoder<in Any?>)
        }
        return payload.toJson()
    }

    @Test
    fun testTopLevelScalarsMatchTheJdbcValues() {
        val schema =
            Schema(
                listOf(
                    field("id", int64, nullable = false),
                    field("name", utf8),
                    field("price", ArrowType.Decimal(29, 9, 128)),
                    field("big", ArrowType.Decimal(76, 38, 256)),
                    field("ratio", float64),
                    field("active", ArrowType.Bool()),
                    field("blob", ArrowType.Binary()),
                    field("day", dateDay),
                    field(
                        "local_ts",
                        ArrowType.Timestamp(TimeUnit.MICROSECOND, null),
                        metadata = datetimeMeta
                    ),
                    field("ts", ArrowType.Timestamp(TimeUnit.MICROSECOND, "UTC")),
                    field("tod", timeMicro),
                    field("geo", utf8, metadata = geoMeta),
                    field("doc", utf8, metadata = jsonMeta),
                    field(
                        "span",
                        ArrowType.Interval(IntervalUnit.MONTH_DAY_NANO),
                        metadata = intervalMeta
                    ),
                    field(
                        "dr",
                        ArrowType.Struct(),
                        listOf(field("start", dateDay), field("end", dateDay)),
                        metadata = rangeMeta
                    ),
                )
            )
        val fields: List<EmittedField> =
            listOf(
                EmittedField("id", BigQueryLongFieldType),
                EmittedField("name", StringFieldType),
                EmittedField("price", BigDecimalFieldType),
                EmittedField("big", BigQueryBigNumericFieldType),
                EmittedField("ratio", BigQueryDoubleFieldType),
                EmittedField("active", BigQueryBooleanFieldType),
                EmittedField("blob", BytesFieldType),
                EmittedField("day", BigQueryDateFieldType),
                EmittedField("local_ts", BigQueryDateTimeFieldType),
                EmittedField("ts", OffsetDateTimeFieldType),
                EmittedField("tod", BigQueryTimeFieldType),
                EmittedField("geo", StringFieldType),
                EmittedField("doc", JsonStringFieldType),
                EmittedField("span", StringFieldType),
                EmittedField("dr", StringFieldType),
            )
        VectorSchemaRoot.create(schema, allocator).use { root ->
            root.allocateNew()
            val bytes = byteArrayOf(0, 1, 2, -1, -2) + "hello".toByteArray()
            // Row 0: the seeded row 1 (every value set), row 1: all NULL, row 2: extremes.
            (root.getVector("id") as BigIntVector).apply {
                setSafe(0, 1L)
                setSafe(1, 2L)
                setSafe(2, 3L)
            }
            (root.getVector("name") as VarCharVector).apply {
                setSafe(0, "ascii and unicode: café🚀".toByteArray())
                setNull(1)
                setSafe(2, ByteArray(0))
            }
            (root.getVector("price") as DecimalVector).apply {
                setSafe(0, BigDecimal("12345.678900000"))
                setNull(1)
                setSafe(2, BigDecimal("-99999999999999999999.999999999"))
            }
            (root.getVector("big") as Decimal256Vector).apply {
                setSafe(
                    0,
                    BigDecimal(
                        "-99999999999999999999999999999999999999.99999999999999999999999999999999999999"
                    )
                )
                setNull(1)
                setSafe(2, BigDecimal("1E-38").setScale(38))
            }
            (root.getVector("ratio") as Float8Vector).apply {
                setSafe(0, 1.9500000000001)
                setNull(1)
                setSafe(2, 3.141592653589793)
            }
            (root.getVector("active") as BitVector).apply {
                setSafe(0, 1)
                setNull(1)
                setSafe(2, 0)
            }
            (root.getVector("blob") as VarBinaryVector).apply {
                setSafe(0, bytes)
                setNull(1)
                setSafe(2, ByteArray(0))
            }
            (root.getVector("day") as DateDayVector).apply {
                setSafe(0, 19550)
                setNull(1)
                setSafe(2, -719162)
            }
            (root.getVector("local_ts") as TimeStampMicroVector).apply {
                setSafe(0, 1689139119531834L)
                setNull(1)
                setSafe(2, 253402300799999999L)
            }
            (root.getVector("ts") as TimeStampMicroTZVector).apply {
                setSafe(0, 1689139119531834L)
                setNull(1)
                setSafe(2, -62135596800000000L)
            }
            (root.getVector("tod") as TimeMicroVector).apply {
                setSafe(0, 55800000001L)
                setNull(1)
                setSafe(2, 0L)
            }
            (root.getVector("geo") as VarCharVector).apply {
                setSafe(0, "POINT(-122.35 47.62)".toByteArray())
                setNull(1)
                setSafe(2, "LINESTRING(0 0, 1 1)".toByteArray())
            }
            (root.getVector("doc") as VarCharVector).apply {
                setSafe(0, """{"a":1,"b":[true,null,"x"],"n":3.14}""".toByteArray())
                setNull(1)
                setSafe(2, "null".toByteArray())
            }
            (root.getVector("span") as IntervalMonthDayNanoVector).apply {
                setSafe(0, 14, 3, 4L * 3_600_000_000_000L + 5L * 60_000_000_000L + 6_789_000_000L)
                setNull(1)
                setSafe(2, 0, -5, 0L)
            }
            (root.getVector("dr") as StructVector).apply {
                val start = getChild("start") as DateDayVector
                val end = getChild("end") as DateDayVector
                start.setSafe(0, 18262)
                end.setSafe(0, 18627)
                setIndexDefined(0)
                setNull(1)
                start.setNull(2)
                end.setSafe(2, 18628)
                setIndexDefined(2)
            }
            root.rowCount = 3

            val decoder = BigQueryArrowRecordDecoder(root, fields)
            val payload: NativeRecordPayload = mutableMapOf()
            val changes = mutableMapOf<EmittedField, FieldValueChange>()

            decoder.decode(0, payload, changes)
            Assertions.assertTrue(changes.isEmpty(), changes.toString())
            val expectedRow0: JsonNode =
                encode(
                    fields,
                    mapOf(
                        "id" to 1L,
                        "name" to "ascii and unicode: café🚀",
                        // The REST API returns NUMERIC/BIGNUMERIC as canonical text: no trailing
                        // zeros.
                        "price" to BigDecimal("12345.6789"),
                        "big" to
                            BigDecimal(
                                "-99999999999999999999999999999999999999.99999999999999999999999999999999999999"
                            ),
                        "ratio" to 1.9500000000001,
                        "active" to true,
                        "blob" to ByteBuffer.wrap(bytes),
                        "day" to LocalDate.parse("2023-07-12"),
                        "local_ts" to LocalDateTime.parse("2023-07-12T05:18:39.531834"),
                        "ts" to OffsetDateTime.parse("2023-07-12T05:18:39.531834Z"),
                        "tod" to LocalTime.parse("15:30:00.000001"),
                        "geo" to "POINT(-122.35 47.62)",
                        "doc" to """{"a":1,"b":[true,null,"x"],"n":3.14}""",
                        "span" to "1-2 3 4:5:6.789",
                        "dr" to "[2020-01-01, 2020-12-31)",
                    )
                )
            Assertions.assertEquals(
                Jsons.writeValueAsString(expectedRow0),
                Jsons.writeValueAsString(payload.toJson())
            )
            Assertions.assertEquals(expectedRow0, payload.toJson())

            decoder.decode(1, payload, changes)
            Assertions.assertTrue(changes.isEmpty(), changes.toString())
            val expectedNulls: JsonNode = encode(fields, mapOf("id" to 2L))
            Assertions.assertEquals(
                Jsons.writeValueAsString(expectedNulls),
                Jsons.writeValueAsString(payload.toJson())
            )

            decoder.decode(2, payload, changes)
            Assertions.assertTrue(changes.isEmpty(), changes.toString())
            val expectedRow2: JsonNode =
                encode(
                    fields,
                    mapOf(
                        "id" to 3L,
                        "name" to "",
                        "price" to BigDecimal("-99999999999999999999.999999999"),
                        "big" to BigDecimal("1E-38"),
                        "ratio" to 3.141592653589793,
                        "active" to false,
                        "blob" to ByteBuffer.wrap(ByteArray(0)),
                        // Proleptic Gregorian, unlike the JDBC driver's java.sql.Date (0001-01-03).
                        "day" to LocalDate.parse("0001-01-01"),
                        "local_ts" to LocalDateTime.parse("9999-12-31T23:59:59.999999"),
                        "ts" to OffsetDateTime.parse("0001-01-01T00:00:00Z"),
                        "tod" to LocalTime.parse("00:00:00"),
                        "geo" to "LINESTRING(0 0, 1 1)",
                        "doc" to "null",
                        "span" to "0-0 -5 0:0:0",
                        "dr" to "[UNBOUNDED, 2021-01-01)",
                    )
                )
            Assertions.assertEquals(
                Jsons.writeValueAsString(expectedRow2),
                Jsons.writeValueAsString(payload.toJson())
            )
        }
    }

    /**
     * Nested values must equal what the JDBC path derives from `TO_JSON_STRING`: the JSON texts
     * here are what BigQuery renders for these values (verified on the real service), and the
     * expected node is [BigQueryValues.fromJsonText] of that text.
     */
    @Test
    fun testNestedValuesMatchTheToJsonStringRendering() {
        val geoStruct =
            BigQueryStructFieldType(listOf(EmittedField("observed_at", BigQueryTimeFieldType)))
        val addressType =
            BigQueryStructFieldType(
                listOf(
                    EmittedField("city", StringFieldType),
                    EmittedField("zip", BigQueryLongFieldType),
                    EmittedField("geo", geoStruct),
                )
            )
        val lineItemType =
            BigQueryStructFieldType(
                listOf(
                    EmittedField("sku", StringFieldType),
                    EmittedField("qty", BigQueryLongFieldType)
                )
            )
        val mixType =
            BigQueryStructFieldType(
                listOf(
                    EmittedField("n", BigDecimalFieldType),
                    EmittedField("n_int", BigDecimalFieldType),
                    EmittedField("f", BigQueryDoubleFieldType),
                    EmittedField("f_big", BigQueryDoubleFieldType),
                    EmittedField("f_small", BigQueryDoubleFieldType),
                    EmittedField("f_frac", BigQueryDoubleFieldType),
                    EmittedField("i", StringFieldType),
                    EmittedField("r", StringFieldType),
                    EmittedField("b", BytesFieldType),
                    EmittedField("t", OffsetDateTimeFieldType),
                    EmittedField("d", BigQueryDateFieldType),
                    EmittedField("dt", BigQueryDateTimeFieldType),
                    EmittedField("j", JsonStringFieldType),
                    EmittedField("ok", BigQueryBooleanFieldType),
                    EmittedField("g", StringFieldType),
                )
            )
        val schema =
            Schema(
                listOf(
                    field(
                        "address",
                        ArrowType.Struct(),
                        listOf(
                            field("city", utf8),
                            field("zip", int64),
                            field(
                                "geo",
                                ArrowType.Struct(),
                                listOf(field("observed_at", timeMicro))
                            ),
                        ),
                    ),
                    field("tags", ArrowType.List(), listOf(field("item", utf8))),
                    field(
                        "line_items",
                        ArrowType.List(),
                        listOf(
                            field(
                                "item",
                                ArrowType.Struct(),
                                listOf(field("sku", utf8), field("qty", int64))
                            )
                        ),
                    ),
                    field(
                        "mix",
                        ArrowType.Struct(),
                        listOf(
                            field("n", ArrowType.Decimal(38, 9, 128)),
                            field("n_int", ArrowType.Decimal(38, 9, 128)),
                            field("f", float64),
                            field("f_big", float64),
                            field("f_small", float64),
                            field("f_frac", float64),
                            field(
                                "i",
                                ArrowType.Interval(IntervalUnit.MONTH_DAY_NANO),
                                metadata = intervalMeta
                            ),
                            field(
                                "r",
                                ArrowType.Struct(),
                                listOf(field("start", dateDay), field("end", dateDay)),
                                metadata = rangeMeta
                            ),
                            field("b", ArrowType.Binary()),
                            field("t", ArrowType.Timestamp(TimeUnit.MICROSECOND, "UTC")),
                            field("d", dateDay),
                            field(
                                "dt",
                                ArrowType.Timestamp(TimeUnit.MICROSECOND, null),
                                metadata = datetimeMeta
                            ),
                            field("j", utf8, metadata = jsonMeta),
                            field("ok", ArrowType.Bool()),
                            field("g", utf8, metadata = geoMeta),
                        ),
                    ),
                )
            )
        VectorSchemaRoot.create(schema, allocator).use { root ->
            root.allocateNew()
            val address = root.getVector("address") as StructVector
            (address.getChild("city") as VarCharVector).setSafe(0, "Seattle".toByteArray())
            (address.getChild("zip") as BigIntVector).setSafe(0, 98109L)
            val geo = address.getChild("geo") as StructVector
            (geo.getChild("observed_at") as TimeMicroVector).setSafe(0, 28800000001L)
            geo.setIndexDefined(0)
            address.setIndexDefined(0)
            // Row 1: a NULL struct; row 2: a struct of NULLs with an inner struct of NULL.
            address.setNull(1)
            (address.getChild("city") as VarCharVector).setNull(2)
            (address.getChild("zip") as BigIntVector).setNull(2)
            (geo.getChild("observed_at") as TimeMicroVector).setNull(2)
            geo.setIndexDefined(2)
            address.setIndexDefined(2)

            val tags = root.getVector("tags") as ListVector
            val tagData = tags.dataVector as VarCharVector
            var offset = tags.startNewValue(0)
            tagData.setSafe(offset, "a".toByteArray())
            tagData.setSafe(offset + 1, "b".toByteArray())
            tagData.setSafe(offset + 2, ByteArray(0))
            tags.endValue(0, 3)
            tags.startNewValue(1)
            tags.endValue(1, 0)
            offset = tags.startNewValue(2)
            tagData.setSafe(offset, "x".toByteArray())
            tags.endValue(2, 1)

            val items = root.getVector("line_items") as ListVector
            val itemData = items.dataVector as StructVector
            offset = items.startNewValue(0)
            (itemData.getChild("sku") as VarCharVector).setSafe(offset, "sku1".toByteArray())
            (itemData.getChild("qty") as BigIntVector).setSafe(offset, 2L)
            itemData.setIndexDefined(offset)
            (itemData.getChild("sku") as VarCharVector).setSafe(offset + 1, "sku2".toByteArray())
            (itemData.getChild("qty") as BigIntVector).setSafe(offset + 1, 0L)
            itemData.setIndexDefined(offset + 1)
            items.endValue(0, 2)
            items.startNewValue(1)
            items.endValue(1, 0)
            offset = items.startNewValue(2)
            (itemData.getChild("sku") as VarCharVector).setNull(offset)
            (itemData.getChild("qty") as BigIntVector).setNull(offset)
            itemData.setIndexDefined(offset)
            items.endValue(2, 1)

            val mix = root.getVector("mix") as StructVector
            (mix.getChild("n") as DecimalVector).setSafe(0, BigDecimal("12345.678900000"))
            (mix.getChild("n_int") as DecimalVector).setSafe(0, BigDecimal("100.000000000"))
            (mix.getChild("f") as Float8Vector).setSafe(0, 100.0)
            (mix.getChild("f_big") as Float8Vector).setSafe(0, 1e20)
            (mix.getChild("f_small") as Float8Vector).setSafe(0, 1e-7)
            (mix.getChild("f_frac") as Float8Vector).setSafe(0, 1.9500000000001)
            (mix.getChild("i") as IntervalMonthDayNanoVector).setSafe(
                0,
                14,
                3,
                4L * 3_600_000_000_000L + 5L * 60_000_000_000L + 6_789_000_000L
            )
            val range = mix.getChild("r") as StructVector
            (range.getChild("start") as DateDayVector).setSafe(0, 18262)
            (range.getChild("end") as DateDayVector).setNull(0)
            range.setIndexDefined(0)
            (mix.getChild("b") as VarBinaryVector).setSafe(0, byteArrayOf(0, 1, 2))
            (mix.getChild("t") as TimeStampMicroTZVector).setSafe(0, 1689139119531834L)
            (mix.getChild("d") as DateDayVector).setSafe(0, 19550)
            (mix.getChild("dt") as TimeStampMicroVector).setSafe(0, 1689139119531834L)
            (mix.getChild("j") as VarCharVector).setSafe(0, """{"a":1,"n":3.14}""".toByteArray())
            (mix.getChild("ok") as BitVector).setSafe(0, 1)
            (mix.getChild("g") as VarCharVector).setSafe(0, "LINESTRING(0 0, 1 1)".toByteArray())
            mix.setIndexDefined(0)
            mix.setNull(1)
            mix.setNull(2)
            root.rowCount = 3

            fun actual(name: String, row: Int, type: io.airbyte.cdk.discover.FieldType): JsonNode =
                BigQueryArrowValues.toJson(root.getVector(name), row, type)

            fun expected(text: String, type: io.airbyte.cdk.discover.FieldType): JsonNode =
                when (type) {
                    is BigQueryStructFieldType ->
                        BigQueryValues.fromJsonText(text, type.fields, null)
                    is BigQueryArrayFieldType ->
                        BigQueryValues.fromJsonText(text, null, type.elementType)
                    else -> throw IllegalArgumentException()
                }

            fun check(
                name: String,
                row: Int,
                type: io.airbyte.cdk.discover.FieldType,
                toJsonStringText: String
            ) {
                val e: JsonNode = expected(toJsonStringText, type)
                val a: JsonNode = actual(name, row, type)
                Assertions.assertEquals(
                    Jsons.writeValueAsString(e),
                    Jsons.writeValueAsString(a),
                    "$name row $row"
                )
                Assertions.assertEquals(e, a, "$name row $row")
            }

            check(
                "address",
                0,
                addressType,
                """{"city":"Seattle","zip":98109,"geo":{"observed_at":"08:00:00.000001"}}"""
            )
            check("address", 1, addressType, "null")
            check(
                "address",
                2,
                addressType,
                """{"city":null,"zip":null,"geo":{"observed_at":null}}"""
            )
            check("tags", 0, BigQueryArrayFieldType(StringFieldType), """["a","b",""]""")
            check("tags", 1, BigQueryArrayFieldType(StringFieldType), "[]")
            check("tags", 2, BigQueryArrayFieldType(StringFieldType), """["x"]""")
            check(
                "line_items",
                0,
                BigQueryArrayFieldType(lineItemType),
                """[{"sku":"sku1","qty":2},{"sku":"sku2","qty":0}]"""
            )
            check("line_items", 1, BigQueryArrayFieldType(lineItemType), "[]")
            check(
                "line_items",
                2,
                BigQueryArrayFieldType(lineItemType),
                """[{"sku":null,"qty":null}]"""
            )
            check(
                "mix",
                0,
                mixType,
                """{"n":"12345.6789","n_int":100,"f":100,"f_big":1e+20,"f_small":1e-07,"f_frac":1.9500000000001,
                    "i":"P1Y2M3DT4H5M6.789S","r":{"start":"2020-01-01","end":null},"b":"AAEC",
                    "t":"2023-07-12T05:18:39.531834Z","d":"2023-07-12","dt":"2023-07-12T05:18:39.531834",
                    "j":{"a":1,"n":3.14},"ok":true,"g":"LINESTRING(0 0, 1 1)"}""",
            )
            check("mix", 1, mixType, "null")
        }
    }

    /**
     * The reader loads every batch through `VectorLoader(root, CommonsCompressionFactory)`; a batch
     * compressed with the codecs the session requests (LZ4 frame by default, ZSTD as an option)
     * must decode to the same rows as an uncompressed one.
     */
    @Test
    fun testCompressedBatchesDecodeLikeUncompressedOnes() {
        val schema =
            Schema(
                listOf(
                    field("id", int64, nullable = false),
                    field("name", utf8),
                    field("ts", ArrowType.Timestamp(TimeUnit.MICROSECOND, "UTC")),
                    field("tags", ArrowType.List(), listOf(field("item", utf8))),
                )
            )
        val fields: List<EmittedField> =
            listOf(
                EmittedField("id", BigQueryLongFieldType),
                EmittedField("name", StringFieldType),
                EmittedField("ts", OffsetDateTimeFieldType),
                EmittedField("tags", BigQueryArrayFieldType(StringFieldType)),
            )
        val rows = 2_000
        for (codecType in
            listOf(CompressionUtil.CodecType.LZ4_FRAME, CompressionUtil.CodecType.ZSTD)) {
            VectorSchemaRoot.create(schema, allocator).use { source ->
                source.allocateNew()
                val ids = source.getVector("id") as BigIntVector
                val names = source.getVector("name") as VarCharVector
                val ts = source.getVector("ts") as TimeStampMicroTZVector
                val tags = source.getVector("tags") as ListVector
                val tagData = tags.dataVector as VarCharVector
                for (i in 0 until rows) {
                    ids.setSafe(i, i.toLong())
                    if (i % 7 == 0) names.setNull(i)
                    else names.setSafe(i, "name-$i-café".toByteArray())
                    ts.setSafe(i, 1689139119531834L + i)
                    val offset: Int = tags.startNewValue(i)
                    for (k in 0 until i % 3) tagData.setSafe(offset + k, "t$k".toByteArray())
                    tags.endValue(i, i % 3)
                }
                source.rowCount = rows

                // Serialize a compressed batch the way the Storage Read API ships one, then load
                // it.
                val codec = CommonsCompressionFactory.INSTANCE.createCodec(codecType)
                val batch: ArrowRecordBatch = VectorUnloader(source, true, codec, true).recordBatch
                val bytes = ByteArrayOutputStream()
                try {
                    MessageSerializer.serialize(WriteChannel(Channels.newChannel(bytes)), batch)
                } finally {
                    batch.close()
                }
                Assertions.assertTrue(bytes.size() > 0)

                VectorSchemaRoot.create(schema, allocator).use { target ->
                    val loaded: ArrowRecordBatch =
                        MessageSerializer.deserializeRecordBatch(
                            ReadChannel(ByteArrayReadableSeekableByteChannel(bytes.toByteArray())),
                            allocator,
                        )
                    try {
                        VectorLoader(target, CommonsCompressionFactory.INSTANCE).load(loaded)
                    } finally {
                        loaded.close()
                    }
                    Assertions.assertEquals(rows, target.rowCount, codecType.name)
                    val expected = BigQueryArrowRecordDecoder(source, fields)
                    val actual = BigQueryArrowRecordDecoder(target, fields)
                    val e: NativeRecordPayload = mutableMapOf()
                    val a: NativeRecordPayload = mutableMapOf()
                    val changes = mutableMapOf<EmittedField, FieldValueChange>()
                    for (i in 0 until rows) {
                        expected.decode(i, e, changes)
                        actual.decode(i, a, changes)
                        Assertions.assertEquals(
                            Jsons.writeValueAsString(e.toJson()),
                            Jsons.writeValueAsString(a.toJson()),
                            "$codecType row $i",
                        )
                    }
                    Assertions.assertEquals(
                        """{"id":5,"name":"name-5-café","ts":"2023-07-12T05:18:39.531839Z","tags":["t0","t1"]}""",
                        Jsons.writeValueAsString(
                            actual.also { it.decode(5, a, changes) }.let { a.toJson() }
                        ),
                    )
                }
            }
        }
    }

    @Test
    fun testTextRenderings() {
        Assertions.assertEquals(
            "1-2 3 4:5:6.789",
            BigQueryArrowValues.intervalText(14, 3, 14_706_789_000_000L)
        )
        Assertions.assertEquals(
            "-1-2 -3 -4:5:6.789012",
            BigQueryArrowValues.intervalText(-14, -3, -14_706_789_012_000L)
        )
        Assertions.assertEquals("0-0 -5 0:0:0", BigQueryArrowValues.intervalText(0, -5, 0))
        Assertions.assertEquals(
            "0-0 0 100:0:0",
            BigQueryArrowValues.intervalText(0, 0, 360_000_000_000_000L)
        )
        Assertions.assertEquals(
            "P1Y2M3DT4H5M6.789S",
            BigQueryArrowValues.intervalIsoText(14, 3, 14_706_789_000_000L)
        )
        Assertions.assertEquals(
            "P-1Y-2M-3DT-4H-5M-6.789012S",
            BigQueryArrowValues.intervalIsoText(-14, -3, -14_706_789_012_000L)
        )
        Assertions.assertEquals("P-5D", BigQueryArrowValues.intervalIsoText(0, -5, 0))
        Assertions.assertEquals(
            "PT100H",
            BigQueryArrowValues.intervalIsoText(0, 0, 360_000_000_000_000L)
        )
        Assertions.assertEquals("P0D", BigQueryArrowValues.intervalIsoText(0, 0, 0))
        Assertions.assertEquals(
            BigDecimal("12345.6789"),
            BigQueryArrowValues.normalizeDecimal(BigDecimal("12345.678900000"))
        )
        Assertions.assertEquals(
            BigDecimal("100"),
            BigQueryArrowValues.normalizeDecimal(BigDecimal("100.000000000"))
        )
        Assertions.assertEquals(
            "100",
            BigQueryArrowValues.normalizeDecimal(BigDecimal("100.000000000")).toString()
        )
        Assertions.assertEquals(
            BigDecimal("0"),
            BigQueryArrowValues.normalizeDecimal(BigDecimal("0.000000000"))
        )
        Assertions.assertEquals(
            "1E-38",
            BigQueryArrowValues.normalizeDecimal(BigDecimal("1E-38").setScale(38)).toString()
        )
        Assertions.assertEquals(
            "\"0.00000000000000000000000000000000000001\"",
            BigQueryArrowValues.nestedDecimalNode(BigDecimal("1E-38").setScale(38)).toString(),
        )
        Assertions.assertEquals(
            "100",
            BigQueryArrowValues.nestedDecimalNode(BigDecimal("100.000000000")).toString()
        )
    }
}
