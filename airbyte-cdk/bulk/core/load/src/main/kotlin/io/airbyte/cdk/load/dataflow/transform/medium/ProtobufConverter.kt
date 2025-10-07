/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.transform.medium

import com.fasterxml.jackson.core.io.BigDecimalParser
import com.fasterxml.jackson.core.io.BigIntegerParser
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.AirbyteValueProxy.FieldAccessor
import io.airbyte.cdk.load.data.ArrayType
import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.BooleanType
import io.airbyte.cdk.load.data.BooleanValue
import io.airbyte.cdk.load.data.DateType
import io.airbyte.cdk.load.data.DateValue
import io.airbyte.cdk.load.data.EnrichedAirbyteValue
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
import io.airbyte.cdk.load.dataflow.transform.ColumnNameMapper
import io.airbyte.cdk.load.dataflow.transform.ValueCoercer
import io.airbyte.cdk.load.dataflow.transform.defaults.NoOpColumnNameMapper
import io.airbyte.cdk.load.message.DestinationRecordProtobufSource
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.util.Jsons
import io.airbyte.cdk.load.util.serializeToString
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import io.airbyte.protocol.protobuf.AirbyteRecordMessage.AirbyteValueProtobuf
import java.math.BigDecimal
import java.time.Instant
import java.time.OffsetDateTime
import java.time.ZoneOffset
import java.util.concurrent.ConcurrentHashMap
import javax.inject.Singleton

/**
 * Converter that extracts typed values from protobuf records and converts them to
 * EnrichedAirbyteValue with destination-specific coercion applied through the Coercer interface.
 */
@Singleton
class ProtobufConverter(
    private val columnNameMapper: ColumnNameMapper,
    private val coercer: ValueCoercer,
) {

    private val isNoOpMapper = columnNameMapper is NoOpColumnNameMapper

    private val perStreamMappedNames =
        ConcurrentHashMap<DestinationStream.Descriptor, Array<String>>()

    private fun mappedNamesFor(
        stream: DestinationStream,
        fieldAccessors: Array<FieldAccessor>
    ): Array<String> {
        val key = stream.mappedDescriptor
        return perStreamMappedNames.computeIfAbsent(key) {
            val maxIndex = fieldAccessors.maxOfOrNull { it.index } ?: -1
            val arr = Array(maxIndex + 1) { "" }
            fieldAccessors.forEach { fa ->
                val mapped = columnNameMapper.getMappedColumnName(stream, fa.name) ?: fa.name
                arr[fa.index] = mapped
            }
            arr
        }
    }

    /**
     * Converts protobuf data to a complete map of AirbyteValue including metadata fields. This
     * method handles both data fields and metadata fields in one operation.
     *
     * @param msg The destination record raw containing stream information
     * @param source The protobuf source containing data and metadata
     * @return Map of column names to AirbyteValue including all metadata fields
     */
    fun convert(
        msg: DestinationRecordRaw,
        source: DestinationRecordProtobufSource,
    ): Map<String, AirbyteValue> {
        val stream = msg.stream
        val fieldAccessors = stream.airbyteValueProxyFieldAccessors
        val data = source.source.record.dataList

        val result =
            HashMap<String, AirbyteValue>(fieldAccessors.size + 4) // +4 for metadata fields
        val allParsingFailures = mutableListOf<Meta.Change>()

        fieldAccessors.forEach { accessor ->
            val protobufValue = data.getOrNull(accessor.index)

            val enrichedValue =
                EnrichedAirbyteValue(
                    abValue = NullValue, // Temporary, will be set by extractTypedValue
                    type = accessor.type,
                    name = accessor.name,
                    airbyteMetaField = null
                )

            val airbyteValue = extractTypedValue(protobufValue, accessor, enrichedValue)
            enrichedValue.abValue = airbyteValue

            val mappedValue = coercer.map(enrichedValue)
            val validatedValue = coercer.validate(mappedValue)

            allParsingFailures.addAll(validatedValue.changes)

            if (validatedValue.abValue !is NullValue || validatedValue.type !is UnknownType) {
                val columnName =
                    if (isNoOpMapper) accessor.name
                    else
                        mappedNamesFor(stream, fieldAccessors).getOrElse(accessor.index) {
                            accessor.name
                        }
                result[columnName] = validatedValue.abValue
            }
        }

        addMetadataFields(result, msg, source, allParsingFailures)

        return result
    }

    private fun addMetadataFields(
        result: HashMap<String, AirbyteValue>,
        msg: DestinationRecordRaw,
        source: DestinationRecordProtobufSource,
        parsingFailures: List<Meta.Change>
    ) {
        val timestampValue = Instant.ofEpochMilli(source.emittedAtMs)
        result[Meta.COLUMN_NAME_AB_EXTRACTED_AT] =
            TimestampWithTimezoneValue(OffsetDateTime.ofInstant(timestampValue, ZoneOffset.UTC))

        result[Meta.COLUMN_NAME_AB_GENERATION_ID] =
            IntegerValue(msg.stream.generationId.toBigInteger())

        result[Meta.COLUMN_NAME_AB_RAW_ID] = StringValue(msg.airbyteRawId.toString())

        val allChanges =
            source.sourceMeta.changes + msg.stream.unknownColumnChanges + parsingFailures
        val changesArray = buildMetaArrayValue(allChanges)

        val metaValue =
            ObjectValue(
                linkedMapOf(
                    "sync_id" to IntegerValue(msg.stream.syncId.toBigInteger()),
                    "changes" to changesArray,
                ),
            )
        result[Meta.COLUMN_NAME_AB_META] = metaValue
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

    private fun extractTypedValue(
        protobufValue: AirbyteValueProtobuf?,
        accessor: FieldAccessor,
        enrichedValue: EnrichedAirbyteValue
    ): AirbyteValue {
        if (protobufValue == null || protobufValue.isNull) {
            return NullValue
        }

        return try {
            // Step 1: Extract raw value from protobuf using the right method based on type
            val rawValue = extractRawValue(protobufValue, accessor)

            // Step 2: Decide final target type (check for destination override first)
            val targetClass =
                coercer.representAs(accessor.type) ?: getDefaultTargetClass(accessor.type)

            // Step 3: Create AirbyteValue of the target type using the raw value
            createAirbyteValue(rawValue, targetClass)
        } catch (_: Exception) {
            // Add parsing error to metadata
            enrichedValue.changes.add(
                Meta.Change(
                    accessor.name,
                    AirbyteRecordMessageMetaChange.Change.NULLED,
                    AirbyteRecordMessageMetaChange.Reason.DESTINATION_SERIALIZATION_ERROR
                )
            )
            NullValue
        }
    }

    private fun extractRawValue(
        protobufValue: AirbyteValueProtobuf,
        accessor: FieldAccessor
    ): Any? {
        return when (accessor.type) {
            is BooleanType -> protobufValue.boolean
            is StringType -> protobufValue.string
            is IntegerType -> {
                if (protobufValue.hasBigInteger()) {
                    BigIntegerParser.parseWithFastParser(protobufValue.bigInteger)
                } else {
                    protobufValue.integer.toBigInteger()
                }
            }
            is NumberType -> {
                if (protobufValue.hasBigDecimal()) {
                    BigDecimalParser.parseWithFastParser(protobufValue.bigDecimal)
                } else if (protobufValue.hasNumber()) {
                    protobufValue.number.toBigDecimal()
                } else {
                    null
                }
            }
            is DateType -> protobufValue.date
            is TimestampTypeWithTimezone -> protobufValue.timestampWithTimezone
            is TimestampTypeWithoutTimezone -> protobufValue.timestampWithoutTimezone
            is TimeTypeWithTimezone -> protobufValue.timeWithTimezone
            is TimeTypeWithoutTimezone -> protobufValue.timeWithoutTimezone
            is UnionType,
            is ArrayType,
            is ObjectType -> {
                val jsonNode = Jsons.readTree(protobufValue.json.toByteArray())
                jsonNode.toAirbyteValue()
            }
            is UnknownType -> null
            else -> {
                val jsonNode = Jsons.readTree(protobufValue.json.toByteArray())
                jsonNode.serializeToString()
            }
        }
    }

    private fun getDefaultTargetClass(
        airbyteType: io.airbyte.cdk.load.data.AirbyteType
    ): Class<out AirbyteValue> {
        return when (airbyteType) {
            is BooleanType -> BooleanValue::class.java
            is StringType -> StringValue::class.java
            is IntegerType -> IntegerValue::class.java
            is NumberType -> NumberValue::class.java
            is DateType -> DateValue::class.java
            is TimestampTypeWithTimezone -> TimestampWithTimezoneValue::class.java
            is TimestampTypeWithoutTimezone -> TimestampWithoutTimezoneValue::class.java
            is TimeTypeWithTimezone -> TimeWithTimezoneValue::class.java
            is TimeTypeWithoutTimezone -> TimeWithoutTimezoneValue::class.java
            is UnionType,
            is ArrayType,
            is ObjectType -> AirbyteValue::class.java // Will be handled specially
            is UnknownType -> NullValue::class.java
            else -> StringValue::class.java
        }
    }

    @Suppress("UNCHECKED_CAST")
    private fun createAirbyteValue(
        rawValue: Any?,
        targetClass: Class<out AirbyteValue>
    ): AirbyteValue {
        if (rawValue == null) return NullValue

        return when (targetClass) {
            BooleanValue::class.java -> BooleanValue(rawValue as Boolean)
            StringValue::class.java -> StringValue(rawValue.toString())
            IntegerValue::class.java -> IntegerValue(rawValue as java.math.BigInteger)
            NumberValue::class.java -> NumberValue(rawValue as BigDecimal)
            DateValue::class.java -> DateValue(rawValue as String)
            TimestampWithTimezoneValue::class.java -> TimestampWithTimezoneValue(rawValue as String)
            TimestampWithoutTimezoneValue::class.java ->
                TimestampWithoutTimezoneValue(rawValue as String)
            TimeWithTimezoneValue::class.java -> TimeWithTimezoneValue(rawValue as String)
            TimeWithoutTimezoneValue::class.java -> TimeWithoutTimezoneValue(rawValue as String)
            NullValue::class.java -> NullValue
            AirbyteValue::class.java ->
                rawValue as AirbyteValue // Already an AirbyteValue (JSON types)
            else -> StringValue(rawValue.toString()) // Fallback to string
        }
    }
}
