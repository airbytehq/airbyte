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
import io.airbyte.cdk.load.data.TimestampTypeWithTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithoutTimezone
import io.airbyte.cdk.load.data.TimestampWithTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithoutTimezoneValue
import io.airbyte.cdk.load.dataflow.transform.FieldExtractionResult
import io.airbyte.cdk.load.dataflow.transform.FieldValidator
import io.airbyte.cdk.load.dataflow.transform.ValidationContext
import io.airbyte.cdk.load.message.Meta
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import java.time.ZoneOffset

/**
 * ClickHouse-specific field validator that applies ClickHouse data type constraints during protobuf
 * to Airbyte value conversion.
 *
 */
class ClickhouseFieldValidator : FieldValidator {

    override fun validate(
        context: ValidationContext,
        extractedValue: FieldExtractionResult
    ): FieldExtractionResult {
        // If there's already a parsing error or null value, return as-is
        if (extractedValue.parsingError != null || extractedValue.value == null) {
            return extractedValue
        }

        return when (context.fieldType) {
            is IntegerType -> validateInteger(context, extractedValue)
            is NumberType -> validateNumber(context, extractedValue)
            is DateType -> validateDate(context, extractedValue)
            is TimestampTypeWithTimezone -> validateTimestampWithTimezone(context, extractedValue)
            is TimestampTypeWithoutTimezone ->
                validateTimestampWithoutTimezone(context, extractedValue)
            else -> extractedValue // No validation needed for other types
        }
    }

    private fun validateInteger(
        context: ValidationContext,
        result: FieldExtractionResult
    ): FieldExtractionResult {
        val integerValue = result.value as? IntegerValue ?: return result

        if (
            integerValue.value < ClickhouseCoercer.Constants.INT64_MIN ||
                integerValue.value > ClickhouseCoercer.Constants.INT64_MAX
        ) {
            return FieldExtractionResult(
                null,
                Meta.Change(
                    context.fieldName,
                    AirbyteRecordMessageMetaChange.Change.NULLED,
                    AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION
                )
            )
        }

        return result
    }

    private fun validateNumber(
        context: ValidationContext,
        result: FieldExtractionResult
    ): FieldExtractionResult {
        val numberValue = result.value as? NumberValue ?: return result

        if (
            numberValue.value <= ClickhouseCoercer.Constants.DECIMAL128_MIN ||
                numberValue.value >= ClickhouseCoercer.Constants.DECIMAL128_MAX
        ) {
            return FieldExtractionResult(
                null,
                Meta.Change(
                    context.fieldName,
                    AirbyteRecordMessageMetaChange.Change.NULLED,
                    AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION
                )
            )
        }

        return result
    }

    private fun validateDate(
        context: ValidationContext,
        result: FieldExtractionResult
    ): FieldExtractionResult {
        val dateValue = result.value as? DateValue ?: return result

        val days = dateValue.value.toEpochDay()
        if (
            days < ClickhouseCoercer.Constants.DATE32_MIN ||
                days > ClickhouseCoercer.Constants.DATE32_MAX
        ) {
            return FieldExtractionResult(
                null,
                Meta.Change(
                    context.fieldName,
                    AirbyteRecordMessageMetaChange.Change.NULLED,
                    AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION
                )
            )
        }

        return result
    }

    private fun validateTimestampWithTimezone(
        context: ValidationContext,
        result: FieldExtractionResult
    ): FieldExtractionResult {
        val timestampValue = result.value as? TimestampWithTimezoneValue ?: return result

        val seconds = timestampValue.value.toEpochSecond()
        if (
            seconds < ClickhouseCoercer.Constants.DATETIME64_MIN ||
                seconds > ClickhouseCoercer.Constants.DATETIME64_MAX
        ) {
            return FieldExtractionResult(
                null,
                Meta.Change(
                    context.fieldName,
                    AirbyteRecordMessageMetaChange.Change.NULLED,
                    AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION
                )
            )
        }

        return result
    }

    private fun validateTimestampWithoutTimezone(
        context: ValidationContext,
        result: FieldExtractionResult
    ): FieldExtractionResult {
        val timestampValue = result.value as? TimestampWithoutTimezoneValue ?: return result

        val seconds = timestampValue.value.toEpochSecond(ZoneOffset.UTC)
        if (
            seconds < ClickhouseCoercer.Constants.DATETIME64_MIN ||
                seconds > ClickhouseCoercer.Constants.DATETIME64_MAX
        ) {
            return FieldExtractionResult(
                null,
                Meta.Change(
                    context.fieldName,
                    AirbyteRecordMessageMetaChange.Change.NULLED,
                    AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION
                )
            )
        }

        return result
    }
}
