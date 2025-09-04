/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse.write.transform

import io.airbyte.cdk.load.data.DateType
import io.airbyte.cdk.load.data.DateValue
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NumberType
import io.airbyte.cdk.load.data.NumberValue
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.TimestampTypeWithTimezone
import io.airbyte.cdk.load.data.TimestampWithTimezoneValue
import io.airbyte.cdk.load.dataflow.transform.FieldExtractionResult
import io.airbyte.cdk.load.dataflow.transform.ValidationContext
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import io.mockk.mockk
import java.math.BigDecimal
import java.math.BigInteger
import java.time.LocalDate
import java.time.OffsetDateTime
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test

class ClickhouseFieldValidatorTest {

    private val validator = ClickhouseFieldValidator()

    @Test
    fun `validates integer within range`() {
        val validInteger = IntegerValue(BigInteger.valueOf(123))
        val context = ValidationContext("test_field", IntegerType, mockk(), mockk())
        val result = FieldExtractionResult(validInteger, null)

        val validatedResult = validator.validate(context, result)

        assertNull(validatedResult.parsingError)
        assertNotNull(validatedResult.value)
        assertEquals(validInteger, validatedResult.value)
    }

    @Test
    fun `rejects integer exceeding max value`() {
        val oversizedInteger = IntegerValue(BigInteger.valueOf(Long.MAX_VALUE).add(BigInteger.ONE))
        val context = ValidationContext("test_field", IntegerType, mockk(), mockk())
        val result = FieldExtractionResult(oversizedInteger, null)

        val validatedResult = validator.validate(context, result)

        assertNotNull(validatedResult.parsingError)
        assertNull(validatedResult.value)
        assertEquals("test_field", validatedResult.parsingError!!.field)
        assertEquals(
            AirbyteRecordMessageMetaChange.Change.NULLED,
            validatedResult.parsingError!!.change
        )
        assertEquals(
            AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION,
            validatedResult.parsingError!!.reason
        )
    }

    @Test
    fun `validates number within range`() {
        val validNumber = NumberValue(BigDecimal.valueOf(123.45))
        val context = ValidationContext("test_field", NumberType, mockk(), mockk())
        val result = FieldExtractionResult(validNumber, null)

        val validatedResult = validator.validate(context, result)

        assertNull(validatedResult.parsingError)
        assertNotNull(validatedResult.value)
        assertEquals(validNumber, validatedResult.value)
    }

    @Test
    fun `rejects number exceeding max value`() {
        val oversizedNumber = NumberValue(ClickhouseCoercer.Constants.DECIMAL128_MAX)
        val context = ValidationContext("test_field", NumberType, mockk(), mockk())
        val result = FieldExtractionResult(oversizedNumber, null)

        val validatedResult = validator.validate(context, result)

        assertNotNull(validatedResult.parsingError)
        assertNull(validatedResult.value)
        assertEquals("test_field", validatedResult.parsingError!!.field)
        assertEquals(
            AirbyteRecordMessageMetaChange.Change.NULLED,
            validatedResult.parsingError!!.change
        )
        assertEquals(
            AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION,
            validatedResult.parsingError!!.reason
        )
    }

    @Test
    fun `validates date within range`() {
        val validDate = DateValue(LocalDate.of(2023, 6, 15))
        val context = ValidationContext("test_field", DateType, mockk(), mockk())
        val result = FieldExtractionResult(validDate, null)

        val validatedResult = validator.validate(context, result)

        assertNull(validatedResult.parsingError)
        assertNotNull(validatedResult.value)
        assertEquals(validDate, validatedResult.value)
    }

    @Test
    fun `rejects date outside valid range`() {
        val invalidDate = DateValue(LocalDate.of(1800, 1, 1)) // Before ClickHouse min date
        val context = ValidationContext("test_field", DateType, mockk(), mockk())
        val result = FieldExtractionResult(invalidDate, null)

        val validatedResult = validator.validate(context, result)

        assertNotNull(validatedResult.parsingError)
        assertNull(validatedResult.value)
        assertEquals("test_field", validatedResult.parsingError!!.field)
        assertEquals(
            AirbyteRecordMessageMetaChange.Change.NULLED,
            validatedResult.parsingError!!.change
        )
        assertEquals(
            AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION,
            validatedResult.parsingError!!.reason
        )
    }

    @Test
    fun `validates timestamp within range`() {
        val validTimestamp =
            TimestampWithTimezoneValue(OffsetDateTime.parse("2023-06-15T10:30:00Z"))
        val context = ValidationContext("test_field", TimestampTypeWithTimezone, mockk(), mockk())
        val result = FieldExtractionResult(validTimestamp, null)

        val validatedResult = validator.validate(context, result)

        assertNull(validatedResult.parsingError)
        assertNotNull(validatedResult.value)
        assertEquals(validTimestamp, validatedResult.value)
    }

    @Test
    fun `passes through non-validated types unchanged`() {
        val stringValue = StringValue("hello")
        val context = ValidationContext("test_field", StringType, mockk(), mockk())
        val result = FieldExtractionResult(stringValue, null)

        val validatedResult = validator.validate(context, result)

        assertNull(validatedResult.parsingError)
        assertNotNull(validatedResult.value)
        assertEquals(stringValue, validatedResult.value)
    }

    @Test
    fun `passes through null values unchanged`() {
        val context = ValidationContext("test_field", IntegerType, mockk(), mockk())
        val result = FieldExtractionResult(null, null)

        val validatedResult = validator.validate(context, result)

        assertNull(validatedResult.parsingError)
        assertNull(validatedResult.value)
    }

    @Test
    fun `preserves existing parsing errors`() {
        val context = ValidationContext("test_field", IntegerType, mockk(), mockk())
        val existingError =
            io.airbyte.cdk.load.message.Meta.Change(
                "test_field",
                AirbyteRecordMessageMetaChange.Change.NULLED,
                AirbyteRecordMessageMetaChange.Reason.SOURCE_SERIALIZATION_ERROR
            )
        val result = FieldExtractionResult(null, existingError)

        val validatedResult = validator.validate(context, result)

        assertNotNull(validatedResult.parsingError)
        assertNull(validatedResult.value)
        assertEquals(existingError, validatedResult.parsingError)
    }
}
