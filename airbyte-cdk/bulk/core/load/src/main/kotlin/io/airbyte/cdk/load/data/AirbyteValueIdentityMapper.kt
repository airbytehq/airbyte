/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

import io.airbyte.cdk.load.message.Meta
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Change
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Reason

interface AirbyteValueMapper {
    fun map(
        value: AirbyteValue,
        schema: AirbyteType,
        changes: List<Meta.Change> = emptyList()
    ): Pair<AirbyteValue, List<Meta.Change>>
}

/** An optimized identity mapper that just passes through. */
class AirbyteValueNoopMapper : AirbyteValueMapper {
    override fun map(
        value: AirbyteValue,
        schema: AirbyteType,
        changes: List<Meta.Change>
    ): Pair<AirbyteValue, List<Meta.Change>> = value to changes
}

open class AirbyteValueIdentityMapper : AirbyteValueMapper {
    data class Context(
        val nullable: Boolean = false,
        val path: List<String> = emptyList(),
        val changes: MutableSet<Meta.Change> = mutableSetOf(),
    )

    override fun map(
        value: AirbyteValue,
        schema: AirbyteType,
        changes: List<Meta.Change>
    ): Pair<AirbyteValue, List<Meta.Change>> =
        mapInner(value, schema, Context(changes = changes.toMutableSet())).let {
            it.first to it.second.changes.toList()
        }

    fun nulledOut(
        schema: AirbyteType,
        context: Context,
        reason: Reason = Reason.DESTINATION_SERIALIZATION_ERROR
    ): Pair<AirbyteValue, Context> {
        context.changes.add(Meta.Change(context.path.joinToString("."), Change.NULLED, reason))
        return mapInner(NullValue, schema, context)
    }

    fun mapInner(
        value: AirbyteValue,
        schema: AirbyteType,
        context: Context,
    ): Pair<AirbyteValue, Context> =
        if (value is NullValue) {
            if (!context.nullable) {
                throw IllegalStateException(
                    "null value for non-nullable field at path: ${context.path.joinToString(".")}"
                )
            }
            mapNull(context)
        } else
            try {
                when (schema) {
                    is ObjectType -> mapObject(value, schema, context)
                    is ObjectTypeWithoutSchema -> mapObjectWithoutSchema(value, schema, context)
                    is ObjectTypeWithEmptySchema -> mapObjectWithEmptySchema(value, schema, context)
                    is ArrayType -> mapArray(value, schema, context)
                    is ArrayTypeWithoutSchema -> mapArrayWithoutSchema(value, schema, context)
                    is UnionType -> mapUnion(value, schema, context)
                    is BooleanType -> mapBoolean(value, context)
                    is NumberType -> mapNumber(value, context)
                    is StringType -> mapString(value, context)
                    is IntegerType -> mapInteger(value, context)
                    is DateType -> mapDate(value, context)
                    is TimeTypeWithTimezone -> mapTimeWithTimezone(value, context)
                    is TimeTypeWithoutTimezone -> mapTimeWithoutTimezone(value, context)
                    is TimestampTypeWithTimezone -> mapTimestampWithTimezone(value, context)
                    is TimestampTypeWithoutTimezone -> mapTimestampWithoutTimezone(value, context)
                    is UnknownType -> mapUnknown(value, context)
                }
            } catch (e: Exception) {
                nulledOut(schema, context)
            }

    open fun mapObject(
        value: AirbyteValue,
        schema: ObjectType,
        context: Context
    ): Pair<AirbyteValue, Context> {
        if (value !is ObjectValue) {
            return value to context
        }
        val values = LinkedHashMap<String, AirbyteValue>()
        schema.properties.forEach { (name, field) ->
            values[name] =
                mapInner(
                        value.values[name] ?: NullValue,
                        field.type,
                        context.copy(path = context.path + name, nullable = field.nullable)
                    )
                    .first
        }
        return ObjectValue(values) to context
    }

    open fun mapObjectWithoutSchema(
        value: AirbyteValue,
        schema: ObjectTypeWithoutSchema,
        context: Context
    ): Pair<AirbyteValue, Context> = value to context

    open fun mapObjectWithEmptySchema(
        value: AirbyteValue,
        schema: ObjectTypeWithEmptySchema,
        context: Context
    ): Pair<AirbyteValue, Context> = value to context

    open fun mapArray(
        value: AirbyteValue,
        schema: ArrayType,
        context: Context
    ): Pair<AirbyteValue, Context> {
        if (value !is ArrayValue) {
            return value to context
        }
        val mapped =
            value.values.mapIndexed { index, element ->
                mapInner(
                        element,
                        schema.items.type,
                        context.copy(
                            path = context.path + "[$index]",
                            nullable = schema.items.nullable
                        )
                    )
                    .first
            }
        return ArrayValue(mapped) to context
    }

    open fun mapArrayWithoutSchema(
        value: AirbyteValue,
        schema: ArrayTypeWithoutSchema,
        context: Context
    ): Pair<AirbyteValue, Context> = value to context

    open fun mapUnion(
        value: AirbyteValue,
        schema: UnionType,
        context: Context
    ): Pair<AirbyteValue, Context> {
        /*
           This mapper should not perform validation, so make a best-faith effort to recurse,
           but if nothing matches the union, pass the value through unchanged. If clients validated
           upstream, then this must match. If they did not, they won't have anything any more
           wrong than they started with.
        */
        schema.options.forEach {
            if (optionMatches(it, value)) {
                return mapInner(value, it, context)
            }
        }
        return value to context
    }

    private fun optionMatches(schema: AirbyteType, value: AirbyteValue): Boolean {
        return when (schema) {
            is StringType -> value is StringValue
            is BooleanType -> value is BooleanValue
            is IntegerType -> value is IntegerValue
            is NumberType -> value is NumberValue
            is ArrayTypeWithoutSchema,
            is ArrayType -> value is ArrayValue
            is ObjectType,
            is ObjectTypeWithoutSchema,
            is ObjectTypeWithEmptySchema -> value is ObjectValue
            is DateType -> value is DateValue
            is TimeTypeWithTimezone -> value is TimeWithTimezoneValue
            is TimeTypeWithoutTimezone -> value is TimeWithoutTimezoneValue
            is TimestampTypeWithTimezone -> value is TimestampWithTimezoneValue
            is TimestampTypeWithoutTimezone -> value is TimestampWithoutTimezoneValue
            is UnionType -> schema.options.any { optionMatches(it, value) }
            is UnknownType -> false
        }
    }

    open fun mapBoolean(value: AirbyteValue, context: Context): Pair<AirbyteValue, Context> =
        value to context

    open fun mapNumber(value: AirbyteValue, context: Context): Pair<AirbyteValue, Context> =
        value to context

    open fun mapString(value: AirbyteValue, context: Context): Pair<AirbyteValue, Context> =
        value to context

    open fun mapInteger(value: AirbyteValue, context: Context): Pair<AirbyteValue, Context> =
        value to context

    /**
     * Time types are only allowed to be strings on the wire, but can be Int/egerValue if passed
     * through [TimeStringToInteger].
     */
    open fun mapDate(value: AirbyteValue, context: Context): Pair<AirbyteValue, Context> =
        value to context

    open fun mapTimeWithTimezone(
        value: AirbyteValue,
        context: Context
    ): Pair<AirbyteValue, Context> = value to context

    open fun mapTimeWithoutTimezone(
        value: AirbyteValue,
        context: Context
    ): Pair<AirbyteValue, Context> = value to context

    open fun mapTimestampWithTimezone(
        value: AirbyteValue,
        context: Context
    ): Pair<AirbyteValue, Context> = value to context

    open fun mapTimestampWithoutTimezone(
        value: AirbyteValue,
        context: Context
    ): Pair<AirbyteValue, Context> = value to context

    open fun mapNull(context: Context): Pair<AirbyteValue, Context> = NullValue to context

    open fun mapUnknown(value: AirbyteValue, context: Context): Pair<AirbyteValue, Context> =
        value to context
}
