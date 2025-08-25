/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.write.bulk_loader

import com.fasterxml.jackson.core.io.JsonStringEncoder
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.AirbyteValueProxy
import io.airbyte.cdk.load.data.AirbyteValueProxy.FieldAccessor
import io.airbyte.cdk.load.data.ArrayType
import io.airbyte.cdk.load.data.BooleanType
import io.airbyte.cdk.load.data.DateType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.NumberType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.TimeTypeWithTimezone
import io.airbyte.cdk.load.data.TimeTypeWithoutTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithoutTimezone
import io.airbyte.cdk.load.data.UnionType
import io.airbyte.cdk.load.data.UnknownType
import io.airbyte.cdk.load.data.collectUnknownPaths
import io.airbyte.cdk.load.message.DestinationRecordProtobufSource
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.util.serializeToString
import io.airbyte.integrations.destination.bigquery.BigQueryConsts
import io.airbyte.integrations.destination.bigquery.formatter.BigQueryRecordFormatter
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import java.math.BigDecimal
import java.math.RoundingMode
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.OffsetDateTime
import java.time.OffsetTime
import java.util.concurrent.TimeUnit

/**
 * High-performance CSV row generator that processes protobuf records directly without JSON
 * conversion, optimized for BigQuery's GCS staging mode.
 * 
 * IMPORTANT: This is NOT for legacy raw tables - only for direct load tables.
 */
class ProtoToBigQueryCSVRowGenerator(
    private val header: Array<String>,
    private val stream: DestinationStream,
    private val fieldAccessors: Array<FieldAccessor>
) {
    
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
    
    // Pre-computed indices for meta columns using header.indexOf() like ProtoToCsvWriter
    private val idxRawId = header.indexOf(Meta.COLUMN_NAME_AB_RAW_ID)
    private val idxExtractedAt = header.indexOf(Meta.COLUMN_NAME_AB_EXTRACTED_AT)
    private val idxMeta = header.indexOf(Meta.COLUMN_NAME_AB_META)
    private val idxGenerationId = header.indexOf(Meta.COLUMN_NAME_AB_GENERATION_ID)
    
    // Row index mapping for field accessors like ProtoToCsvWriter
    private val rowIndex: Map<String, Int> = fieldAccessors.associate { it.name to header.indexOf(it.name) }
    
    // Reusable buffer to avoid repeated allocations - pre-filled with NULL_MARKER since BigQuery has no nulls
    private val rowBuf: Array<Any> = Array(header.size) { BigQueryConsts.NULL_MARKER }

    fun generate(record: DestinationRecordRaw): Array<Any> {
        val src = record.rawData
        require(src is DestinationRecordProtobufSource) {
            "ProtoToBigQueryCSVRowGenerator only supports DestinationRecordProtobufSource"
        }

        val proxy = src.asAirbyteValueProxy()
        val parsingFailures = mutableListOf<Meta.Change>()
        
        // Process data fields using row index mapping like ProtoToCsvWriter
        var i = 0
        while (i < fieldAccessors.size) {
            val accessor = fieldAccessors[i]
            val index = rowIndex[accessor.name] 
                ?: throw IllegalArgumentException("Column '${accessor.name}' not found in row index")
            val result = extractTypedValueWithErrorHandling(proxy, accessor)
            if (result.parsingError != null) {
                parsingFailures.add(result.parsingError)
            }
            rowBuf[index] = result.value ?: BigQueryConsts.NULL_MARKER
            i++
        }
        
        // Set meta columns using pre-computed indices
        rowBuf[idxRawId] = record.airbyteRawId.toString()
        rowBuf[idxExtractedAt] = formatExtractedAt(record.rawData.emittedAtMs)
        rowBuf[idxGenerationId] = stream.generationId.toString()
        
        // Build meta object with all changes including parsing failures
        val allChanges = record.rawData.sourceMeta.changes + unknownColumnChanges + parsingFailures
        rowBuf[idxMeta] = buildMetaString(record, allChanges)
        
        return rowBuf
    }

    data class ExtractionResult(
        val value: Any?,
        val parsingError: Meta.Change?
    )
    
    private fun extractTypedValueWithErrorHandling(
        proxy: AirbyteValueProxy,
        accessor: FieldAccessor
    ): ExtractionResult {
        return try {
            when (accessor.type) {
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
                                    AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION
                                )
                            )
                        } else if (validatedResult.changeType != null) {
                            ExtractionResult(
                                validatedResult.value,
                                Meta.Change(
                                    accessor.name,
                                    validatedResult.changeType,
                                    AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION
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
                                        AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION
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
                                    AirbyteRecordMessageMetaChange.Reason.DESTINATION_SERIALIZATION_ERROR
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
                                        AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION
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
                                    AirbyteRecordMessageMetaChange.Reason.DESTINATION_SERIALIZATION_ERROR
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
                                        AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION
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
                                    AirbyteRecordMessageMetaChange.Reason.DESTINATION_SERIALIZATION_ERROR
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
                                    OffsetTime.parse(timeValue)
                                )
                            ExtractionResult(formattedValue, null)
                        } catch (_: Exception) {
                            ExtractionResult(
                                null,
                                Meta.Change(
                                    accessor.name,
                                    AirbyteRecordMessageMetaChange.Change.NULLED,
                                    AirbyteRecordMessageMetaChange.Reason.DESTINATION_SERIALIZATION_ERROR
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
                                    LocalTime.parse(timeValue)
                                )
                            ExtractionResult(formattedValue, null)
                        } catch (_: Exception) {
                            ExtractionResult(
                                null,
                                Meta.Change(
                                    accessor.name,
                                    AirbyteRecordMessageMetaChange.Change.NULLED,
                                    AirbyteRecordMessageMetaChange.Reason.DESTINATION_SERIALIZATION_ERROR
                                )
                            )
                        }
                    } else {
                        ExtractionResult(null, null)
                    }
                }
                is ArrayType,
                is ObjectType,
                is UnknownType,
                is UnionType -> {
                    // Complex types: serialize to JSON string for BigQuery
                    val jsonNode = proxy.getJsonNode(accessor)
                    ExtractionResult(jsonNode?.serializeToString(), null)
                }
                else -> {
                    // Fallback for unknown types
                    val jsonNode = proxy.getJsonNode(accessor)
                    ExtractionResult(jsonNode?.serializeToString(), null)
                }
            }
        } catch (_: Exception) {
            // Handle any extraction errors by nulling the field
            ExtractionResult(
                null,
                Meta.Change(
                    accessor.name,
                    AirbyteRecordMessageMetaChange.Change.NULLED,
                    AirbyteRecordMessageMetaChange.Reason.DESTINATION_SERIALIZATION_ERROR
                )
            )
        }
    }


    data class ValidatedNumericResult(
        val value: BigDecimal?,
        val changeType: AirbyteRecordMessageMetaChange.Change?
    )
    
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

    private fun formatExtractedAt(emittedAtMs: Long): String {
        val emittedAtMicroseconds =
            TimeUnit.MICROSECONDS.convert(emittedAtMs, TimeUnit.MILLISECONDS)
        return com.google.cloud.bigquery.QueryParameterValue.timestamp(emittedAtMicroseconds)
            .value!!
    }

    private fun buildMetaString(record: DestinationRecordRaw, allChanges: List<Meta.Change>): String =
        buildString(64) {
            append('{')
            append("\"sync_id\":").append(record.stream.syncId).append(',')
            append("\"changes\":[")
            allChanges.forEachIndexed { idx, c ->
                append('{')
                append("\"field\":\"").append(escape(c.field)).append("\",")
                append("\"change\":\"").append(c.change.name).append("\",")
                append("\"reason\":\"").append(c.reason.name).append("\"}")
                if (idx != allChanges.lastIndex) append(',')
            }
            append("]}")
        }

    private fun escape(s: String): String = String(jsonEscaper.quoteAsString(s))
}
