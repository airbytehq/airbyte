/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.bigqueryv2

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.discover.EmittedField
import io.airbyte.cdk.jdbc.BigDecimalFieldType
import io.airbyte.cdk.jdbc.BooleanFieldType
import io.airbyte.cdk.jdbc.BytesFieldType
import io.airbyte.cdk.jdbc.DoubleFieldType
import io.airbyte.cdk.jdbc.JsonStringFieldType
import io.airbyte.cdk.jdbc.LongFieldType
import io.airbyte.cdk.jdbc.OffsetDateTimeFieldType
import io.airbyte.cdk.jdbc.StringFieldType
import io.airbyte.cdk.util.Jsons
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

/** Conversion of `TO_JSON_STRING` output for STRUCT / ARRAY columns, as BigQuery renders it. */
class BigQueryValuesTest {

    private val discount =
        BigQueryStructFieldType(
            listOf(EmittedField("code", StringFieldType), EmittedField("pct", DoubleFieldType))
        )
    private val lineItem =
        BigQueryStructFieldType(
            listOf(
                EmittedField("sku", StringFieldType),
                EmittedField("qty", LongFieldType),
                EmittedField("price", BigDecimalFieldType),
                EmittedField("discounts", BigQueryArrayFieldType(discount)),
            )
        )
    private val address =
        BigQueryStructFieldType(
            listOf(
                EmittedField("city", StringFieldType),
                EmittedField("zip", LongFieldType),
                EmittedField("active", BooleanFieldType),
                EmittedField("observed_at", BigQueryTimeFieldType),
                EmittedField("on", BigQueryDateFieldType),
                EmittedField("local_ts", BigQueryDateTimeFieldType),
                EmittedField("ts", OffsetDateTimeFieldType),
                EmittedField("blob", BytesFieldType),
                EmittedField("geo", StringFieldType),
                EmittedField("doc", JsonStringFieldType),
                EmittedField("big", BigDecimalFieldType),
                EmittedField(
                    "inner",
                    BigQueryStructFieldType(listOf(EmittedField("a", StringFieldType)))
                ),
                EmittedField("items", BigQueryArrayFieldType(lineItem)),
            )
        )

    @Test
    fun testStructFromJsonText() {
        val text =
            """{"city":"Paris","zip":75001,"active":true,"observed_at":"08:00:00.000001","on":"0001-01-01",
               "local_ts":"0001-01-01T11:22:33.123456","ts":"2021-10-20T11:22:33.123456Z","blob":"YWJj",
               "geo":{"type":"Point","coordinates":[1,2]},"doc":{"a":[1,null]},
               "big":-0.00000000000000000000000000000000000001,"inner":null,
               "items":[{"sku":"sku-1","qty":2,"price":1.5,"discounts":[{"code":"SUMMER","pct":10.5}]},
                        {"sku":null,"qty":null,"price":null,"discounts":[]}]}"""
        val actual: JsonNode = BigQueryValues.fromJsonText(text, address.fields, null)
        // Numbers are compared as text: the converter keeps BigDecimal nodes (no double rounding),
        // Jsons.readTree would produce double nodes.
        Assertions.assertEquals(
            """{"city":"Paris","zip":75001,"active":true,"observed_at":"08:00:00.000001","on":"0001-01-01",""" +
                """"local_ts":"0001-01-01T11:22:33.123456","ts":"2021-10-20T11:22:33.123456Z","blob":"YWJj",""" +
                """"geo":"POINT(1 2)","doc":{"a":[1,null]},"big":-0.00000000000000000000000000000000000001,"inner":null,""" +
                """"items":[{"sku":"sku-1","qty":2,"price":1.5,"discounts":[{"code":"SUMMER","pct":10.5}]},""" +
                """{"sku":null,"qty":null,"price":null,"discounts":[]}]}""",
            Jsons.writeValueAsString(actual),
        )
        Assertions.assertEquals(
            "-0.00000000000000000000000000000000000001",
            actual["big"].decimalValue().toPlainString(),
        )
    }

    @Test
    fun testArrayFromJsonText() {
        val actual: JsonNode =
            BigQueryValues.fromJsonText(
                """["08:00:00","23:59:59.999999"]""",
                null,
                BigQueryTimeFieldType
            )
        Assertions.assertEquals(Jsons.readTree("""["08:00:00.000000","23:59:59.999999"]"""), actual)
        Assertions.assertEquals(
            Jsons.readTree("[]"),
            BigQueryValues.fromJsonText("[]", null, lineItem)
        )
    }

    @Test
    fun testEmulatorRenderingIsRepaired() {
        // goccy/bigquery-emulator output for the same struct: temporals unquoted, BOOL as 1.
        val emulatorText =
            """{"city":"Paris","zip":75001,"active":1,"observed_at":08:00:00.000001,"on":0001-01-01,""" +
                """"local_ts":0001-01-01T11:22:33.123456,"ts":2021-10-20T11:22:33Z,"blob":"YWJj",""" +
                """"geo":"POINT(1 2)","doc":{"a":[1,null]},"big":-0.00000000000000000000000000000000000001,"inner":null,"items":[]}"""
        val actual: JsonNode = BigQueryValues.fromJsonText(emulatorText, address.fields, null)
        Assertions.assertEquals(
            """{"city":"Paris","zip":75001,"active":true,"observed_at":"08:00:00.000001","on":"0001-01-01",""" +
                """"local_ts":"0001-01-01T11:22:33.123456","ts":"2021-10-20T11:22:33.000000Z","blob":"YWJj",""" +
                """"geo":"POINT(1 2)","doc":{"a":[1,null]},"big":-0.00000000000000000000000000000000000001,"inner":null,"items":[]}""",
            Jsons.writeValueAsString(actual),
        )
        Assertions.assertEquals(
            """{"t":"08:00:00","times":["08:00:00.000001","09:00:00"],"s":"x,2021-10-20"}""",
            BigQueryValues.quoteBareTemporals(
                """{"t":08:00:00,"times":[08:00:00.000001,09:00:00],"s":"x,2021-10-20"}"""
            ),
        )
    }

    @Test
    fun testGeoJsonToWkt() {
        Assertions.assertEquals(
            "POINT(1.5 -2)",
            GeoJson.toWkt(Jsons.readTree("""{"type":"Point","coordinates":[1.5,-2.0]}"""))
        )
        Assertions.assertEquals(
            "LINESTRING(0 0, 1 1)",
            GeoJson.toWkt(Jsons.readTree("""{"type":"LineString","coordinates":[[0,0],[1,1]]}"""))
        )
        Assertions.assertEquals(
            "POLYGON((0 0, 1 0, 1 1, 0 0), (0.2 0.2, 0.4 0.2, 0.2 0.4, 0.2 0.2))",
            GeoJson.toWkt(
                Jsons.readTree(
                    """{"type":"Polygon","coordinates":[[[0,0],[1,0],[1,1],[0,0]],[[0.2,0.2],[0.4,0.2],[0.2,0.4],[0.2,0.2]]]}"""
                )
            )
        )
        Assertions.assertEquals(
            "MULTIPOINT(1 2, 3 4)",
            GeoJson.toWkt(Jsons.readTree("""{"type":"MultiPoint","coordinates":[[1,2],[3,4]]}"""))
        )
        Assertions.assertEquals(
            "GEOMETRYCOLLECTION(POINT(1 2), LINESTRING(0 0, 1 1))",
            GeoJson.toWkt(
                Jsons.readTree(
                    """{"type":"GeometryCollection","geometries":[{"type":"Point","coordinates":[1,2]},{"type":"LineString","coordinates":[[0,0],[1,1]]}]}"""
                )
            )
        )
        Assertions.assertEquals(
            "GEOMETRYCOLLECTION EMPTY",
            GeoJson.toWkt(Jsons.readTree("""{"type":"GeometryCollection","geometries":[]}"""))
        )
    }
}
