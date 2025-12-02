/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.formatter

import com.fasterxml.jackson.core.io.JsonStringEncoder
import com.google.cloud.bigquery.QueryParameterValue
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.AirbyteValueCoercer
import io.airbyte.cdk.load.data.AirbyteValueProxy
import io.airbyte.cdk.load.data.AirbyteValueProxy.FieldAccessor
import io.airbyte.cdk.load.data.ArrayType
import io.airbyte.cdk.load.data.BooleanType
import io.airbyte.cdk.load.data.BooleanValue
import io.airbyte.cdk.load.data.DateType
import io.airbyte.cdk.load.data.DateValue
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NullValue
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
import io.airbyte.cdk.load.data.collectUnknownPaths
import io.airbyte.cdk.load.data.json.toAirbyteValue
import io.airbyte.cdk.load.message.DestinationRecordProtobufSource
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.integrations.destination.bigquery.write.standard_insert.RecordFormatter
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import java.math.BigDecimal
import java.math.RoundingMode
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.OffsetDateTime
import java.util.concurrent.TimeUnit

class ProtoToBigQueryStandardInsertRecordFormatter(
    private val fieldAccessors: Array<FieldAccessor>,
    private val columnNameMapping: ColumnNameMapping,
    private val stream: DestinationStream,
    private val legacyRawTablesOnly: Boolean = false,
) : RecordFormatter {

    // Pre-compute unknown columns to track parsing failures
    private val unknownColumnChanges =
        stream.schema
            .collectUnknownPaths()
            .map {
                Meta.Change(
                    it,
                    AirbyteRecordMessageMetaChange.Change.NULLED,
                    AirbyteRecordMessageMetaChange.Reason.DESTINATION_SERIALIZATION_ERROR,
                )
            }
            .toMutableList()

    private val jsonEscaper = JsonStringEncoder.getInstance()

    override fun formatRecord(record: DestinationRecordRaw): String {
        val src = record.rawData
        require(src is DestinationRecordProtobufSource) {
            "ProtoToBigQueryRecordFormatter only supports DestinationRecordProtobufSource"
        }

        val proxy = src.asAirbyteValueProxy()

        val parsingFailures = mutableListOf<Meta.Change>()

        return buildJsonRecord(record, proxy, parsingFailures)
    }

    private fun buildJsonRecord(
        record: DestinationRecordRaw,
        proxy: AirbyteValueProxy,
        parsingFailures: MutableList<Meta.Change>
    ): String {
        val estimatedCapacity = 256 + fieldAccessors.size * 32

        return buildString(estimatedCapacity) {
            append('{')

            var needsComma = false

            needsComma = appendRecordFields(this, proxy, parsingFailures, needsComma)

            appendMetaFields(this, record, parsingFailures, needsComma)

            append('}')
        }
    }

    private fun appendRecordFields(
        builder: StringBuilder,
        proxy: AirbyteValueProxy,
        parsingFailures: MutableList<Meta.Change>,
        needsComma: Boolean
    ): Boolean {
        var addComma = needsComma

        if (legacyRawTablesOnly) {
            if (addComma) builder.append(',')

            builder.append('"').append(Meta.COLUMN_NAME_DATA).append("\":")

            val validatedJsonData = buildValidatedJsonData(proxy, parsingFailures)
            builder.append('"').append(escape(validatedJsonData)).append('"')

            addComma = true
        } else {
            fieldAccessors.forEach { accessor ->
                val result = extractTypedValueWithErrorHandling(proxy, accessor)

                if (result.parsingError != null) {
                    parsingFailures.add(result.parsingError)
                }

                if (addComma) builder.append(',')

                val columnName = columnNameMapping[accessor.name]!!
                builder.append('"').append(escape(columnName)).append("\":")
                appendJsonValue(builder, result.value, result.isRawJson)

                addComma = true
            }
        }

        return addComma
    }

    private fun appendMetaFields(
        builder: StringBuilder,
        record: DestinationRecordRaw,
        parsingFailures: MutableList<Meta.Change>,
        needsComma: Boolean
    ) {
        if (needsComma) builder.append(',')
        builder
            .append('"')
            .append(Meta.COLUMN_NAME_AB_RAW_ID)
            .append("\":\"")
            .append(escape(record.airbyteRawId.toString()))
            .append('"')

        builder
            .append(",\"")
            .append(Meta.COLUMN_NAME_AB_EXTRACTED_AT)
            .append("\":\"")
            .append(formatExtractedAt(record.rawData.emittedAtMs))
            .append('"')

        builder
            .append(",\"")
            .append(Meta.COLUMN_NAME_AB_GENERATION_ID)
            .append("\":")
            .append(stream.generationId)

        builder.append(",\"").append(Meta.COLUMN_NAME_AB_META).append("\":")
        val allChanges = record.rawData.sourceMeta.changes + unknownColumnChanges + parsingFailures

        if (legacyRawTablesOnly) {
            // In legacy mode, serialize meta as escaped JSON string
            val metaJson = buildMetaObjectAsString(record, allChanges)
            builder.append('"').append(escape(metaJson)).append('"')
        } else {
            // In direct-load mode, create raw JSON object
            appendMetaObject(builder, record, allChanges)
        }
    }

    data class ExtractionResult(
        val value: Any?,
        val parsingError: Meta.Change?,
        val isRawJson: Boolean = false
    )

    private fun extractTypedValueWithErrorHandling(
        proxy: AirbyteValueProxy,
        accessor: FieldAccessor
    ): ExtractionResult {
        return when (accessor.type) {
            is BooleanType -> ExtractionResult(proxy.getBoolean(accessor), null)
            is StringType -> ExtractionResult(proxy.getString(accessor), null)
            is IntegerType -> {
                val value = proxy.getInteger(accessor)
                if (
                    value != null &&
                        (value < BigQueryRecordFormatter.INT64_MIN_VALUE ||
                            value > BigQueryRecordFormatter.INT64_MAX_VALUE)
                ) {
                    ExtractionResult(
                        null,
                        Meta.Change(
                            accessor.name,
                            AirbyteRecordMessageMetaChange.Change.NULLED,
                            AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION
                        )
                    )
                } else {
                    ExtractionResult(value?.longValueExact(), null)
                }
            }
            is NumberType -> {
                val value = proxy.getNumber(accessor)
                if (value != null) {
                    val validatedResult = validateAndFormatNumeric(value)
                    if (validatedResult.value == null) {
                        ExtractionResult(
                            null,
                            Meta.Change(
                                accessor.name,
                                validatedResult.changeType!!,
                                AirbyteRecordMessageMetaChange.Reason
                                    .DESTINATION_FIELD_SIZE_LIMITATION
                            )
                        )
                    } else if (validatedResult.changeType != null) {
                        ExtractionResult(
                            validatedResult.value,
                            Meta.Change(
                                accessor.name,
                                validatedResult.changeType,
                                AirbyteRecordMessageMetaChange.Reason
                                    .DESTINATION_FIELD_SIZE_LIMITATION
                            )
                        )
                    } else {
                        ExtractionResult(validatedResult.value, null)
                    }
                } else {
                    ExtractionResult(null, null)
                }
            }
            is DateType -> {
                val dateValue = proxy.getDate(accessor)
                if (dateValue != null) {
                    try {
                        val parsedDate = LocalDate.parse(dateValue)
                        if (
                            parsedDate < BigQueryRecordFormatter.DATE_MIN_VALUE ||
                                parsedDate > BigQueryRecordFormatter.DATE_MAX_VALUE
                        ) {
                            ExtractionResult(
                                null,
                                Meta.Change(
                                    accessor.name,
                                    AirbyteRecordMessageMetaChange.Change.NULLED,
                                    AirbyteRecordMessageMetaChange.Reason
                                        .DESTINATION_FIELD_SIZE_LIMITATION
                                )
                            )
                        } else {
                            ExtractionResult(dateValue, null)
                        }
                    } catch (_: Exception) {
                        ExtractionResult(
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
                    ExtractionResult(null, null)
                }
            }
            is TimestampTypeWithTimezone -> {
                val timestampValue = proxy.getTimestampWithTimezone(accessor)
                if (timestampValue != null) {
                    try {
                        val parsedTimestamp = OffsetDateTime.parse(timestampValue)
                        if (
                            parsedTimestamp < BigQueryRecordFormatter.TIMESTAMP_MIN_VALUE ||
                                parsedTimestamp > BigQueryRecordFormatter.TIMESTAMP_MAX_VALUE
                        ) {
                            ExtractionResult(
                                null,
                                Meta.Change(
                                    accessor.name,
                                    AirbyteRecordMessageMetaChange.Change.NULLED,
                                    AirbyteRecordMessageMetaChange.Reason
                                        .DESTINATION_FIELD_SIZE_LIMITATION
                                )
                            )
                        } else {
                            val formattedValue =
                                BigQueryRecordFormatter.DATETIME_WITH_TIMEZONE_FORMATTER.format(
                                    parsedTimestamp
                                )
                            ExtractionResult(formattedValue, null)
                        }
                    } catch (_: Exception) {
                        ExtractionResult(
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
                    ExtractionResult(null, null)
                }
            }
            is TimestampTypeWithoutTimezone -> {
                val timestampValue = proxy.getTimestampWithoutTimezone(accessor)
                if (timestampValue != null) {
                    try {
                        val parsedDateTime = LocalDateTime.parse(timestampValue)
                        if (
                            parsedDateTime < BigQueryRecordFormatter.DATETIME_MIN_VALUE ||
                                parsedDateTime > BigQueryRecordFormatter.DATETIME_MAX_VALUE
                        ) {
                            ExtractionResult(
                                null,
                                Meta.Change(
                                    accessor.name,
                                    AirbyteRecordMessageMetaChange.Change.NULLED,
                                    AirbyteRecordMessageMetaChange.Reason
                                        .DESTINATION_FIELD_SIZE_LIMITATION
                                )
                            )
                        } else {
                            val formattedValue =
                                BigQueryRecordFormatter.DATETIME_WITHOUT_TIMEZONE_FORMATTER.format(
                                    parsedDateTime
                                )
                            ExtractionResult(formattedValue, null)
                        }
                    } catch (_: Exception) {
                        ExtractionResult(
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
                    ExtractionResult(null, null)
                }
            }
            is TimeTypeWithTimezone -> {
                val timeValue = proxy.getTimeWithTimezone(accessor)
                if (timeValue != null) {
                    try {
                        val formattedValue =
                            BigQueryRecordFormatter.TIME_WITH_TIMEZONE_FORMATTER.format(
                                java.time.OffsetTime.parse(timeValue)
                            )
                        ExtractionResult(formattedValue, null)
                    } catch (_: Exception) {
                        ExtractionResult(
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
                    ExtractionResult(null, null)
                }
            }
            is TimeTypeWithoutTimezone -> {
                val timeValue = proxy.getTimeWithoutTimezone(accessor)
                if (timeValue != null) {
                    try {
                        val formattedValue =
                            BigQueryRecordFormatter.TIME_WITHOUT_TIMEZONE_FORMATTER.format(
                                java.time.LocalTime.parse(timeValue)
                            )
                        ExtractionResult(formattedValue, null)
                    } catch (_: Exception) {
                        ExtractionResult(
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
                    ExtractionResult(null, null)
                }
            }
            is UnionType -> {
                // Handle legacy unions by choosing the best type and coercing the value
                val unionType = accessor.type as UnionType
                if (unionType.isLegacyUnion) {
                    val chosenType = unionType.chooseType()
                    val jsonNode = proxy.getJsonNode(accessor)

                    if (jsonNode != null && !jsonNode.isNull) {
                        try {
                            val airbyteValue = jsonNode.toAirbyteValue()
                            val coercedValue =
                                AirbyteValueCoercer.coerce(
                                    airbyteValue,
                                    chosenType,
                                    respectLegacyUnions = true
                                )

                            if (coercedValue != null) {
                                return extractValueFromCoercedAirbyteValue(
                                    coercedValue,
                                    accessor.name
                                )
                            } else {
                                return ExtractionResult(
                                    null,
                                    Meta.Change(
                                        accessor.name,
                                        AirbyteRecordMessageMetaChange.Change.NULLED,
                                        AirbyteRecordMessageMetaChange.Reason
                                            .DESTINATION_SERIALIZATION_ERROR
                                    )
                                )
                            }
                        } catch (_: Exception) {
                            return ExtractionResult(
                                null,
                                Meta.Change(
                                    accessor.name,
                                    AirbyteRecordMessageMetaChange.Change.NULLED,
                                    AirbyteRecordMessageMetaChange.Reason
                                        .DESTINATION_SERIALIZATION_ERROR
                                )
                            )
                        }
                    }
                }
                ExtractionResult(proxy.getJsonNode(accessor)?.toString(), null, true)
            }
            is UnknownType -> {
                ExtractionResult(null, null)
            }
            is ArrayType,
            is ObjectType -> {
                ExtractionResult(proxy.getJsonNode(accessor)?.toString(), null, true)
            }
            else -> {
                ExtractionResult(proxy.getJsonNode(accessor)?.toString(), null, true)
            }
        }
    }

    private fun validateAndFormatNumeric(value: BigDecimal): ValidatedNumericResult {
        return when {
            value < BigQueryRecordFormatter.NUMERIC_MIN_VALUE ||
                value > BigQueryRecordFormatter.NUMERIC_MAX_VALUE ->
                ValidatedNumericResult(null, AirbyteRecordMessageMetaChange.Change.NULLED)
            value.scale() > BigQueryRecordFormatter.NUMERIC_MAX_SCALE -> {
                val roundedValue =
                    value.setScale(BigQueryRecordFormatter.NUMERIC_MAX_SCALE, RoundingMode.HALF_UP)
                ValidatedNumericResult(
                    roundedValue,
                    AirbyteRecordMessageMetaChange.Change.TRUNCATED
                )
            }
            else -> ValidatedNumericResult(value, null)
        }
    }

    private data class ValidatedNumericResult(
        val value: BigDecimal?,
        val changeType: AirbyteRecordMessageMetaChange.Change?
    )

    private fun extractValueFromCoercedAirbyteValue(
        coercedValue: AirbyteValue,
        fieldName: String
    ): ExtractionResult {
        return when (coercedValue) {
            NullValue -> ExtractionResult(null, null)
            is BooleanValue -> ExtractionResult(coercedValue.value, null)
            is StringValue -> ExtractionResult(coercedValue.value, null)
            is IntegerValue -> {
                if (
                    coercedValue.value < BigQueryRecordFormatter.INT64_MIN_VALUE ||
                        coercedValue.value > BigQueryRecordFormatter.INT64_MAX_VALUE
                ) {
                    ExtractionResult(
                        null,
                        Meta.Change(
                            fieldName,
                            AirbyteRecordMessageMetaChange.Change.NULLED,
                            AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION
                        )
                    )
                } else {
                    ExtractionResult(coercedValue.value.longValueExact(), null)
                }
            }
            is NumberValue -> {
                val validatedResult = validateAndFormatNumeric(coercedValue.value)
                if (validatedResult.value == null) {
                    ExtractionResult(
                        null,
                        Meta.Change(
                            fieldName,
                            validatedResult.changeType!!,
                            AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION
                        )
                    )
                } else if (validatedResult.changeType != null) {
                    ExtractionResult(
                        validatedResult.value,
                        Meta.Change(
                            fieldName,
                            validatedResult.changeType,
                            AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION
                        )
                    )
                } else {
                    ExtractionResult(validatedResult.value, null)
                }
            }
            is DateValue -> {
                if (
                    coercedValue.value < BigQueryRecordFormatter.DATE_MIN_VALUE ||
                        coercedValue.value > BigQueryRecordFormatter.DATE_MAX_VALUE
                ) {
                    ExtractionResult(
                        null,
                        Meta.Change(
                            fieldName,
                            AirbyteRecordMessageMetaChange.Change.NULLED,
                            AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION
                        )
                    )
                } else {
                    ExtractionResult(coercedValue.value.toString(), null)
                }
            }
            is TimestampWithTimezoneValue -> {
                if (
                    coercedValue.value < BigQueryRecordFormatter.TIMESTAMP_MIN_VALUE ||
                        coercedValue.value > BigQueryRecordFormatter.TIMESTAMP_MAX_VALUE
                ) {
                    ExtractionResult(
                        null,
                        Meta.Change(
                            fieldName,
                            AirbyteRecordMessageMetaChange.Change.NULLED,
                            AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION
                        )
                    )
                } else {
                    val formattedValue =
                        BigQueryRecordFormatter.DATETIME_WITH_TIMEZONE_FORMATTER.format(
                            coercedValue.value
                        )
                    ExtractionResult(formattedValue, null)
                }
            }
            is TimestampWithoutTimezoneValue -> {
                if (
                    coercedValue.value < BigQueryRecordFormatter.DATETIME_MIN_VALUE ||
                        coercedValue.value > BigQueryRecordFormatter.DATETIME_MAX_VALUE
                ) {
                    ExtractionResult(
                        null,
                        Meta.Change(
                            fieldName,
                            AirbyteRecordMessageMetaChange.Change.NULLED,
                            AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION
                        )
                    )
                } else {
                    val formattedValue =
                        BigQueryRecordFormatter.DATETIME_WITHOUT_TIMEZONE_FORMATTER.format(
                            coercedValue.value
                        )
                    ExtractionResult(formattedValue, null)
                }
            }
            is TimeWithTimezoneValue -> {
                val formattedValue =
                    BigQueryRecordFormatter.TIME_WITH_TIMEZONE_FORMATTER.format(coercedValue.value)
                ExtractionResult(formattedValue, null)
            }
            is TimeWithoutTimezoneValue -> {
                val formattedValue =
                    BigQueryRecordFormatter.TIME_WITHOUT_TIMEZONE_FORMATTER.format(
                        coercedValue.value
                    )
                ExtractionResult(formattedValue, null)
            }
            else -> {
                ExtractionResult(coercedValue.toString(), null, true)
            }
        }
    }

    private fun formatExtractedAt(emittedAtMs: Long): String? {
        val emittedAtMicroseconds =
            TimeUnit.MICROSECONDS.convert(emittedAtMs, TimeUnit.MILLISECONDS)
        return QueryParameterValue.timestamp(emittedAtMicroseconds).value
    }

    private fun appendMetaObject(
        builder: StringBuilder,
        record: DestinationRecordRaw,
        allChanges: List<Meta.Change>
    ) {
        builder.append('{').append("\"sync_id\":").append(record.stream.syncId)
        builder.append(",\"changes\":[")
        allChanges.forEachIndexed { idx, change ->
            if (idx > 0) builder.append(',')
            builder
                .append("{\"field\":\"")
                .append(escape(change.field))
                .append("\",\"change\":\"")
                .append(change.change.name)
                .append("\",\"reason\":\"")
                .append(change.reason.name)
                .append("\"}")
        }
        builder.append(']')

        builder.append('}')
    }

    private fun appendJsonValue(builder: StringBuilder, value: Any?, isRawJson: Boolean = false) {
        when {
            value == null -> builder.append("null")
            isRawJson && value is String -> builder.append(value) // Raw JSON, don't escape
            value is String -> builder.append('"').append(escape(value)).append('"')
            value is Boolean -> builder.append(value)
            value is Number -> builder.append(value)
            else -> {
                builder.append('"').append(escape(value.toString())).append('"')
            }
        }
    }

    private fun buildValidatedJsonData(
        proxy: AirbyteValueProxy,
        parsingFailures: MutableList<Meta.Change>
    ): String {
        return buildString {
            append('{')

            var needsComma = false

            fieldAccessors.forEach { accessor ->
                val result = extractTypedValueWithErrorHandling(proxy, accessor)

                if (result.parsingError != null) {
                    parsingFailures.add(result.parsingError)
                }

                if (needsComma) append(',')

                append('"').append(escape(accessor.name)).append("\":")
                appendJsonValue(this, result.value, result.isRawJson)

                needsComma = true
            }

            append('}')
        }
    }

    private fun buildMetaObjectAsString(
        record: DestinationRecordRaw,
        allChanges: List<Meta.Change>
    ): String {
        return buildString {
            append('{').append("\"sync_id\":").append(record.stream.syncId)
            append(",\"changes\":[")
            allChanges.forEachIndexed { idx, change ->
                if (idx > 0) append(',')
                append("{\"field\":\"")
                append(escape(change.field))
                append("\",\"change\":\"")
                append(change.change.name)
                append("\",\"reason\":\"")
                append(change.reason.name)
                append("\"}")
            }
            append(']')
            append('}')
        }
    }

    private fun escape(s: String): String = String(jsonEscaper.quoteAsString(s))
}
