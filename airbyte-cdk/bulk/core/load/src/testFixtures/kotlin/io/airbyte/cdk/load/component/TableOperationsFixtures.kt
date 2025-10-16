/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.component

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.table.CDC_DELETED_AT_COLUMN
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.cdk.load.table.TableName
import java.util.UUID

/**
 * Common test fixtures and constants used across table operations test suites. Provides reusable
 * schemas, column mappings, and field definitions.
 */
object TableOperationsFixtures {
    // Common field names
    const val TEST_FIELD = "test"
    const val ID_FIELD = "id"

    // Common schemas
    val TEST_INTEGER_SCHEMA = ObjectType(linkedMapOf(TEST_FIELD to FieldType(IntegerType, false)))

    val ID_AND_TEST_SCHEMA =
        ObjectType(
            linkedMapOf(
                ID_FIELD to FieldType(StringType, false),
                TEST_FIELD to FieldType(IntegerType, false),
            ),
        )

    val ID_TEST_WITH_CDC_SCHEMA =
        ObjectType(
            linkedMapOf(
                ID_FIELD to FieldType(StringType, false),
                TEST_FIELD to FieldType(IntegerType, false),
                CDC_DELETED_AT_COLUMN to FieldType(IntegerType, false),
            ),
        )

    // Common column mappings
    val TEST_MAPPING = ColumnNameMapping(mapOf(TEST_FIELD to TEST_FIELD))

    val ID_TEST_WITH_CDC_MAPPING =
        ColumnNameMapping(
            mapOf(
                ID_FIELD to ID_FIELD,
                TEST_FIELD to TEST_FIELD,
                CDC_DELETED_AT_COLUMN to CDC_DELETED_AT_COLUMN,
            ),
        )

    // Common test cases
    val SINGLE_TEST_RECORD_INPUT: List<Map<String, AirbyteValue>> =
        listOf(mapOf(TEST_FIELD to IntegerValue(42)))

    val SINGLE_TEST_RECORD_EXPECTED: List<Map<String, Any>> = listOf(mapOf(TEST_FIELD to 42L))

    val OVERWRITE_SOURCE_RECORDS: List<Map<String, AirbyteValue>> =
        listOf(
            mapOf(TEST_FIELD to IntegerValue(123)),
            mapOf(TEST_FIELD to IntegerValue(456)),
        )

    val OVERWRITE_TARGET_RECORDS: List<Map<String, AirbyteValue>> =
        listOf(
            mapOf(TEST_FIELD to IntegerValue(86)),
            mapOf(TEST_FIELD to IntegerValue(75)),
            mapOf(TEST_FIELD to IntegerValue(309)),
        )

    val OVERWRITE_EXPECTED_RECORDS: List<Map<String, Any>> =
        listOf(
            mapOf(TEST_FIELD to 123L),
            mapOf(TEST_FIELD to 456L),
        )

    val COPY_EXPECTED_RECORDS: List<Map<String, Any>> =
        listOf(
            mapOf(TEST_FIELD to 123L),
            mapOf(TEST_FIELD to 456L),
            mapOf(TEST_FIELD to 86L),
            mapOf(TEST_FIELD to 75L),
            mapOf(TEST_FIELD to 309L),
        )

    val UPSERT_SOURCE_RECORDS: List<Map<String, AirbyteValue>> =
        listOf(
            mapOf(ID_FIELD to StringValue("2"), TEST_FIELD to IntegerValue(86)),
            mapOf(
                ID_FIELD to StringValue("3"),
                TEST_FIELD to IntegerValue(75),
                CDC_DELETED_AT_COLUMN to IntegerValue(1234),
            ),
            mapOf(ID_FIELD to StringValue("4"), TEST_FIELD to IntegerValue(309)),
            mapOf(ID_FIELD to StringValue("5"), TEST_FIELD to IntegerValue(309)),
            mapOf(
                ID_FIELD to StringValue("5"),
                TEST_FIELD to IntegerValue(309),
                CDC_DELETED_AT_COLUMN to IntegerValue(1234),
            ),
        )

    val UPSERT_TARGET_RECORDS: List<Map<String, AirbyteValue>> =
        listOf(
            mapOf(ID_FIELD to StringValue("1"), TEST_FIELD to IntegerValue(123)),
            mapOf(ID_FIELD to StringValue("2"), TEST_FIELD to IntegerValue(456)),
            mapOf(ID_FIELD to StringValue("3"), TEST_FIELD to IntegerValue(789)),
            mapOf(ID_FIELD to StringValue("4"), TEST_FIELD to IntegerValue(101112)),
        )

    val UPSERT_EXPECTED_RECORDS: List<Map<String, Any>> =
        listOf(
            mapOf(ID_FIELD to StringValue("1"), TEST_FIELD to 123L),
            mapOf(ID_FIELD to StringValue("2"), TEST_FIELD to 86L),
            mapOf(ID_FIELD to StringValue("4"), TEST_FIELD to 309L),
        )

    // Generate unique test table and test namespaces
    fun generateTestTableName(
        prefix: String,
        namespace: String,
    ): TableName {
        return TableName(namespace, "$prefix-${UUID.randomUUID()}")
    }

    fun generateTestNamespace(prefix: String): String {
        return "$prefix-${UUID.randomUUID()}"
    }

    // Create common destination stream configurations
    fun createAppendStream(
        namespace: String,
        name: String,
        schema: ObjectType,
        generationId: Long = 1,
        minimumGenerationId: Long = 0,
        syncId: Long = 1,
    ): DestinationStream =
        DestinationStream(
            unmappedNamespace = namespace,
            unmappedName = name,
            importType = Append,
            generationId = generationId,
            minimumGenerationId = minimumGenerationId,
            syncId = syncId,
            schema = schema,
            namespaceMapper = NamespaceMapper(),
        )

    fun createDedupeStream(
        namespace: String,
        name: String,
        schema: ObjectType,
        primaryKey: List<List<String>>,
        cursor: List<String>,
        generationId: Long = 1,
        minimumGenerationId: Long = 0,
        syncId: Long = 1,
    ): DestinationStream =
        DestinationStream(
            unmappedNamespace = namespace,
            unmappedName = name,
            importType =
                Dedupe(
                    primaryKey = primaryKey,
                    cursor = cursor,
                ),
            generationId = generationId,
            minimumGenerationId = minimumGenerationId,
            syncId = syncId,
            schema = schema,
            namespaceMapper = NamespaceMapper(),
        )

    fun List<Map<String, Any>>.sortByTestField() = this.sortedBy { it["test"] as Long }
}
