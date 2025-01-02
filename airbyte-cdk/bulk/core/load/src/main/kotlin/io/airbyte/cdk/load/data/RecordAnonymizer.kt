/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

class RecordAnonymizer : AirbyteValueIdentityMapper() {
    override fun mapString(value: AirbyteValue, context: Context): Pair<AirbyteValue, Context> {
        return StringValue(value.javaClass.simpleName) to context
    }

    override fun mapBoolean(value: AirbyteValue, context: Context): Pair<AirbyteValue, Context> {
        return StringValue(value.javaClass.simpleName) to context
    }

    override fun mapInteger(value: AirbyteValue, context: Context): Pair<AirbyteValue, Context> {
        return StringValue(value.javaClass.simpleName) to context
    }

    override fun mapNumber(value: AirbyteValue, context: Context): Pair<AirbyteValue, Context> {
        return StringValue(value.javaClass.simpleName) to context
    }

    override fun mapDate(value: AirbyteValue, context: Context): Pair<AirbyteValue, Context> {
        return StringValue(value.javaClass.simpleName) to context
    }

    override fun mapTimestampWithTimezone(
        value: AirbyteValue,
        context: Context
    ): Pair<AirbyteValue, Context> {
        return StringValue(value.javaClass.simpleName) to context
    }

    override fun mapTimestampWithoutTimezone(
        value: AirbyteValue,
        context: Context
    ): Pair<AirbyteValue, Context> {
        return StringValue(value.javaClass.simpleName) to context
    }

    override fun mapTimeWithTimezone(
        value: AirbyteValue,
        context: Context
    ): Pair<AirbyteValue, Context> {
        return StringValue(value.javaClass.simpleName) to context
    }

    override fun mapTimeWithoutTimezone(
        value: AirbyteValue,
        context: Context
    ): Pair<AirbyteValue, Context> {
        return StringValue(value.javaClass.simpleName) to context
    }

    override fun mapArrayWithoutSchema(
        value: AirbyteValue,
        schema: ArrayTypeWithoutSchema,
        context: Context
    ): Pair<AirbyteValue, Context> {
        return StringValue(value.javaClass.simpleName) to context
    }

    override fun mapObjectWithoutSchema(
        value: AirbyteValue,
        schema: ObjectTypeWithoutSchema,
        context: Context
    ): Pair<AirbyteValue, Context> {
        return StringValue(value.javaClass.simpleName) to context
    }

    override fun mapObjectWithEmptySchema(
        value: AirbyteValue,
        schema: ObjectTypeWithEmptySchema,
        context: Context
    ): Pair<AirbyteValue, Context> {
        return StringValue(value.javaClass.simpleName) to context
    }
}

fun AirbyteValue.anonymized(schema: AirbyteType): AirbyteValue {
    val anonymizer = RecordAnonymizer()
    return anonymizer.map(this, schema).first
}
