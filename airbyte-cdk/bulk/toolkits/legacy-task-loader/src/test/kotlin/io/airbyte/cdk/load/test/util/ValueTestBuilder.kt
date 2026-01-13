/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.test.util

import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectValue
import java.util.UUID

@Suppress("UNCHECKED_CAST")
data class ValueTestBuilder<T : SchemaRecordBuilderType>(
    private val inputValues: ObjectValue = ObjectValue(linkedMapOf()),
    private val expectedValues: ObjectValue = ObjectValue(linkedMapOf()),
    private val schemaRecordBuilder: T = SchemaRecordBuilder<Root>() as T,
    private val parent: ValueTestBuilder<*>? = null
) {
    fun with(
        inputValue: AirbyteValue,
        inputSchema: AirbyteType,
        expectedValue: AirbyteValue = inputValue,
        nameOverride: String? = null,
        nullable: Boolean = false,
    ): ValueTestBuilder<T> {
        val name = nameOverride ?: UUID.randomUUID().toString()
        inputValues.values[name] = inputValue
        expectedValues.values[name] = expectedValue
        (schemaRecordBuilder as SchemaRecordBuilder<*>).with(
            FieldType(inputSchema, nullable),
            nameOverride = name
        )
        return this
    }

    @Suppress("UNCHECKED_CAST")
    fun withRecord(): ValueTestBuilder<T> {
        val name = UUID.randomUUID().toString()
        val inputRecord = ObjectValue(linkedMapOf())
        val outputRecord = ObjectValue(linkedMapOf())
        inputValues.values[name] = inputRecord
        expectedValues.values[name] = outputRecord
        return ValueTestBuilder(
            inputValues = inputRecord,
            expectedValues = outputRecord,
            schemaRecordBuilder =
                ((schemaRecordBuilder as SchemaRecordBuilder<*>).withRecord(nameOverride = name)
                    as T),
            parent = this
        )
    }

    @Suppress("UNCHECKED_CAST")
    fun endRecord(): ValueTestBuilder<T> {
        if (parent == null) {
            throw IllegalStateException("Cannot end record without parent")
        }
        return ValueTestBuilder(
            parent.inputValues,
            parent.expectedValues,
            ((schemaRecordBuilder as SchemaRecordBuilder<*>).endRecord() as T),
            parent.parent
        )
    }

    fun build(): Triple<ObjectValue, ObjectType, ObjectValue> {
        if (parent != null) {
            throw IllegalStateException("Cannot build nested schema")
        }
        return Triple(
            inputValues,
            (schemaRecordBuilder as SchemaRecordBuilder<*>).build().first,
            expectedValues
        )
    }
}
