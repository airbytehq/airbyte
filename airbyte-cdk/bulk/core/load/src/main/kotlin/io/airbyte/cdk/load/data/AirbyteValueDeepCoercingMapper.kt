/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

import io.airbyte.cdk.load.util.serializeToString
import java.math.BigDecimal
import java.math.BigInteger
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.OffsetDateTime
import java.time.OffsetTime
import java.time.ZoneOffset
import java.time.ZonedDateTime
import java.time.format.DateTimeFormatter

/**
 * A mapper which coerces ALL values against the schema. This mapper MUST NOT be called after any
 * mapper that returns non-native-JSON types (date, timestamp, etc.), or any mapper that causes the
 * values to become misaligned with the schema (e.g. [AirbyteSchemaNoopMapper] +
 * [SchemalessValuesToJsonString]).
 *
 * If this mapper is included in a [MapperPipeline], it SHOULD be preceded by a [MergeUnions]
 * mapper. Not including this mapper may result in strange behavior when coercing union types.
 *
 * This mapper performs common-sense type coercions. For example, it will promote IntegerValue to
 * NumberValue, or parse StringValue to TimestampValue.
 */
class AirbyteValueDeepCoercingMapper : AirbyteValueIdentityMapper() {
    override fun mapObject(
        value: AirbyteValue,
        schema: ObjectType,
        context: Context
    ): Pair<AirbyteValue, Context> =
        // force to object, and then use the superclass recursion
        requireType<ObjectValue>(value, schema, context) { super.mapObject(it, schema, context) }

    override fun mapObjectWithEmptySchema(
        value: AirbyteValue,
        schema: ObjectTypeWithEmptySchema,
        context: Context
    ): Pair<AirbyteValue, Context> = requireType<ObjectValue>(value, schema, context)

    override fun mapObjectWithoutSchema(
        value: AirbyteValue,
        schema: ObjectTypeWithoutSchema,
        context: Context
    ): Pair<AirbyteValue, Context> = requireType<ObjectValue>(value, schema, context)

    override fun mapArray(
        value: AirbyteValue,
        schema: ArrayType,
        context: Context
    ): Pair<AirbyteValue, Context> =
        // force to array, and then use the superclass recursion
        requireType<ArrayValue>(value, schema, context) { super.mapArray(it, schema, context) }

    override fun mapArrayWithoutSchema(
        value: AirbyteValue,
        schema: ArrayTypeWithoutSchema,
        context: Context
    ): Pair<AirbyteValue, Context> = requireType<ArrayValue>(value, schema, context)

    override fun mapBoolean(value: AirbyteValue, context: Context): Pair<AirbyteValue, Context> =
        requireType<BooleanValue>(value, BooleanType, context)

    override fun mapNumber(value: AirbyteValue, context: Context): Pair<AirbyteValue, Context> =
        when (value) {
            is NumberValue -> value to context
            is IntegerValue -> NumberValue(value.value.toBigDecimal()) to context
            is StringValue -> NumberValue(BigDecimal(value.value)) to context
            else -> nulledOut(NumberType, context)
        }

    override fun mapInteger(value: AirbyteValue, context: Context): Pair<AirbyteValue, Context> =
        when (value) {
            // Maybe we should truncate non-int values?
            // But to match existing behavior, let's just null for now.
            is NumberValue -> IntegerValue(value.value.toBigIntegerExact()) to context
            is IntegerValue -> value to context
            is StringValue -> IntegerValue(BigInteger(value.value)) to context
            else -> nulledOut(IntegerType, context)
        }

    override fun mapString(value: AirbyteValue, context: Context): Pair<AirbyteValue, Context> {
        val stringified =
            when (value) {
                // this should never happen, because we handle `value is NullValue`
                // in the top-level if statement
                NullValue -> throw IllegalStateException("Unexpected NullValue")
                is StringValue -> value.value
                is NumberValue -> value.value.toString()
                is IntegerValue -> value.value.toString()
                is BooleanValue -> value.value.toString()
                is ArrayValue,
                is ObjectValue -> value.serializeToString()
                // JsonToAirbyteValue never outputs these values, so don't handle them.
                is DateValue,
                is TimeWithTimezoneValue,
                is TimeWithoutTimezoneValue,
                is TimestampWithTimezoneValue,
                is TimestampWithoutTimezoneValue,
                is UnknownValue ->
                    throw IllegalArgumentException(
                        "Invalid value type ${value.javaClass.canonicalName}"
                    )
            }
        return StringValue(stringified) to context
    }

    override fun mapDate(value: AirbyteValue, context: Context): Pair<AirbyteValue, Context> =
        requireType<StringValue>(value, DateType, context) {
            DateValue(LocalDate.parse(it.value, DATE_TIME_FORMATTER)) to context
        }

    override fun mapTimeWithTimezone(
        value: AirbyteValue,
        context: Context
    ): Pair<AirbyteValue, Context> =
        requireType<StringValue>(value, TimeTypeWithTimezone, context) {
            val ot =
                try {
                    OffsetTime.parse(it.value, TIME_FORMATTER)
                } catch (e: Exception) {
                    LocalTime.parse(it.value, TIME_FORMATTER).atOffset(ZoneOffset.UTC)
                }
            TimeWithTimezoneValue(ot) to context
        }

    override fun mapTimeWithoutTimezone(
        value: AirbyteValue,
        context: Context
    ): Pair<AirbyteValue, Context> =
        requireType<StringValue>(value, TimeTypeWithoutTimezone, context) {
            TimeWithoutTimezoneValue(LocalTime.parse(it.value, TIME_FORMATTER)) to context
        }

    override fun mapTimestampWithTimezone(
        value: AirbyteValue,
        context: Context
    ): Pair<AirbyteValue, Context> =
        requireType<StringValue>(value, TimestampTypeWithTimezone, context) {
            TimestampWithTimezoneValue(offsetDateTime(it)) to context
        }

    override fun mapTimestampWithoutTimezone(
        value: AirbyteValue,
        context: Context
    ): Pair<AirbyteValue, Context> =
        requireType<StringValue>(value, TimestampTypeWithoutTimezone, context) {
            TimestampWithoutTimezoneValue(offsetDateTime(it).toLocalDateTime()) to context
        }

    private fun offsetDateTime(it: StringValue): OffsetDateTime {
        val odt =
            try {
                ZonedDateTime.parse(it.value, DATE_TIME_FORMATTER).toOffsetDateTime()
            } catch (e: Exception) {
                LocalDateTime.parse(it.value, DATE_TIME_FORMATTER).atOffset(ZoneOffset.UTC)
            }
        return odt
    }

    override fun mapUnion(
        value: AirbyteValue,
        schema: UnionType,
        context: Context
    ): Pair<AirbyteValue, Context> =
        if (schema.options.isEmpty()) {
            nulledOut(schema, context)
        } else {
            val option =
                schema.options.find { matchesStrictly(value, it) }
                    ?: schema.options.find { matchesPermissively(value, it) }
                        ?: throw IllegalArgumentException(
                        "No matching union option in ${schema.options} for ${value::class.java.canonicalName}",
                    )
            mapInner(value, option, context)
        }

    private fun matchesStrictly(value: AirbyteValue, schema: AirbyteType): Boolean =
        when (schema) {
            is ArrayType,
            is ArrayTypeWithoutSchema -> value is ArrayValue
            is BooleanType -> value is BooleanValue
            is DateType -> value is StringValue
            is IntegerType -> value is IntegerValue
            is NumberType -> value is NumberValue
            is ObjectType,
            is ObjectTypeWithoutSchema,
            is ObjectTypeWithEmptySchema -> value is ObjectValue
            is StringType -> value is StringValue
            is TimeTypeWithTimezone,
            is TimeTypeWithoutTimezone,
            is TimestampTypeWithTimezone,
            is TimestampTypeWithoutTimezone -> value is StringValue
            is UnionType -> schema.options.any { matchesStrictly(value, it) }
            is UnknownType -> false
        }

    private fun matchesPermissively(value: AirbyteValue, schema: AirbyteType): Boolean {
        val (mappedValue, _) = mapInner(value, schema, Context(nullable = true))
        return mappedValue !is NullValue
    }

    private inline fun <reified T : AirbyteValue> requireType(
        value: AirbyteValue,
        schema: AirbyteType,
        context: Context,
        f: (T) -> Pair<AirbyteValue, Context> = { value to context },
    ): Pair<AirbyteValue, Context> {
        return if (value is T) {
            f(value)
        } else {
            nulledOut(schema, context)
        }
    }

    companion object {
        val DATE_TIME_FORMATTER: DateTimeFormatter =
            DateTimeFormatter.ofPattern(
                "[yyyy][yy]['-']['/']['.'][' '][MMM][MM][M]['-']['/']['.'][' '][dd][d][[' '][G]][[' ']['T']HH:mm[':'ss[.][SSSSSS][SSSSS][SSSS][SSS][' '][z][zzz][Z][O][x][XXX][XX][X][[' '][G]]]]"
            )
        val TIME_FORMATTER: DateTimeFormatter =
            DateTimeFormatter.ofPattern(
                "HH:mm[':'ss[.][SSSSSS][SSSSS][SSSS][SSS][' '][z][zzz][Z][O][x][XXX][XX][X]]"
            )
    }
}
