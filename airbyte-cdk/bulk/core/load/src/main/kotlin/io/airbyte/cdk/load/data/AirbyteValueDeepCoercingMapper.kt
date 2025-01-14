/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

import io.airbyte.cdk.load.message.Meta
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Change
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Reason
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
class AirbyteValueDeepCoercingMapper(
    recurseIntoObjects: Boolean,
    recurseIntoArrays: Boolean,
    recurseIntoUnions: Boolean,
) :
    AirbyteValueIdentityMapper(
        recurseIntoObjects = recurseIntoObjects,
        recurseIntoArrays = recurseIntoArrays,
        recurseIntoUnions = recurseIntoUnions,
    ) {
    override fun mapObject(
        value: AirbyteValue,
        schema: ObjectType,
        context: Context,
    ): Pair<AirbyteValue, Context> =
        // We should inspect the object's fields if we're doing full recursion,
        // or if this is the root object.
        if (recurseIntoObjects || context.path.isEmpty()) {
            // force to object, and then use the superclass recursion
            AirbyteValueCoercer.coerceObject(value)?.let { super.mapObject(it, schema, context) }
                ?: nulledOut(schema, context)
        } else {
            // otherwise, try to get an ObjectValue out of this value, but don't recurse.
            withContext(AirbyteValueCoercer.coerceObject(value), context)
        }

    override fun mapObjectWithEmptySchema(
        value: AirbyteValue,
        schema: ObjectTypeWithEmptySchema,
        context: Context
    ): Pair<AirbyteValue, Context> = withContext(AirbyteValueCoercer.coerceObject(value), context)

    override fun mapObjectWithoutSchema(
        value: AirbyteValue,
        schema: ObjectTypeWithoutSchema,
        context: Context
    ): Pair<AirbyteValue, Context> = withContext(AirbyteValueCoercer.coerceObject(value), context)

    override fun mapArray(
        value: AirbyteValue,
        schema: ArrayType,
        context: Context
    ): Pair<AirbyteValue, Context> =
        // similar to mapObject, recurse if needed.
        // Realistically, the root node is _never_ an array, i.e. `context.path.isEmpty()` is
        // always false.
        // But might as well be consistent.
        if (recurseIntoArrays || context.path.isEmpty()) {
            // force to array, and then use the superclass recursion
            AirbyteValueCoercer.coerceArray(value)?.let { super.mapArray(it, schema, context) }
                ?: nulledOut(schema, context)
        } else {
            withContext(AirbyteValueCoercer.coerceArray(value), context)
        }

    override fun mapArrayWithoutSchema(
        value: AirbyteValue,
        schema: ArrayTypeWithoutSchema,
        context: Context
    ): Pair<AirbyteValue, Context> = withContext(AirbyteValueCoercer.coerceArray(value), context)

    override fun mapBoolean(value: AirbyteValue, context: Context): Pair<AirbyteValue, Context> =
        withContext(AirbyteValueCoercer.coerceBoolean(value), context)

    override fun mapNumber(value: AirbyteValue, context: Context): Pair<AirbyteValue, Context> =
        withContext(AirbyteValueCoercer.coerceNumber(value), context)

    override fun mapInteger(value: AirbyteValue, context: Context): Pair<AirbyteValue, Context> =
        withContext(AirbyteValueCoercer.coerceInt(value), context)

    override fun mapString(value: AirbyteValue, context: Context): Pair<AirbyteValue, Context> =
        withContext(AirbyteValueCoercer.coerceString(value), context)

    override fun mapDate(value: AirbyteValue, context: Context): Pair<AirbyteValue, Context> =
        withContext(AirbyteValueCoercer.coerceDate(value), context)

    override fun mapTimeWithTimezone(
        value: AirbyteValue,
        context: Context
    ): Pair<AirbyteValue, Context> = withContext(AirbyteValueCoercer.coerceTimeTz(value), context)

    override fun mapTimeWithoutTimezone(
        value: AirbyteValue,
        context: Context
    ): Pair<AirbyteValue, Context> = withContext(AirbyteValueCoercer.coerceTimeNtz(value), context)

    override fun mapTimestampWithTimezone(
        value: AirbyteValue,
        context: Context
    ): Pair<AirbyteValue, Context> =
        withContext(AirbyteValueCoercer.coerceTimestampTz(value), context)

    override fun mapTimestampWithoutTimezone(
        value: AirbyteValue,
        context: Context
    ): Pair<AirbyteValue, Context> =
        withContext(AirbyteValueCoercer.coerceTimestampNtz(value), context)

    override fun mapUnion(
        value: AirbyteValue,
        schema: UnionType,
        context: Context
    ): Pair<AirbyteValue, Context> =
        if (!recurseIntoUnions) {
            value to context
        } else if (schema.options.isEmpty()) {
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

    private fun withContext(value: AirbyteValue?, context: Context): Pair<AirbyteValue, Context> =
        if (value != null) {
            // Note: This only triggers if the value was explicitly nulled out.
            // If the value was originally null, then value would be NullValue.i
            value to context
        } else {
            context.changes.add(
                Meta.Change(
                    context.path.joinToString("."),
                    Change.NULLED,
                    Reason.DESTINATION_SERIALIZATION_ERROR
                )
            )
            NullValue to context
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
