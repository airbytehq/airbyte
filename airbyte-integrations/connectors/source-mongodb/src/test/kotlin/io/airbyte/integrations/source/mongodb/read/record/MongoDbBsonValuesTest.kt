/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodb.read.record

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.output.sockets.NativeRecordPayload
import io.airbyte.cdk.output.sockets.toJson
import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.source.mongodb.discover.MongoDbFieldType
import org.bson.BsonArray
import org.bson.BsonBinary
import org.bson.BsonBoolean
import org.bson.BsonDateTime
import org.bson.BsonDbPointer
import org.bson.BsonDecimal128
import org.bson.BsonDocument
import org.bson.BsonDouble
import org.bson.BsonInt32
import org.bson.BsonInt64
import org.bson.BsonJavaScriptWithScope
import org.bson.BsonMaxKey
import org.bson.BsonMinKey
import org.bson.BsonNull
import org.bson.BsonObjectId
import org.bson.BsonRegularExpression
import org.bson.BsonString
import org.bson.BsonUndefined
import org.bson.RawBsonDocument
import org.bson.codecs.BsonDocumentCodec
import org.bson.types.Decimal128
import org.bson.types.ObjectId
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

/** The one-pass BSON reading: what nested values become, and the two readers agreeing. */
class MongoDbBsonValuesTest {

    @Test
    fun testDroppedKindsAreOmittedInDocumentsAndNullInArrays() {
        val document =
            BsonDocument("_id", BsonInt32(1))
                .append(
                    "obj",
                    BsonDocument("keep", BsonInt32(1))
                        .append("min", BsonMinKey())
                        .append("max", BsonMaxKey())
                        .append("undef", BsonUndefined())
                        .append("ptr", BsonDbPointer("db.coll", ObjectId()))
                        .append("last", BsonString("x")),
                )
                .append(
                    "arr",
                    BsonArray(listOf(BsonInt32(1), BsonMinKey(), BsonUndefined(), BsonString("x"))),
                )
        val node: JsonNode = json(document)
        Assertions.assertEquals("""{"keep":1,"last":"x"}""", node["obj"].toString())
        Assertions.assertEquals("""[1,null,null,"x"]""", node["arr"].toString())
    }

    @Test
    fun testNestedSpecialTypesConvertLikeTopLevelOnes() {
        val document =
            BsonDocument("_id", BsonInt32(1))
                .append(
                    "obj",
                    BsonDocument("oid", BsonObjectId(ObjectId("650000000000000000000001")))
                        .append("date", BsonDateTime(1_704_067_200_000L))
                        .append("bin", BsonBinary(byteArrayOf(1, 2, 3)))
                        .append("re", BsonRegularExpression("^a", "i"))
                        .append("dec", BsonDecimal128(Decimal128.parse("1E+3")))
                        .append("long", BsonInt64(9_007_199_254_740_993L))
                        .append("bool", BsonBoolean(false))
                        .append("nil", BsonNull())
                        .append(
                            "code",
                            BsonJavaScriptWithScope("f()", BsonDocument("x", BsonInt32(1))),
                        ),
                )
        Assertions.assertEquals(
            """{"oid":"650000000000000000000001","date":"2024-01-01T00:00:00.000Z","bin":"AQID",""" +
                """"re":"(i)^a","dec":1000,"long":9007199254740993,"bool":false,"nil":null,""" +
                """"code":{"code":"f()","scope":{"x":1}}}""",
            json(document)["obj"].toString(),
        )
    }

    /**
     * NaN and the infinities have no JSON number: they are emitted as their names, in text. A
     * decimal negative zero keeps its sign as the double `-0.0`.
     */
    @Test
    fun testNonFiniteNumbersAreText() {
        val document =
            BsonDocument("_id", BsonInt32(1))
                .append("nan", BsonDouble(Double.NaN))
                .append("inf", BsonDouble(Double.POSITIVE_INFINITY))
                .append("decNan", BsonDecimal128(Decimal128.NaN))
                .append("decNegInf", BsonDecimal128(Decimal128.NEGATIVE_INFINITY))
                .append("negZero", BsonDecimal128(Decimal128.NEGATIVE_ZERO))
                .append(
                    "nested",
                    BsonDocument("nan", BsonDouble(Double.NaN))
                        .append("inf", BsonDecimal128(Decimal128.POSITIVE_INFINITY)),
                )
        val node: JsonNode = json(document)
        Assertions.assertEquals("NaN", node["nan"].asText())
        Assertions.assertEquals("Infinity", node["inf"].asText())
        Assertions.assertEquals("NaN", node["decNan"].asText())
        Assertions.assertEquals("-Infinity", node["decNegInf"].asText())
        Assertions.assertTrue(
            """"negZero":-0.0""" in Jsons.writeValueAsString(payloadOf(document).toJson()),
            "a decimal negative zero keeps its sign",
        )
        Assertions.assertEquals("""{"nan":"NaN","inf":"Infinity"}""", node["nested"].toString())
        // A `number` field holding one is nulled on protobuf rather than failing the sync.
        val payload: NativeRecordPayload =
            MongoDbRecordConverter(true, mapOf("nan" to MongoDbFieldType.NUMBER))
                .toPayload(document)
        Assertions.assertNull(
            MongoNumberValueCodec.valueForProtobufEncoding(
                payload.getValue("nan").fieldValue as MongoDbValue,
            ),
        )
    }

    /**
     * A value outside the catalog is skipped whatever its shape; the sources of transforms read.
     */
    @Test
    fun testFieldsOutsideTheCatalogAreSkipped() {
        val converter =
            MongoDbRecordConverter(
                schemaEnforced = true,
                schemaFieldTypes =
                    mapOf(
                        "_id" to MongoDbFieldType.NUMBER,
                        "kept" to MongoDbFieldType.STRING,
                        "n_aibyte_transform" to MongoDbFieldType.STRING,
                    ),
            )
        Assertions.assertEquals(
            setOf("_id", "kept", "n_aibyte_transform", "n"),
            converter.readFields,
        )
        val document =
            BsonDocument("_id", BsonInt32(1))
                .append("skipped", BsonDocument("deep", BsonArray(listOf(BsonDocument()))))
                .append("n", BsonDouble(2.5))
                .append("kept", BsonString("yes"))
                .append("alsoSkipped", BsonArray())
        val node: JsonNode = json(converter.toPayload(document))
        Assertions.assertEquals(
            setOf("_id", "kept", "n_aibyte_transform"),
            node.fieldNames().asSequence().toSet(),
        )
        Assertions.assertEquals("yes", node["kept"].asText())
        Assertions.assertEquals("2.5", node["n_aibyte_transform"].asText())
    }

    /** `_aibyte_transform` of a non-text scalar is its JSON text; of a BSON null, `null`. */
    @Test
    fun testTransformOfScalars() {
        val converter =
            MongoDbRecordConverter(
                schemaEnforced = true,
                schemaFieldTypes =
                    listOf("_id", "b_aibyte_transform", "n_aibyte_transform", "z_aibyte_transform")
                        .associateWith { MongoDbFieldType.STRING },
            )
        val node: JsonNode =
            json(
                converter.toPayload(
                    BsonDocument("_id", BsonInt32(1))
                        .append("b", BsonBoolean(true))
                        .append("n", BsonDecimal128(Decimal128.parse("12.340")))
                        .append("z", BsonNull()),
                ),
            )
        Assertions.assertEquals("true", node["b_aibyte_transform"].asText())
        Assertions.assertEquals("12.340", node["n_aibyte_transform"].asText())
        Assertions.assertEquals("null", node["z_aibyte_transform"].asText())
    }

    /** The schemaless `_id` is converted like a field; a document `_id` is its JSON. */
    @Test
    fun testSchemalessIdKinds() {
        val converter =
            MongoDbRecordConverter(
                schemaEnforced = false,
                mapOf("_id" to MongoDbFieldType.STRING, "data" to MongoDbFieldType.OBJECT),
            )
        val oid: JsonNode =
            json(
                converter.toPayload(
                    BsonDocument("_id", BsonObjectId(ObjectId("650000000000000000000001"))),
                ),
            )
        Assertions.assertEquals("650000000000000000000001", oid["_id"].asText())
        Assertions.assertEquals("650000000000000000000001", oid["data"]["_id"].asText())
        val composite: JsonNode =
            json(
                converter.toPayload(
                    BsonDocument(
                        "_id",
                        BsonDocument("tenant", BsonString("acme")).append("seq", BsonInt32(1)),
                    ),
                ),
            )
        Assertions.assertEquals("""{"tenant":"acme","seq":1}""", composite["_id"].toString())
    }

    /** The driver hands the readers raw bytes; the in-memory reader of the tests must agree. */
    @Test
    fun testRawAndDecodedDocumentsConvertIdentically() {
        val document =
            BsonDocument("_id", BsonObjectId(ObjectId("650000000000000000000001")))
                .append("s", BsonString("héllo \"quoted\" \n"))
                .append("n", BsonDecimal128(Decimal128.parse("12.34")))
                .append("d", BsonDouble(1.5))
                .append("l", BsonInt64(-7))
                .append(
                    "obj",
                    BsonDocument("date", BsonDateTime(0))
                        .append("arr", BsonArray(listOf(BsonInt32(1), BsonNull(), BsonMaxKey())))
                        .append("bin", BsonBinary(byteArrayOf(0, -1))),
                )
                .append("arr", BsonArray(listOf(BsonDocument("x", BsonInt32(1)), BsonString("y"))))
                .append("min", BsonMinKey())
        val raw = RawBsonDocument(document, BsonDocumentCodec())
        for (schemaEnforced in listOf(true, false)) {
            val types: Map<String, MongoDbFieldType> =
                if (schemaEnforced) {
                    document.keys.associateWith { MongoDbFieldType.STRING } +
                        mapOf("obj" to MongoDbFieldType.OBJECT, "arr" to MongoDbFieldType.ARRAY)
                } else {
                    mapOf("_id" to MongoDbFieldType.STRING, "data" to MongoDbFieldType.OBJECT)
                }
            val converter = MongoDbRecordConverter(schemaEnforced, types)
            Assertions.assertEquals(
                json(converter.toPayload(document)),
                json(converter.toPayload(raw)),
                "schemaEnforced=$schemaEnforced",
            )
        }
    }

    /** Converts with a schema of every top-level field (all `string`). */
    private fun json(document: BsonDocument): JsonNode = json(payloadOf(document))

    private fun payloadOf(document: BsonDocument): NativeRecordPayload =
        MongoDbRecordConverter(true, document.keys.associateWith { MongoDbFieldType.STRING })
            .toPayload(document)

    /** The payload as the JSON channel writes it. */
    private fun json(payload: NativeRecordPayload): JsonNode =
        Jsons.readTree(Jsons.writeValueAsBytes(payload.toJson()))
}
