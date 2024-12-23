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
                    is ObjectType -> mapObject(value as ObjectValue, schema, context)
                    is ObjectTypeWithoutSchema -> mapObjectWithoutSchema(value, schema, context)
                    is ObjectTypeWithEmptySchema -> mapObjectWithEmptySchema(value, schema, context)
                    is ArrayType -> mapArray(value as ArrayValue, schema, context)
                    is ArrayTypeWithoutSchema -> mapArrayWithoutSchema(value, schema, context)
                    is UnionType -> mapUnion(value, schema, context)
                    is BooleanType -> mapBoolean(value as BooleanValue, context)
                    is NumberType -> mapNumber(value as NumberValue, context)
                    is StringType -> mapString(value as StringValue, context)
                    is IntegerType -> mapInteger(value as IntegerValue, context)
                    is DateType -> mapDate(value, context)
                    is TimeTypeWithTimezone ->
                        mapTimeWithTimezone(
                            value,
                            context,
                        )
                    is TimeTypeWithoutTimezone ->
                        mapTimeWithoutTimezone(
                            value,
                            context,
                        )
                    is TimestampTypeWithTimezone -> mapTimestampWithTimezone(value, context)
                    is TimestampTypeWithoutTimezone -> mapTimestampWithoutTimezone(value, context)
                    is UnknownType -> mapUnknown(value as UnknownValue, context)
                }
            } catch (e: Exception) {
                nulledOut(schema, context)
            }

    open fun mapObject(
        value: ObjectValue,
        schema: ObjectType,
        context: Context
    ): Pair<AirbyteValue, Context> {
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
        value: ArrayValue,
        schema: ArrayType,
        context: Context
    ): Pair<AirbyteValue, Context> {
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
    ): Pair<AirbyteValue, Context> = value to context

    open fun mapBoolean(value: BooleanValue, context: Context): Pair<AirbyteValue, Context> =
        value to context

    open fun mapNumber(value: NumberValue, context: Context): Pair<AirbyteValue, Context> =
        value to context

    open fun mapString(value: StringValue, context: Context): Pair<AirbyteValue, Context> =
        value to context

    open fun mapInteger(value: IntegerValue, context: Context): Pair<AirbyteValue, Context> =
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

    open fun mapUnknown(value: UnknownValue, context: Context): Pair<AirbyteValue, Context> =
        value to context
}
