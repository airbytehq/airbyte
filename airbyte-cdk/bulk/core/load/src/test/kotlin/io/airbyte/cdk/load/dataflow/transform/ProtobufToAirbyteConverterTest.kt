/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.transform

import io.airbyte.cdk.load.data.AirbyteValueProxy
import io.airbyte.cdk.load.data.BooleanType
import io.airbyte.cdk.load.data.BooleanValue
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.message.Meta
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import io.mockk.every
import io.mockk.mockk
import java.math.BigInteger
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test

class ProtobufToAirbyteConverterTest {

    @Test
    fun `extracts field without validator`() {
        val proxy = mockk<AirbyteValueProxy>()
        val accessor = mockk<AirbyteValueProxy.FieldAccessor>()

        every { accessor.name } returns "test_field"
        every { accessor.type } returns StringType
        every { proxy.getString(accessor) } returns "hello"

        val converter = ProtobufToAirbyteConverter()
        val result = converter.extractFieldWithValidation(proxy, accessor)

        assertNull(result.parsingError)
        assertNotNull(result.value)
        assertTrue(result.value is StringValue)
        assertEquals("hello", (result.value as StringValue).value)
    }

    @Test
    fun `extracts field with validator that passes`() {
        val proxy = mockk<AirbyteValueProxy>()
        val accessor = mockk<AirbyteValueProxy.FieldAccessor>()
        val validator = mockk<FieldValidator>()

        every { accessor.name } returns "test_field"
        every { accessor.type } returns BooleanType
        every { proxy.getBoolean(accessor) } returns true

        val extractionResult = FieldExtractionResult(BooleanValue(true), null)
        every { validator.validate(any(), extractionResult) } returns extractionResult

        val converter = ProtobufToAirbyteConverter(validator)
        val result = converter.extractFieldWithValidation(proxy, accessor)

        assertNull(result.parsingError)
        assertNotNull(result.value)
        assertTrue(result.value is BooleanValue)
        assertEquals(true, (result.value as BooleanValue).value)
    }

    @Test
    fun `extracts field with validator that rejects`() {
        val proxy = mockk<AirbyteValueProxy>()
        val accessor = mockk<AirbyteValueProxy.FieldAccessor>()
        val validator = mockk<FieldValidator>()

        every { accessor.name } returns "test_field"
        every { accessor.type } returns IntegerType
        every { proxy.getInteger(accessor) } returns BigInteger.valueOf(123)

        val originalResult = FieldExtractionResult(IntegerValue(BigInteger.valueOf(123)), null)
        val rejectedResult =
            FieldExtractionResult(
                null,
                Meta.Change(
                    "test_field",
                    AirbyteRecordMessageMetaChange.Change.NULLED,
                    AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION
                )
            )
        every { validator.validate(any(), originalResult) } returns rejectedResult

        val converter = ProtobufToAirbyteConverter(validator)
        val result = converter.extractFieldWithValidation(proxy, accessor)

        assertNotNull(result.parsingError)
        assertNull(result.value)
        assertEquals("test_field", result.parsingError!!.field)
        assertEquals(AirbyteRecordMessageMetaChange.Change.NULLED, result.parsingError!!.change)
        assertEquals(
            AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION,
            result.parsingError!!.reason
        )
    }

    @Test
    fun `handles extraction exception`() {
        val proxy = mockk<AirbyteValueProxy>()
        val accessor = mockk<AirbyteValueProxy.FieldAccessor>()

        every { accessor.name } returns "test_field"
        every { accessor.type } returns StringType
        every { proxy.getString(accessor) } throws RuntimeException("Extraction failed")

        val converter = ProtobufToAirbyteConverter()
        val result = converter.extractFieldWithValidation(proxy, accessor)

        assertNotNull(result.parsingError)
        assertNull(result.value)
        assertEquals("test_field", result.parsingError!!.field)
        assertEquals(AirbyteRecordMessageMetaChange.Change.NULLED, result.parsingError!!.change)
        assertEquals(
            AirbyteRecordMessageMetaChange.Reason.DESTINATION_SERIALIZATION_ERROR,
            result.parsingError!!.reason
        )
    }

    @Test
    fun `extracts null values correctly`() {
        val proxy = mockk<AirbyteValueProxy>()
        val accessor = mockk<AirbyteValueProxy.FieldAccessor>()

        every { accessor.name } returns "test_field"
        every { accessor.type } returns StringType
        every { proxy.getString(accessor) } returns null

        val converter = ProtobufToAirbyteConverter()
        val result = converter.extractFieldWithValidation(proxy, accessor)

        assertNull(result.parsingError)
        assertNull(result.value)
    }
}
