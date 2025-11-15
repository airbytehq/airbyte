/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.transform.medium

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.AirbyteValueProxy.FieldAccessor
import io.airbyte.cdk.load.data.ArrayType
import io.airbyte.cdk.load.data.ArrayTypeWithoutSchema
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
import io.airbyte.cdk.load.data.ObjectTypeWithEmptySchema
import io.airbyte.cdk.load.data.ObjectTypeWithoutSchema
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.ProtobufTypeMismatchException
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
import io.airbyte.cdk.load.dataflow.transform.ValueCoercer
import io.airbyte.cdk.load.dataflow.transform.data.ValidationResultHandler
import io.airbyte.cdk.load.message.DestinationRecordProtobufSource
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.util.Jsons
import io.airbyte.cdk.protocol.AirbyteValueProtobufDecoder
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import io.airbyte.protocol.protobuf.AirbyteRecordMessage.AirbyteValueProtobuf
import java.math.BigDecimal
import java.math.BigInteger
import java.time.Instant
import java.time.LocalDate
import java.time.LocalTime
import java.time.OffsetDateTime
import java.time.OffsetTime
import java.time.ZoneOffset
import javax.inject.Singleton

/**
 * Converter that extracts typed values from protobuf records and converts them to
 * EnrichedAirbyteValue with destination-specific coercion applied through the Coercer interface.
 */
@Singleton
class ProtobufConverter(
    private val coercer: ValueCoercer,
    private val validationResultHandler: ValidationResultHandler,
) : MediumConverter {

    private val decoder = AirbyteValueProtobufDecoder()

    override fun convert(input: ConversionInput): Map<String, AirbyteValue> {
        check(input.msg.rawData is DestinationRecordProtobufSource) {
            "The raw data must be a protobuf source."
        }
        checkNotNull(input.msg.rawData) {
            "The protobuf source containing data and metadata must be non-null."
        }
        val stream = input.msg.stream
        val fieldAccessors = stream.airbyteValueProxyFieldAccessors
        val data = input.msg.rawData.source.record.dataList

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

            val airbyteValue =
                extractTypedValue(
                    protobufValue = protobufValue,
                    accessor = accessor,
                    enrichedValue = enrichedValue,
                    streamName = stream.unmappedDescriptor.name
                )
            enrichedValue.abValue = airbyteValue

            val mappedValue = coercer.map(enrichedValue)
            val validatedValue =
                validationResultHandler.handle(
                    partitionKey = input.partitionKey,
                    stream = stream.mappedDescriptor,
                    result = coercer.validate(mappedValue),
                    value = mappedValue
                )

            allParsingFailures.addAll(validatedValue.changes)

            if (validatedValue.abValue !is NullValue || validatedValue.type !is UnknownType) {
                // Use column mapping from stream
                val columnName = stream.tableSchema.getFinalColumnName(accessor.name)
                result[columnName] = validatedValue.abValue
            }
        }

        addMetadataFields(result, input.msg, input.msg.rawData, allParsingFailures)

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
        enrichedValue: EnrichedAirbyteValue,
        streamName: String
    ): AirbyteValue {
        if (
            protobufValue == null || protobufValue.valueCase == AirbyteValueProtobuf.ValueCase.NULL
        ) {
            return NullValue
        }

        return try {
            // Step 1: Extract raw value from protobuf using the right method based on type
            val rawValue = extractRawValue(protobufValue, accessor, streamName)

            // Step 2: Decide final target type (check for destination override first)
            val targetClass =
                coercer.representAs(accessor.type) ?: getDefaultTargetClass(accessor.type)

            // Step 3: Create AirbyteValue of the target type using the raw value
            createAirbyteValue(rawValue, targetClass)
        } catch (e: ProtobufTypeMismatchException) {
            throw e
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
        accessor: FieldAccessor,
        streamName: String
    ): Any? {
        // Validate that the protobuf value type matches the expected AirbyteType
        validateProtobufType(protobufValue, accessor.type, streamName, accessor.name)

        // Use the centralized decoder for all scalar and temporal types
        val decodedValue = decoder.decode(protobufValue)

        // For complex types (arrays, objects, unions), handle separately
        return when (accessor.type) {
            is UnionType,
            is ArrayType,
            is ObjectType -> {
                if (decodedValue is String) {
                    // If decoder returned a JSON string, parse it
                    val jsonNode = Jsons.readTree(decodedValue.toByteArray())
                    jsonNode.toAirbyteValue()
                } else {
                    decodedValue
                }
            }
            is UnknownType -> null
            else -> decodedValue
        }
    }

    /**
     * Validates that the protobuf value case matches the expected AirbyteType.
     *
     * @throws ProtobufTypeMismatchException if there's a type mismatch
     */
    private fun validateProtobufType(
        value: AirbyteValueProtobuf,
        expectedType: io.airbyte.cdk.load.data.AirbyteType,
        streamName: String,
        columnName: String
    ) {
        val valueCase = value.valueCase

        // Null values are always valid
        if (
            valueCase == AirbyteValueProtobuf.ValueCase.NULL ||
                valueCase == AirbyteValueProtobuf.ValueCase.VALUE_NOT_SET ||
                valueCase == null
        ) {
            return
        }

        // Check if the value case matches the expected type
        val isValid =
            when (expectedType) {
                is StringType -> valueCase == AirbyteValueProtobuf.ValueCase.STRING
                is BooleanType -> valueCase == AirbyteValueProtobuf.ValueCase.BOOLEAN
                is IntegerType ->
                    valueCase == AirbyteValueProtobuf.ValueCase.INTEGER ||
                        valueCase == AirbyteValueProtobuf.ValueCase.BIG_INTEGER
                is NumberType ->
                    valueCase == AirbyteValueProtobuf.ValueCase.NUMBER ||
                        valueCase == AirbyteValueProtobuf.ValueCase.BIG_DECIMAL
                is DateType -> valueCase == AirbyteValueProtobuf.ValueCase.DATE
                is TimeTypeWithTimezone ->
                    valueCase == AirbyteValueProtobuf.ValueCase.TIME_WITH_TIMEZONE
                is TimeTypeWithoutTimezone ->
                    valueCase == AirbyteValueProtobuf.ValueCase.TIME_WITHOUT_TIMEZONE
                is TimestampTypeWithTimezone ->
                    valueCase == AirbyteValueProtobuf.ValueCase.TIMESTAMP_WITH_TIMEZONE
                is TimestampTypeWithoutTimezone ->
                    valueCase == AirbyteValueProtobuf.ValueCase.TIMESTAMP_WITHOUT_TIMEZONE
                is ArrayType,
                is ArrayTypeWithoutSchema,
                is ObjectType,
                is ObjectTypeWithEmptySchema,
                is ObjectTypeWithoutSchema -> valueCase == AirbyteValueProtobuf.ValueCase.JSON
                is UnionType -> {
                    // For union types, the value must match at least one of the options
                    valueCase == AirbyteValueProtobuf.ValueCase.JSON ||
                        expectedType.options.any { option ->
                            try {
                                validateProtobufType(value, option, streamName, columnName)
                                true
                            } catch (_: ProtobufTypeMismatchException) {
                                false
                            }
                        }
                }
                is UnknownType -> true // Unknown types accept any value
            }

        if (!isValid) {
            throw ProtobufTypeMismatchException(
                streamName = streamName,
                columnName = columnName,
                expectedType = expectedType,
                actualValueCase = valueCase
            )
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
            IntegerValue::class.java -> IntegerValue(rawValue as BigInteger)
            NumberValue::class.java -> NumberValue(rawValue as BigDecimal)
            DateValue::class.java ->
                when (rawValue) {
                    is LocalDate -> DateValue(rawValue)
                    is String -> DateValue(rawValue)
                    else -> DateValue(rawValue.toString())
                }
            TimestampWithTimezoneValue::class.java ->
                when (rawValue) {
                    is OffsetDateTime -> TimestampWithTimezoneValue(rawValue)
                    is String -> TimestampWithTimezoneValue(rawValue)
                    else -> TimestampWithTimezoneValue(rawValue.toString())
                }
            TimestampWithoutTimezoneValue::class.java ->
                when (rawValue) {
                    is java.time.LocalDateTime -> TimestampWithoutTimezoneValue(rawValue)
                    is String -> TimestampWithoutTimezoneValue(rawValue)
                    else -> TimestampWithoutTimezoneValue(rawValue.toString())
                }
            TimeWithTimezoneValue::class.java ->
                when (rawValue) {
                    is OffsetTime -> TimeWithTimezoneValue(rawValue)
                    is String -> TimeWithTimezoneValue(rawValue)
                    else -> TimeWithTimezoneValue(rawValue.toString())
                }
            TimeWithoutTimezoneValue::class.java ->
                when (rawValue) {
                    is LocalTime -> TimeWithoutTimezoneValue(rawValue)
                    is String -> TimeWithoutTimezoneValue(rawValue)
                    else -> TimeWithoutTimezoneValue(rawValue.toString())
                }
            NullValue::class.java -> NullValue
            AirbyteValue::class.java ->
                rawValue as AirbyteValue // Already an AirbyteValue (JSON types)
            else -> StringValue(rawValue.toString()) // Fallback to string
        }
    }
}
