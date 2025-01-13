/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.test.util

import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.UnionType
import java.util.*
import kotlin.collections.LinkedHashMap

sealed interface SchemaRecordBuilderType

class Root : SchemaRecordBuilderType

class SchemaRecordBuilder<T : SchemaRecordBuilderType>(
    val inputSchema: ObjectType = ObjectType(properties = LinkedHashMap()),
    val expectedSchema: ObjectType = ObjectType(properties = LinkedHashMap()),
    val parent: T? = null
) : SchemaRecordBuilderType {
    fun with(
        given: FieldType,
        expected: FieldType = given,
        nameOverride: String? = null
    ): SchemaRecordBuilder<T> {
        val name = nameOverride ?: UUID.randomUUID().toString()
        inputSchema.properties[name] = given
        expectedSchema.properties[name] = expected
        return this
    }

    fun with(
        given: AirbyteType,
        expected: AirbyteType = given,
        nameOverride: String? = null,
    ): SchemaRecordBuilder<T> {
        return with(FieldType(given, false), FieldType(expected, false), nameOverride)
    }

    fun withRecord(
        nullable: Boolean = false,
        nameOverride: String? = null,
        expectedInstead: ObjectType? = null
    ): SchemaRecordBuilder<SchemaRecordBuilder<T>> {
        val name = nameOverride ?: UUID.randomUUID().toString()
        val inputRecord = ObjectType(properties = LinkedHashMap())
        val outputRecord = ObjectType(properties = LinkedHashMap())
        inputSchema.properties[name] = FieldType(inputRecord, nullable = nullable)
        expectedSchema.properties[name] = FieldType(outputRecord, nullable = nullable)
        return SchemaRecordBuilder(
            inputSchema = inputRecord,
            expectedSchema = expectedInstead ?: outputRecord,
            parent = this
        )
    }

    fun withUnion(
        nullable: Boolean = false,
        nameOverride: String? = null,
        expectedInstead: FieldType? = null
    ): SchemaTestUnionBuilder<T> {
        val name = nameOverride ?: UUID.randomUUID().toString()
        val inputOptions = mutableSetOf<AirbyteType>()
        val expectedOptions =
            if (expectedInstead == null) {
                mutableSetOf<AirbyteType>()
            } else {
                null
            }
        inputSchema.properties[name] = FieldType(UnionType(inputOptions), nullable = nullable)
        expectedSchema.properties[name] =
            expectedInstead ?: FieldType(UnionType(expectedOptions!!), nullable = nullable)
        return SchemaTestUnionBuilder(this, inputOptions, expectedOptions)
    }

    fun endRecord(): T {
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

class SchemaTestUnionBuilder<T : SchemaRecordBuilderType>(
    private val parent: SchemaRecordBuilder<T>,
    private val options: MutableSet<AirbyteType>,
    private val expectedOptions: MutableSet<AirbyteType>?
) : SchemaRecordBuilderType {
    fun with(option: AirbyteType, expected: AirbyteType? = null): SchemaTestUnionBuilder<T> {
        options.add(option)
        if (expected != null && expectedOptions == null) {
            throw IllegalStateException(
                "Cannot specify expected options for union without nullable"
            )
        }
        expected?.let { expectedOptions!!.add(it) }
        return this
    }

    fun withRecord(): SchemaRecordBuilder<SchemaTestUnionBuilder<T>> {
        val inputRecord = ObjectType(properties = LinkedHashMap())
        val outputRecord = ObjectType(properties = LinkedHashMap())
        options.add(inputRecord)
        expectedOptions?.add(outputRecord)
        return SchemaRecordBuilder(
            inputSchema = inputRecord,
            expectedSchema = outputRecord,
            parent = this
        )
    }

    fun endUnion(): SchemaRecordBuilder<T> {
        return parent
    }
}
