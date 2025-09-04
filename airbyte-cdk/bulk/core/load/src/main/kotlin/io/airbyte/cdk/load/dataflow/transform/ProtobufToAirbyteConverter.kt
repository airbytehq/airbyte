/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.transform

import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.AirbyteValueProxy
import io.airbyte.cdk.load.data.AirbyteValueProxy.FieldAccessor
import io.airbyte.cdk.load.data.ArrayType
import io.airbyte.cdk.load.data.BooleanType
import io.airbyte.cdk.load.data.BooleanValue
import io.airbyte.cdk.load.data.DateType
import io.airbyte.cdk.load.data.DateValue
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NumberType
import io.airbyte.cdk.load.data.NumberValue
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.TimeTypeWithTimezone
import io.airbyte.cdk.load.data.TimeTypeWithoutTimezone
import io.airbyte.cdk.load.data.TimeWithTimezoneValue
import io.airbyte.cdk.load.data.TimeWithoutTimezoneValue
import io.airbyte.cdk.load.data.TimestampTypeWithTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithoutTimezone
import io.airbyte.cdk.load.data.TimestampWithTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithoutTimezoneValue
import io.airbyte.cdk.load.data.UnionType
import io.airbyte.cdk.load.data.UnknownType
import io.airbyte.cdk.load.data.json.toAirbyteValue
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.util.serializeToString
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.OffsetDateTime
import java.time.OffsetTime

/**
 * Result of field extraction from protobuf, including the converted value and any parsing errors.
 */
data class FieldExtractionResult(val value: AirbyteValue?, val parsingError: Meta.Change?)

/** Context for field validation containing the field name, type, and raw value. */
data class ValidationContext(
    val fieldName: String,
    val fieldType: AirbyteType,
    val proxy: AirbyteValueProxy,
    val accessor: FieldAccessor
)

/**
 * Interface for destination-specific field validators. Implementations can apply
 * destination-specific validation logic like range checks, format validation, etc.
 */
interface FieldValidator {
    /**
     * Validates a field value and returns validation result.
     *
     * @param context The validation context containing field information
     * @param extractedValue The extracted value from protobuf conversion
     * @return FieldExtractionResult with potentially modified value or error
     */
    fun validate(
        context: ValidationContext,
        extractedValue: FieldExtractionResult
    ): FieldExtractionResult
}

/**
 * Reusable converter that extracts typed values from protobuf records and converts them to Airbyte
 * values. Supports destination-specific validation through the FieldValidator interface.
 */
class ProtobufToAirbyteConverter(private val fieldValidator: FieldValidator? = null) {

    /**
     * Extracts and converts a field value from protobuf to AirbyteValue with error handling.
     * Applies destination-specific validation if a validator is provided.
     */
    fun extractFieldWithValidation(
        proxy: AirbyteValueProxy,
        accessor: FieldAccessor
    ): FieldExtractionResult {
        val context = ValidationContext(accessor.name, accessor.type, proxy, accessor)

        val extractionResult =
            try {
                extractTypedValue(proxy, accessor)
            } catch (_: Exception) {
                FieldExtractionResult(
                    null,
                    Meta.Change(
                        accessor.name,
                        AirbyteRecordMessageMetaChange.Change.NULLED,
                        AirbyteRecordMessageMetaChange.Reason.DESTINATION_SERIALIZATION_ERROR
                    )
                )
            }

        // Apply destination-specific validation if validator is provided
        return fieldValidator?.validate(context, extractionResult) ?: extractionResult
    }

    /** Core extraction logic that converts protobuf values to Airbyte values based on type. */
    private fun extractTypedValue(
        proxy: AirbyteValueProxy,
        accessor: FieldAccessor
    ): FieldExtractionResult {
        return when (accessor.type) {
            is BooleanType ->
                FieldExtractionResult(proxy.getBoolean(accessor)?.let { BooleanValue(it) }, null)
            is StringType ->
                FieldExtractionResult(proxy.getString(accessor)?.let { StringValue(it) }, null)
            is IntegerType ->
                FieldExtractionResult(proxy.getInteger(accessor)?.let { IntegerValue(it) }, null)
            is NumberType ->
                FieldExtractionResult(proxy.getNumber(accessor)?.let { NumberValue(it) }, null)
            is DateType -> {
                val dateStr = proxy.getDate(accessor)
                if (dateStr != null) {
                    try {
                        val localDate = LocalDate.parse(dateStr)
                        FieldExtractionResult(DateValue(localDate), null)
                    } catch (_: Exception) {
                        FieldExtractionResult(
                            null,
                            Meta.Change(
                                accessor.name,
                                AirbyteRecordMessageMetaChange.Change.NULLED,
                                AirbyteRecordMessageMetaChange.Reason
                                    .DESTINATION_SERIALIZATION_ERROR
                            )
                        )
                    }
                } else {
                    FieldExtractionResult(null, null)
                }
            }
            is TimestampTypeWithTimezone -> {
                val timestampStr = proxy.getTimestampWithTimezone(accessor)
                if (timestampStr != null) {
                    try {
                        val offsetDateTime = OffsetDateTime.parse(timestampStr)
                        FieldExtractionResult(TimestampWithTimezoneValue(offsetDateTime), null)
                    } catch (_: Exception) {
                        FieldExtractionResult(
                            null,
                            Meta.Change(
                                accessor.name,
                                AirbyteRecordMessageMetaChange.Change.NULLED,
                                AirbyteRecordMessageMetaChange.Reason
                                    .DESTINATION_SERIALIZATION_ERROR
                            )
                        )
                    }
                } else {
                    FieldExtractionResult(null, null)
                }
            }
            is TimestampTypeWithoutTimezone -> {
                val timestampStr = proxy.getTimestampWithoutTimezone(accessor)
                if (timestampStr != null) {
                    try {
                        val localDateTime = LocalDateTime.parse(timestampStr)
                        FieldExtractionResult(TimestampWithoutTimezoneValue(localDateTime), null)
                    } catch (_: Exception) {
                        FieldExtractionResult(
                            null,
                            Meta.Change(
                                accessor.name,
                                AirbyteRecordMessageMetaChange.Change.NULLED,
                                AirbyteRecordMessageMetaChange.Reason
                                    .DESTINATION_SERIALIZATION_ERROR
                            )
                        )
                    }
                } else {
                    FieldExtractionResult(null, null)
                }
            }
            is TimeTypeWithTimezone -> {
                val timeStr = proxy.getTimeWithTimezone(accessor)
                if (timeStr != null) {
                    try {
                        val offsetTime = OffsetTime.parse(timeStr)
                        FieldExtractionResult(TimeWithTimezoneValue(offsetTime), null)
                    } catch (_: Exception) {
                        FieldExtractionResult(
                            null,
                            Meta.Change(
                                accessor.name,
                                AirbyteRecordMessageMetaChange.Change.NULLED,
                                AirbyteRecordMessageMetaChange.Reason
                                    .DESTINATION_SERIALIZATION_ERROR
                            )
                        )
                    }
                } else {
                    FieldExtractionResult(null, null)
                }
            }
            is TimeTypeWithoutTimezone -> {
                val timeStr = proxy.getTimeWithoutTimezone(accessor)
                if (timeStr != null) {
                    try {
                        val localTime = LocalTime.parse(timeStr)
                        FieldExtractionResult(TimeWithoutTimezoneValue(localTime), null)
                    } catch (_: Exception) {
                        FieldExtractionResult(
                            null,
                            Meta.Change(
                                accessor.name,
                                AirbyteRecordMessageMetaChange.Change.NULLED,
                                AirbyteRecordMessageMetaChange.Reason
                                    .DESTINATION_SERIALIZATION_ERROR
                            )
                        )
                    }
                } else {
                    FieldExtractionResult(null, null)
                }
            }
            is UnionType -> {
                val jsonNode = proxy.getJsonNode(accessor)
                FieldExtractionResult(jsonNode?.toAirbyteValue(), null)
            }
            is ArrayType,
            is ObjectType -> {
                val jsonNode = proxy.getJsonNode(accessor)
                FieldExtractionResult(jsonNode?.toAirbyteValue(), null)
            }
            is UnknownType -> {
                FieldExtractionResult(null, null)
            }
            else -> {
                val jsonNode = proxy.getJsonNode(accessor)
                FieldExtractionResult(jsonNode?.let { StringValue(it.serializeToString()) }, null)
            }
        }
    }
}
