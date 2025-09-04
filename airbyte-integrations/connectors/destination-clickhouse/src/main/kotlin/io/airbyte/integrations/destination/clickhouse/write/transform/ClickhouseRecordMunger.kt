/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse.write.transform

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.AirbyteValueProxy
import io.airbyte.cdk.load.data.AirbyteValueProxy.FieldAccessor
import io.airbyte.cdk.load.data.ArrayType
import io.airbyte.cdk.load.data.ArrayValue
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
import io.airbyte.cdk.load.data.ObjectValue
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
import io.airbyte.cdk.load.dataflow.transform.DataMunger
import io.airbyte.cdk.load.message.DestinationRecordProtobufSource
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TableCatalog
import io.airbyte.cdk.load.util.serializeToString
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import jakarta.inject.Singleton
import kotlin.collections.plus

/*
 * Munges values and keys into a simple map form. Encapsulates
 * EnrichedAirbyteValue logic from other classes, so it can be replaced if
 * necessary, as we know it's slow.
 *
 * The HashMap construction is deliberate for speed considerations.
 */
@Singleton
class ClickhouseRecordMunger(
    private val catalogInfo: TableCatalog,
    private val coercer: ClickhouseCoercer,
) : DataMunger {
    override fun transformForDest(msg: DestinationRecordRaw): Map<String, AirbyteValue> {
        return when (val source = msg.rawData) {
            is DestinationRecordProtobufSource -> transformProtobuf(msg, source)
            else -> transformEnrichedLegacy(msg)
        }
    }

    private fun transformEnrichedLegacy(msg: DestinationRecordRaw): HashMap<String, AirbyteValue> {
        // this actually munges and coerces data
        val enriched =
            msg.asEnrichedDestinationRecordAirbyteValue(extractedAtAsTimestampWithTimezone = true)

        val munged = HashMap<String, AirbyteValue>()
        enriched.declaredFields.forEach { field ->
            val mappedKey = catalogInfo.getMappedColumnName(msg.stream, field.key)!!
            val fieldType = msg.schemaFields[field.key]!!

            var mappedValue =
                field.value
                    .let { if (fieldType.type is UnionType) coercer.toJsonStringValue(it) else it }
                    .let { coercer.validate(it) }

            mappedValue = coercer.validate(mappedValue)

            munged[mappedKey] = mappedValue.abValue
        }
        // must be called second so it picks up any meta changes from above
        enriched.airbyteMetaFields.forEach { munged[it.key] = it.value.abValue }

        return munged
    }

    private fun transformProtobuf(
        msg: DestinationRecordRaw,
        source: DestinationRecordProtobufSource
    ): Map<String, AirbyteValue> {
        val stream = msg.stream
        val proxy = source.asAirbyteValueProxy()

        val fieldAccessors = stream.airbyteValueProxyFieldAccessors

        val result = HashMap<String, AirbyteValue>(stream.airbyteValueProxyFieldAccessors.size)
        val parsingFailures = mutableListOf<Meta.Change>()

        fieldAccessors.forEach { accessor ->
            val mappedColumnName =
                catalogInfo.getMappedColumnName(stream, accessor.name) ?: return@forEach

            val extractionResult = extractTypedValueWithErrorHandling(proxy, accessor)
            if (extractionResult.parsingError != null) {
                parsingFailures.add(extractionResult.parsingError)
            }

            if (extractionResult.value != null) {
                result[mappedColumnName] = extractionResult.value
            } else if (accessor.type !is UnknownType) {
                result[mappedColumnName] = NullValue
            }
        }

        addMetadataFields(result, msg, source, parsingFailures)

        return result
    }

    data class ExtractionResult(val value: AirbyteValue?, val parsingError: Meta.Change?)

    private fun extractTypedValueWithErrorHandling(
        proxy: AirbyteValueProxy,
        accessor: FieldAccessor
    ): ExtractionResult {
        return try {
            when (accessor.type) {
                is BooleanType ->
                    ExtractionResult(proxy.getBoolean(accessor)?.let { BooleanValue(it) }, null)
                is StringType ->
                    ExtractionResult(proxy.getString(accessor)?.let { StringValue(it) }, null)
                is IntegerType -> {
                    val value = proxy.getInteger(accessor)
                    if (
                        value != null &&
                            (value < ClickhouseCoercer.Constants.INT64_MIN ||
                                value > ClickhouseCoercer.Constants.INT64_MAX)
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
                        ExtractionResult(value?.let { IntegerValue(it) }, null)
                    }
                }
                is NumberType -> {
                    val value = proxy.getNumber(accessor)
                    if (value != null) {
                        if (
                            value <= ClickhouseCoercer.Constants.DECIMAL128_MIN ||
                                value >= ClickhouseCoercer.Constants.DECIMAL128_MAX
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
                            ExtractionResult(NumberValue(value), null)
                        }
                    } else {
                        ExtractionResult(null, null)
                    }
                }
                is DateType -> {
                    val dateStr = proxy.getDate(accessor)
                    if (dateStr != null) {
                        try {
                            val localDate = java.time.LocalDate.parse(dateStr)
                            val days = localDate.toEpochDay()
                            if (
                                days < ClickhouseCoercer.Constants.DATE32_MIN ||
                                    days > ClickhouseCoercer.Constants.DATE32_MAX
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
                                ExtractionResult(DateValue(localDate), null)
                            }
                        } catch (e: Exception) {
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
                    val timestampStr = proxy.getTimestampWithTimezone(accessor)
                    if (timestampStr != null) {
                        try {
                            val instant = java.time.Instant.parse(timestampStr)
                            val seconds = instant.epochSecond
                            if (
                                seconds < ClickhouseCoercer.Constants.DATETIME64_MIN ||
                                    seconds > ClickhouseCoercer.Constants.DATETIME64_MAX
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
                                ExtractionResult(
                                    TimestampWithTimezoneValue(
                                        java.time.OffsetDateTime.parse(timestampStr)
                                    ),
                                    null
                                )
                            }
                        } catch (e: Exception) {
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
                    val timestampStr = proxy.getTimestampWithoutTimezone(accessor)
                    if (timestampStr != null) {
                        try {
                            val localDateTime = java.time.LocalDateTime.parse(timestampStr)
                            val seconds = localDateTime.toEpochSecond(java.time.ZoneOffset.UTC)
                            if (
                                seconds < ClickhouseCoercer.Constants.DATETIME64_MIN ||
                                    seconds > ClickhouseCoercer.Constants.DATETIME64_MAX
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
                                ExtractionResult(TimestampWithoutTimezoneValue(localDateTime), null)
                            }
                        } catch (e: Exception) {
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
                    val timeStr = proxy.getTimeWithTimezone(accessor)
                    if (timeStr != null) {
                        try {
                            val offsetTime = java.time.OffsetTime.parse(timeStr)
                            ExtractionResult(TimeWithTimezoneValue(offsetTime), null)
                        } catch (e: Exception) {
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
                    val timeStr = proxy.getTimeWithoutTimezone(accessor)
                    if (timeStr != null) {
                        try {
                            val localTime = java.time.LocalTime.parse(timeStr)
                            ExtractionResult(TimeWithoutTimezoneValue(localTime), null)
                        } catch (e: Exception) {
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
                    val jsonNode = proxy.getJsonNode(accessor)
                    ExtractionResult(jsonNode?.toAirbyteValue(), null)
                }
                is ArrayType,
                is ObjectType -> {
                    val jsonNode = proxy.getJsonNode(accessor)
                    ExtractionResult(jsonNode?.toAirbyteValue(), null)
                }
                is UnknownType -> {
                    ExtractionResult(null, null)
                }
                else -> {
                    val jsonNode = proxy.getJsonNode(accessor)
                    ExtractionResult(jsonNode?.let { StringValue(it.serializeToString()) }, null)
                }
            }
        } catch (e: Exception) {
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

    private fun addMetadataFields(
        result: HashMap<String, AirbyteValue>,
        msg: DestinationRecordRaw,
        source: DestinationRecordProtobufSource,
        parsingFailures: List<Meta.Change>
    ) {
        val extractedAtColumn =
            catalogInfo.getMappedColumnName(msg.stream, Meta.COLUMN_NAME_AB_EXTRACTED_AT)
        if (extractedAtColumn != null) {
            val timestampValue = java.time.Instant.ofEpochMilli(source.emittedAtMs)
            result[extractedAtColumn] =
                TimestampWithTimezoneValue(
                    java.time.OffsetDateTime.ofInstant(
                        timestampValue,
                        java.time.ZoneOffset.UTC,
                    ),
                )
        }

        val generationIdColumn =
            catalogInfo.getMappedColumnName(msg.stream, Meta.COLUMN_NAME_AB_GENERATION_ID)
        if (generationIdColumn != null) {
            result[generationIdColumn] = IntegerValue(msg.stream.generationId.toBigInteger())
        }

        val rawIdColumn = catalogInfo.getMappedColumnName(msg.stream, Meta.COLUMN_NAME_AB_RAW_ID)
        if (rawIdColumn != null) {
            result[rawIdColumn] = StringValue(msg.airbyteRawId.toString())
        }

        val metaColumn = catalogInfo.getMappedColumnName(msg.stream, Meta.COLUMN_NAME_AB_META)
        if (metaColumn != null) {
            val unknownColumnChanges = msg.stream.unknownColumnChanges

            val allChanges = source.sourceMeta.changes + unknownColumnChanges + parsingFailures
            val changesArray = buildMetaArrayValue(allChanges)

            val metaValue =
                ObjectValue(
                    linkedMapOf(
                        "sync_id" to IntegerValue(msg.stream.syncId.toBigInteger()),
                        "changes" to changesArray,
                    ),
                )
            result[metaColumn] = metaValue
        }
    }

    private fun buildMetaArrayValue(allChanges: List<Meta.Change>): ArrayValue {
        val changeObjects =
            allChanges.map { change ->
                ObjectValue(
                    linkedMapOf(
                        "field" to StringValue(change.field),
                        "change" to StringValue(change.change.toString()),
                        "reason" to StringValue(change.reason.toString())
                    )
                )
            }

        return ArrayValue(changeObjects)
    }
}
