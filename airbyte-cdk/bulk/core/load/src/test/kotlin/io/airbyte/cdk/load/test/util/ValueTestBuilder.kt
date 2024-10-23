/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.test.util

import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectValue
import java.util.UUID

data class ValueTestBuilder(
    private val inputValues: ObjectValue = ObjectValue(linkedMapOf()),
    private val expectedValues: ObjectValue = ObjectValue(linkedMapOf()),
    private val schemaTestBuilder: SchemaTestBuilder = SchemaTestBuilder(),
    private val parent: ValueTestBuilder? = null
) {
    fun with(
        inputValue: AirbyteValue,
        inputSchema: AirbyteType,
        expectedValue: AirbyteValue = inputValue,
        nameOverride: String? = null
    ): ValueTestBuilder {
        val name = nameOverride ?: UUID.randomUUID().toString()
        inputValues.values[name] = inputValue
        expectedValues.values[name] = expectedValue
        schemaTestBuilder.with(inputSchema, nameOverride = name)
        return this
    }

    fun withRecord(): ValueTestBuilder {
        val name = UUID.randomUUID().toString()
        val inputRecord = ObjectValue(linkedMapOf())
        val outputRecord = ObjectValue(linkedMapOf())
        inputValues.values[name] = inputRecord
        expectedValues.values[name] = outputRecord
        return ValueTestBuilder(
            inputValues = inputRecord,
            expectedValues = outputRecord,
            schemaTestBuilder = schemaTestBuilder.withRecord(nameOverride = name),
            parent = this
        )
    }

    fun endRecord(): ValueTestBuilder {
        if (parent == null) {
            throw IllegalStateException("Cannot end record without parent")
        }
        return parent.copy(schemaTestBuilder = schemaTestBuilder.endRecord())
    }

    fun build(): Triple<ObjectValue, ObjectType, ObjectValue> {
        if (parent != null) {
            throw IllegalStateException("Cannot build nested schema")
        }
        return Triple(inputValues, schemaTestBuilder.build().first, expectedValues)
    }
}
