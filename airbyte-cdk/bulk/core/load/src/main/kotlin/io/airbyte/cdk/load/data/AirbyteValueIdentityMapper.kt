/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

import io.airbyte.cdk.load.message.DestinationRecord
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Change
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Reason

interface AirbyteValueMapper {
    val collectedChanges: List<DestinationRecord.Change>
    fun map(
        value: AirbyteValue,
        schema: AirbyteType,
        path: List<String> = emptyList(),
        nullable: Boolean = false
    ): AirbyteValue
}

/** An optimized identity mapper that just passes through. */
class AirbyteValueNoopMapper : AirbyteValueMapper {
    override val collectedChanges: List<DestinationRecord.Change> = emptyList()

    override fun map(
        value: AirbyteValue,
        schema: AirbyteType,
        path: List<String>,
        nullable: Boolean
    ): AirbyteValue = value
}

open class AirbyteValueIdentityMapper : AirbyteValueMapper {
    override val collectedChanges: List<DestinationRecord.Change>
        get() = changes.toList().also { changes.clear() }

    private val changes: MutableList<DestinationRecord.Change> = mutableListOf()

    private fun collectFailure(
        path: List<String>,
        reason: Reason = Reason.DESTINATION_SERIALIZATION_ERROR
    ) {
        val joined = path.joinToString(".")
        if (changes.none { it.field == joined }) {
            changes.add(DestinationRecord.Change(path.joinToString("."), Change.NULLED, reason))
        }
    }

    override fun map(
        value: AirbyteValue,
        schema: AirbyteType,
        path: List<String>,
        nullable: Boolean,
    ): AirbyteValue =
        if (value is NullValue) {
            if (!nullable) {
                throw IllegalStateException(
                    "null value for non-nullable field at path: ${path.joinToString(".")}"
                )
            }
            mapNull(path)
        } else
            try {
                when (schema) {
                    is ObjectType -> mapObject(value as ObjectValue, schema, path)
                    is ObjectTypeWithoutSchema ->
                        mapObjectWithoutSchema(value as ObjectValue, schema, path)
                    is ObjectTypeWithEmptySchema ->
                        mapObjectWithEmptySchema(value as ObjectValue, schema, path)
                    is ArrayType -> mapArray(value as ArrayValue, schema, path)
                    is ArrayTypeWithoutSchema ->
                        mapArrayWithoutSchema(value as ArrayValue, schema, path)
                    is UnionType -> mapUnion(value, schema, path)
                    is BooleanType -> mapBoolean(value as BooleanValue, path)
                    is NumberType -> mapNumber(value as NumberValue, path)
                    is StringType -> mapString(value as StringValue, path)
                    is IntegerType -> mapInteger(value as IntegerValue, path)
                    is DateType -> mapDate(value as DateValue, path)
                    is TimeTypeWithTimezone ->
                        mapTimeWithTimezone(
                            value as TimeValue,
                            path,
                        )
                    is TimeTypeWithoutTimezone ->
                        mapTimeWithoutTimezone(
                            value as TimeValue,
                            path,
                        )
                    is TimestampTypeWithTimezone ->
                        mapTimestampWithTimezone(value as TimestampValue, path)
                    is TimestampTypeWithoutTimezone ->
                        mapTimestampWithoutTimezone(value as TimestampValue, path)
                    is UnknownType -> mapUnknown(value as UnknownValue, path)
                }
            } catch (e: Exception) {
                collectFailure(path)
                map(NullValue, schema, path, nullable)
            }

    open fun mapObject(value: ObjectValue, schema: ObjectType, path: List<String>): AirbyteValue {
        val values = LinkedHashMap<String, AirbyteValue>()
        schema.properties.forEach { (name, field) ->
            values[name] =
                map(value.values[name] ?: NullValue, field.type, path + name, field.nullable)
        }
        return ObjectValue(values)
    }

    open fun mapObjectWithoutSchema(
        value: ObjectValue,
        schema: ObjectTypeWithoutSchema,
        path: List<String>
    ): AirbyteValue = value

    open fun mapObjectWithEmptySchema(
        value: ObjectValue,
        schema: ObjectTypeWithEmptySchema,
        path: List<String>
    ): AirbyteValue = value

    open fun mapArray(value: ArrayValue, schema: ArrayType, path: List<String>): AirbyteValue {
        return ArrayValue(
            value.values.mapIndexed { index, element ->
                map(element, schema.items.type, path + "[$index]", schema.items.nullable)
            }
        )
    }

    open fun mapArrayWithoutSchema(
        value: ArrayValue,
        schema: ArrayTypeWithoutSchema,
        path: List<String>
    ): AirbyteValue = value

    open fun mapUnion(value: AirbyteValue, schema: UnionType, path: List<String>): AirbyteValue =
        value

    open fun mapBoolean(value: BooleanValue, path: List<String>): AirbyteValue = value

    open fun mapNumber(value: NumberValue, path: List<String>): AirbyteValue = value

    open fun mapString(value: StringValue, path: List<String>): AirbyteValue = value

    open fun mapInteger(value: IntegerValue, path: List<String>): AirbyteValue = value

    open fun mapDate(value: DateValue, path: List<String>): AirbyteValue = value

    open fun mapTimeWithTimezone(value: TimeValue, path: List<String>): AirbyteValue = value

    open fun mapTimeWithoutTimezone(value: TimeValue, path: List<String>): AirbyteValue = value

    open fun mapTimestampWithTimezone(value: TimestampValue, path: List<String>): AirbyteValue =
        value

    open fun mapTimestampWithoutTimezone(value: TimestampValue, path: List<String>): AirbyteValue =
        value

    open fun mapNull(path: List<String>): AirbyteValue = NullValue

    open fun mapUnknown(value: UnknownValue, path: List<String>): AirbyteValue = value
}
