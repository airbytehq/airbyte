/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.write.transform

import com.fasterxml.jackson.databind.node.NullNode
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.ArrayType
import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.BooleanValue
import io.airbyte.cdk.load.data.EnrichedAirbyteValue
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.NumberType
import io.airbyte.cdk.load.data.NumberValue
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.UnionType
import io.airbyte.cdk.load.data.UnknownType
import io.airbyte.cdk.load.dataflow.transform.ValidationResult
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import java.math.BigDecimal
import java.math.BigInteger
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

internal class RedshiftValueCoercerTest {

    private lateinit var coercer: RedshiftValueCoercer

    @BeforeEach
    fun setUp() {
        coercer = RedshiftValueCoercer()
    }

    // ================================================================
    // map() tests
    // ================================================================

    @Test
    fun `map passes through non-union types unchanged`() {
        val value = StringValue("hello")
        val enriched = enriched(value, StringType)

        val result = coercer.map(enriched)

        assertEquals(value, result.abValue)
    }

    @Test
    fun `map serializes union type values to string`() {
        val value = ObjectValue(linkedMapOf("key" to StringValue("val")))
        val enriched =
            enriched(value, UnionType(options = setOf(StringType), isLegacyUnion = false))

        val result = coercer.map(enriched)

        assertTrue(result.abValue is StringValue)
        assertEquals(StringType, result.abValue.airbyteType)
    }

    @Test
    fun `map passes through unknown type values unchanged`() {
        val value = IntegerValue(42)
        val enriched = enriched(value, UnknownType(schema = NullNode.instance))

        val result = coercer.map(enriched)

        assertEquals(value, result.abValue)
    }

    @Test
    fun `map serializes legacy union type values to string`() {
        val value = ObjectValue(linkedMapOf("key" to StringValue("val")))
        val enriched = enriched(value, UnionType(options = setOf(StringType), isLegacyUnion = true))

        val result = coercer.map(enriched)

        assertTrue(result.abValue is StringValue)
    }

    @Test
    fun `map preserves NullValue for union types`() {
        val enriched =
            enriched(NullValue, UnionType(options = setOf(StringType), isLegacyUnion = false))

        val result = coercer.map(enriched)

        assertEquals(NullValue, result.abValue)
    }

    // ================================================================
    // validate() — Integer (BIGINT) tests
    // ================================================================

    @Test
    fun `validate accepts valid integer`() {
        val result = coercer.validate(enriched(IntegerValue(10000.toBigInteger()), IntegerType))
        assertEquals(ValidationResult.Valid, result)
    }

    @Test
    fun `validate accepts integer at BIGINT_MAX boundary`() {
        val result = coercer.validate(enriched(IntegerValue(BIGINT_MAX), IntegerType))
        assertEquals(ValidationResult.Valid, result)
    }

    @Test
    fun `validate accepts integer at BIGINT_MIN boundary`() {
        val result = coercer.validate(enriched(IntegerValue(BIGINT_MIN), IntegerType))
        assertEquals(ValidationResult.Valid, result)
    }

    @Test
    fun `validate nullifies integer above BIGINT_MAX`() {
        val result =
            coercer.validate(enriched(IntegerValue(BIGINT_MAX + BigInteger.ONE), IntegerType))
        assertShouldNullify(result)
    }

    @Test
    fun `validate nullifies integer below BIGINT_MIN`() {
        val result =
            coercer.validate(enriched(IntegerValue(BIGINT_MIN - BigInteger.ONE), IntegerType))
        assertShouldNullify(result)
    }

    @Test
    fun `validate accepts zero integer`() {
        val result = coercer.validate(enriched(IntegerValue(BigInteger.ZERO), IntegerType))
        assertEquals(ValidationResult.Valid, result)
    }

    // ================================================================
    // validate() — Number (NUMERIC) tests
    // ================================================================

    @Test
    fun `validate accepts valid number`() {
        val result = coercer.validate(enriched(NumberValue(BigDecimal("10000.123")), NumberType))
        assertEquals(ValidationResult.Valid, result)
    }

    @Test
    fun `validate nullifies number exceeding maximum`() {
        val result =
            coercer.validate(
                enriched(NumberValue(NUMERIC_MAX.multiply(BigDecimal.TEN)), NumberType)
            )
        assertShouldNullify(result)
    }

    @Test
    fun `validate nullifies number below minimum`() {
        val result =
            coercer.validate(
                enriched(NumberValue(NUMERIC_MIN.multiply(BigDecimal.TEN)), NumberType)
            )
        assertShouldNullify(result)
    }

    @Test
    fun `validate accepts zero number`() {
        val result = coercer.validate(enriched(NumberValue(BigDecimal.ZERO), NumberType))
        assertEquals(ValidationResult.Valid, result)
    }

    @Test
    fun `validate accepts very small positive number`() {
        val result =
            coercer.validate(enriched(NumberValue(BigDecimal("0.000000000001")), NumberType))
        assertEquals(ValidationResult.Valid, result)
    }

    @Test
    fun `validate accepts scientific notation number`() {
        val result = coercer.validate(enriched(NumberValue(BigDecimal("1.23E-10")), NumberType))
        assertEquals(ValidationResult.Valid, result)
    }

    // ================================================================
    // validate() — String (VARCHAR 65535 bytes) tests
    // ================================================================

    @Test
    fun `validate accepts short string`() {
        val result = coercer.validate(enriched(StringValue("hello"), StringType))
        assertEquals(ValidationResult.Valid, result)
    }

    @Test
    fun `validate accepts string at VARCHAR byte limit`() {
        val value = "a".repeat(VARCHAR_MAX_BYTES) // 65535 ASCII chars = 65535 bytes
        val result = coercer.validate(enriched(StringValue(value), StringType))
        assertEquals(ValidationResult.Valid, result)
    }

    @Test
    fun `validate nullifies string exceeding VARCHAR byte limit`() {
        val value = "a".repeat(VARCHAR_MAX_BYTES + 1) // 65536 ASCII chars = 65536 bytes
        val result = coercer.validate(enriched(StringValue(value), StringType))
        assertShouldNullify(result)
    }

    @Test
    fun `validate nullifies multi-byte string exceeding VARCHAR byte limit`() {
        // Each emoji is 4 bytes in UTF-8. 16384 emojis = 65536 bytes > 65535 limit.
        val value = "\uD83D\uDE00".repeat(16384)
        val result = coercer.validate(enriched(StringValue(value), StringType))
        assertShouldNullify(result)
    }

    @Test
    fun `validate accepts multi-byte string within VARCHAR byte limit`() {
        // Each 'é' is 2 bytes in UTF-8. 32000 chars = 64000 bytes < 65535 limit.
        val value = "é".repeat(32000)
        val result = coercer.validate(enriched(StringValue(value), StringType))
        assertEquals(ValidationResult.Valid, result)
    }

    // ================================================================
    // validate() — Object/Array (SUPER 16MB) tests
    // ================================================================

    @Test
    fun `validate accepts small object`() {
        val obj =
            ObjectValue(
                linkedMapOf(
                    "foo" to IntegerValue(1),
                    "bar" to IntegerValue(2),
                )
            )
        val result =
            coercer.validate(
                enriched(
                    obj,
                    ObjectType(
                        properties = linkedMapOf(),
                        additionalProperties = true,
                        required = emptyList(),
                    ),
                )
            )
        assertEquals(ValidationResult.Valid, result)
    }

    @Test
    fun `validate accepts small array`() {
        val arr = ArrayValue(listOf(IntegerValue(1), IntegerValue(2), IntegerValue(3)))
        val result = coercer.validate(enriched(arr, ArrayType(FieldType(IntegerType, false))))
        assertEquals(ValidationResult.Valid, result)
    }

    @Test
    fun `validate accepts deeply nested object`() {
        val deepObj =
            ObjectValue(
                linkedMapOf<String, AirbyteValue>(
                    "l1" to
                        ObjectValue(
                            linkedMapOf<String, AirbyteValue>(
                                "l2" to
                                    ObjectValue(
                                        linkedMapOf<String, AirbyteValue>(
                                            "l3" to StringValue("deep"),
                                        )
                                    ),
                            )
                        ),
                )
            )
        val result =
            coercer.validate(
                enriched(
                    deepObj,
                    ObjectType(
                        properties = linkedMapOf(),
                        additionalProperties = true,
                        required = emptyList(),
                    ),
                )
            )
        assertEquals(ValidationResult.Valid, result)
    }

    @Test
    fun `validate accepts large array under SUPER limit`() {
        val largeArray = ArrayValue((1..1000).map { IntegerValue(it.toBigInteger()) })
        val result =
            coercer.validate(enriched(largeArray, ArrayType(FieldType(IntegerType, false))))
        assertEquals(ValidationResult.Valid, result)
    }

    // ================================================================
    // validate() — SUPER nested string (VARCHAR 65535) tests
    // ================================================================

    @Test
    fun `validate nullifies object with nested string exceeding 65535 bytes`() {
        val obj =
            ObjectValue(
                linkedMapOf(
                    "id" to StringValue("abc-123"),
                    "signature" to StringValue("a".repeat(VARCHAR_MAX_BYTES + 1)),
                )
            )
        val result =
            coercer.validate(
                enriched(
                    obj,
                    ObjectType(
                        properties = linkedMapOf(),
                        additionalProperties = true,
                        required = emptyList(),
                    ),
                )
            )
        assertShouldNullify(result)
    }

    @Test
    fun `validate accepts object with nested string at exactly 65535 bytes`() {
        val obj =
            ObjectValue(
                linkedMapOf(
                    "id" to StringValue("abc-123"),
                    "data" to StringValue("a".repeat(VARCHAR_MAX_BYTES)),
                )
            )
        val result =
            coercer.validate(
                enriched(
                    obj,
                    ObjectType(
                        properties = linkedMapOf(),
                        additionalProperties = true,
                        required = emptyList(),
                    ),
                )
            )
        assertEquals(ValidationResult.Valid, result)
    }

    @Test
    fun `validate nullifies array with nested oversized string`() {
        val arr =
            ArrayValue(
                listOf(
                    StringValue("small"),
                    StringValue("a".repeat(70000)),
                )
            )
        val result = coercer.validate(enriched(arr, ArrayType(FieldType(StringType, false))))
        assertShouldNullify(result)
    }

    @Test
    fun `validate nullifies deeply nested object with oversized string`() {
        val deepObj =
            ObjectValue(
                linkedMapOf<String, AirbyteValue>(
                    "level1" to
                        ObjectValue(
                            linkedMapOf<String, AirbyteValue>(
                                "level2" to
                                    ObjectValue(
                                        linkedMapOf<String, AirbyteValue>(
                                            "huge" to
                                                StringValue("x".repeat(VARCHAR_MAX_BYTES + 1)),
                                        )
                                    ),
                            )
                        ),
                )
            )
        val result =
            coercer.validate(
                enriched(
                    deepObj,
                    ObjectType(
                        properties = linkedMapOf(),
                        additionalProperties = true,
                        required = emptyList(),
                    ),
                )
            )
        assertShouldNullify(result)
    }

    @Test
    fun `validate accepts object with only small values`() {
        val obj =
            ObjectValue(
                linkedMapOf(
                    "name" to StringValue("Alice"),
                    "count" to IntegerValue(42),
                    "active" to BooleanValue(true),
                    "tags" to ArrayValue(listOf(StringValue("a"), StringValue("b"))),
                )
            )
        val result =
            coercer.validate(
                enriched(
                    obj,
                    ObjectType(
                        properties = linkedMapOf(),
                        additionalProperties = true,
                        required = emptyList(),
                    ),
                )
            )
        assertEquals(ValidationResult.Valid, result)
    }

    @Test
    fun `validate nullifies object with multi-byte nested string over limit`() {
        // Each emoji is 4 bytes in UTF-8. 16384 emojis = 65536 bytes > 65535 limit.
        val obj =
            ObjectValue(
                linkedMapOf(
                    "data" to StringValue("\uD83D\uDE00".repeat(16384)),
                )
            )
        val result =
            coercer.validate(
                enriched(
                    obj,
                    ObjectType(
                        properties = linkedMapOf(),
                        additionalProperties = true,
                        required = emptyList(),
                    ),
                )
            )
        assertShouldNullify(result)
    }

    @Test
    fun `validate accepts object with multi-byte nested string under limit`() {
        // Each 'é' is 2 bytes in UTF-8. 32000 chars = 64000 bytes < 65535 limit.
        val obj =
            ObjectValue(
                linkedMapOf(
                    "data" to StringValue("é".repeat(32000)),
                )
            )
        val result =
            coercer.validate(
                enriched(
                    obj,
                    ObjectType(
                        properties = linkedMapOf(),
                        additionalProperties = true,
                        required = emptyList(),
                    ),
                )
            )
        assertEquals(ValidationResult.Valid, result)
    }

    // ================================================================
    // isSuperValid() — boundary tests
    // ================================================================

    @Test
    fun `isSuperValid accepts string at SUPER character limit`() {
        assertTrue(isSuperValid("a".repeat(SUPER_LIMIT_BYTES)))
    }

    @Test
    fun `isSuperValid rejects string exceeding SUPER character limit`() {
        assertEquals(false, isSuperValid("a".repeat(SUPER_LIMIT_BYTES + 1)))
    }

    // ================================================================
    // validate() — Other types
    // ================================================================

    @Test
    fun `validate accepts NullValue`() {
        val result = coercer.validate(enriched(NullValue, StringType))
        assertEquals(ValidationResult.Valid, result)
    }

    @Test
    fun `validate accepts BooleanValue`() {
        val result =
            coercer.validate(enriched(BooleanValue(true), io.airbyte.cdk.load.data.BooleanType))
        assertEquals(ValidationResult.Valid, result)
    }

    // ================================================================
    // Helpers
    // ================================================================

    private fun enriched(
        value: AirbyteValue,
        type: io.airbyte.cdk.load.data.AirbyteType,
    ): EnrichedAirbyteValue =
        EnrichedAirbyteValue(
            abValue = value,
            type = type,
            name = "test_field",
            changes = mutableListOf(),
            airbyteMetaField = null,
        )

    private fun assertShouldNullify(result: ValidationResult) {
        assertEquals(ValidationResult.ShouldNullify::class, result::class)
        assertEquals(
            AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION,
            (result as ValidationResult.ShouldNullify).reason,
        )
    }
}
