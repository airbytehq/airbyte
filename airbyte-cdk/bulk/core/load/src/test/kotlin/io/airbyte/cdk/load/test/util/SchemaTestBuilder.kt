/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.test.util

import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.ObjectType
import java.util.*
import kotlin.collections.LinkedHashMap

class SchemaTestBuilder(
    val inputSchema: ObjectType = ObjectType(properties = LinkedHashMap()),
    val expectedSchema: ObjectType = ObjectType(properties = LinkedHashMap()),
    val parent: SchemaTestBuilder? = null
) {

    fun with(
        given: FieldType,
        expected: FieldType = given,
        nameOverride: String? = null
    ): SchemaTestBuilder {
        val name = nameOverride ?: UUID.randomUUID().toString()
        inputSchema.properties[name] = given
        expectedSchema.properties[name] = expected
        return this
    }

    fun with(
        given: AirbyteType,
        expected: AirbyteType = given,
        nameOverride: String? = null
    ): SchemaTestBuilder {
        return with(FieldType(given, false), FieldType(expected, false), nameOverride)
    }

    fun withRecord(nullable: Boolean = false, nameOverride: String? = null): SchemaTestBuilder {
        val name = nameOverride ?: UUID.randomUUID().toString()
        val inputRecord = ObjectType(properties = LinkedHashMap())
        val outputRecord = ObjectType(properties = LinkedHashMap())
        inputSchema.properties[name] = FieldType(inputRecord, nullable = nullable)
        expectedSchema.properties[name] = FieldType(outputRecord, nullable = nullable)
        return SchemaTestBuilder(
            inputSchema = inputRecord,
            expectedSchema = outputRecord,
            parent = this
        )
    }

    fun endRecord(): SchemaTestBuilder {
        if (parent == null) {
            throw IllegalStateException("Cannot end record without parent")
        }
        return parent
    }

    fun build(): Pair<ObjectType, ObjectType> {
        if (parent != null) {
            throw IllegalStateException("Cannot build nested schema")
        }
        return Pair(inputSchema, expectedSchema)
    }
}
