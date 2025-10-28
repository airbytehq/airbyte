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
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.TimestampWithTimezoneValue
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_EXTRACTED_AT
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_GENERATION_ID
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_META
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_RAW_ID
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
    val TEST_INTEGER_SCHEMA = ObjectType(linkedMapOf(TEST_FIELD to FieldType(IntegerType, true)))

    val ID_AND_TEST_SCHEMA =
        ObjectType(
            linkedMapOf(
                ID_FIELD to FieldType(StringType, true),
                TEST_FIELD to FieldType(IntegerType, true),
            ),
        )

    val ID_TEST_WITH_CDC_SCHEMA =
        ObjectType(
            linkedMapOf(
                ID_FIELD to FieldType(StringType, true),
                TEST_FIELD to FieldType(IntegerType, true),
                CDC_DELETED_AT_COLUMN to FieldType(IntegerType, true),
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
        listOf(
            inputRecord(
                "07332f85-f41c-4cfe-971d-dcdc1e797c2d",
                "2025-01-23T00:00:00Z",
                linkedMapOf(),
                generationId = 1,
                TEST_FIELD to IntegerValue(42),
            )
        )

    val SINGLE_TEST_RECORD_EXPECTED: List<Map<String, Any>> = listOf(mapOf(TEST_FIELD to 42L))

    val OVERWRITE_SOURCE_RECORDS: List<Map<String, AirbyteValue>> =
        listOf(
            inputRecord(
                "ebdcf97c-5521-4852-ba55-2928b25443b6",
                "2025-01-23T00:00:00Z",
                linkedMapOf(),
                generationId = 1,
                TEST_FIELD to IntegerValue(123),
            ),
            inputRecord(
                "8cbdd2d3-c351-4180-86b7-84e05f12b65f",
                "2025-01-23T00:00:00Z",
                linkedMapOf(),
                generationId = 1,
                TEST_FIELD to IntegerValue(456),
            ),
        )

    val OVERWRITE_TARGET_RECORDS: List<Map<String, AirbyteValue>> =
        listOf(
            inputRecord(
                "258fab3d-ba01-4a2d-9f51-2e0313ad485d",
                "2025-01-22T00:00:00Z",
                linkedMapOf(),
                generationId = 1,
                TEST_FIELD to IntegerValue(86),
            ),
            inputRecord(
                "887bf227-24b0-4b8b-bb51-ea450bb4215b",
                "2025-01-22T00:00:00Z",
                linkedMapOf(),
                generationId = 1,
                TEST_FIELD to IntegerValue(75),
            ),
            inputRecord(
                "b9043b04-bcec-4999-a2e1-11d7051e5725",
                "2025-01-22T00:00:00Z",
                linkedMapOf(),
                generationId = 1,
                TEST_FIELD to IntegerValue(309),
            ),
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

    /**
     * These represent records that are being inserted to an existing destination. See also
     * [UPSERT_TARGET_RECORDS].
     *
     * Note that the TEST_FIELD/EXTRACTED_AT values here are higher than UPSERT_TARGET_RECORDS,
     * except where indicated otherwise
     */
    val UPSERT_SOURCE_RECORDS: List<Map<String, AirbyteValue>> =
        listOf(
            inputRecord(
                "5499cdef-1411-4c7e-987c-b22fe1284a49",
                "2025-01-23T00:00:00Z",
                linkedMapOf(),
                generationId = 1,
                ID_FIELD to StringValue("2"),
                TEST_FIELD to IntegerValue(1001),
            ),
            inputRecord(
                "295eb05d-da91-4cf5-8d26-a2bf8b6e8ef7",
                "2025-01-23T00:00:00Z",
                linkedMapOf(),
                generationId = 1,
                ID_FIELD to StringValue("3"),
                TEST_FIELD to IntegerValue(1002),
                CDC_DELETED_AT_COLUMN to IntegerValue(1234),
            ),
            inputRecord(
                "9110dcf0-2171-4daa-a934-695163950d98",
                "2025-01-23T00:00:00Z",
                linkedMapOf(),
                generationId = 1,
                ID_FIELD to StringValue("4"),
                TEST_FIELD to IntegerValue(4),
            ),
            // There are two records with id=5, which differ only in extracted_at.
            // The second record has non-null deleted_at, so we expect the record to be deleted.
            inputRecord(
                "35295b83-302f-49c3-af0f-cf093bc46def",
                "2025-01-23T00:00:00Z",
                linkedMapOf(),
                generationId = 1,
                ID_FIELD to StringValue("5"),
                TEST_FIELD to IntegerValue(1004),
            ),
            inputRecord(
                "5773cf6f-f8b7-48f2-8f23-728a4a4eb56d",
                "2025-01-23T01:00:00Z",
                linkedMapOf(),
                generationId = 1,
                ID_FIELD to StringValue("5"),
                TEST_FIELD to IntegerValue(1005),
                CDC_DELETED_AT_COLUMN to IntegerValue(1234),
            ),
        )

    /**
     * These represent the records that already exist in the destination. See also
     * [UPSERT_SOURCE_RECORDS].
     */
    val UPSERT_TARGET_RECORDS: List<Map<String, AirbyteValue>> =
        listOf(
            // id=1 has no incoming record, so it should remain untouched.
            inputRecord(
                "6317026e-12f9-4713-976e-ce43901bd7ce",
                "2025-01-22T00:00:00Z",
                linkedMapOf(),
                1,
                ID_FIELD to StringValue("1"),
                TEST_FIELD to IntegerValue(1),
            ),
            // id=2 has a normal incoming record, which will overwrite this one.
            inputRecord(
                "46159e3a-9bf9-42d9-8bb7-9f47d37bd663",
                "2025-01-22T00:00:00Z",
                linkedMapOf(),
                generationId = 1,
                ID_FIELD to StringValue("2"),
                TEST_FIELD to IntegerValue(2),
            ),
            // id=3 has an incoming record with nonnull deleted_at, so this record should be
            // deleted.
            // TODO what about destinations with CDC soft deletes?
            // https://github.com/airbytehq/airbyte-internal-issues/issues/14911
            inputRecord(
                "0c9770d2-d68d-4525-9bf2-d462527e25ab",
                "2025-01-22T00:00:00Z",
                linkedMapOf(),
                generationId = 1,
                ID_FIELD to StringValue("3"),
                TEST_FIELD to IntegerValue(3),
            ),
            // id=4 has an incoming record with the same cursor value (test=4) but later
            // extracted_at.
            // That record should replace this one.
            inputRecord(
                "02e22e03-587f-4d30-9718-994357407b65",
                "2025-01-22T00:00:00Z",
                linkedMapOf(),
                generationId = 1,
                ID_FIELD to StringValue("4"),
                TEST_FIELD to IntegerValue(4),
            ),
        )

    val UPSERT_EXPECTED_RECORDS: List<Map<String, Any>> =
        listOf(
            outputRecord(
                "6317026e-12f9-4713-976e-ce43901bd7ce",
                "2025-01-22T00:00:00Z",
                linkedMapOf(),
                generationId = 1L,
                ID_FIELD to "1",
                TEST_FIELD to 1L,
            ),
            outputRecord(
                "5499cdef-1411-4c7e-987c-b22fe1284a49",
                "2025-01-23T00:00:00Z",
                linkedMapOf(),
                1L,
                ID_FIELD to "2",
                TEST_FIELD to 1001L,
            ),
            outputRecord(
                "9110dcf0-2171-4daa-a934-695163950d98",
                "2025-01-23T00:00:00Z",
                linkedMapOf(),
                1L,
                ID_FIELD to "4",
                TEST_FIELD to 4L,
            ),
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

    fun <V> List<Map<String, V>>.sortByTestField() = this.sortedBy { it["test"] as Long }

    fun <V> List<Map<String, V>>.applyColumnNameMapping(mapping: ColumnNameMapping) =
        map { record ->
            record.mapKeys { (k, _) -> mapping[k] ?: k }
        }
    fun <V> List<Map<String, V>>.reverseColumnNameMapping(
        columnNameMapping: ColumnNameMapping,
        airbyteMetaColumnMapping: Map<String, String>
    ): List<Map<String, V>> {
        val totalMapping = ColumnNameMapping(columnNameMapping + airbyteMetaColumnMapping)
        return map { record -> record.mapKeys { (k, _) -> totalMapping.originalName(k) ?: k } }
    }

    suspend fun TableOperationsClient.insertRecords(
        table: TableName,
        records: List<Map<String, AirbyteValue>>,
        columnNameMapping: ColumnNameMapping,
    ) = insertRecords(table, records.applyColumnNameMapping(columnNameMapping))

    fun inputRecord(
        rawId: String,
        extractedAt: String,
        meta: LinkedHashMap<String, AirbyteValue>,
        generationId: Long,
        vararg pairs: Pair<String, AirbyteValue>
    ) =
        mapOf(
            COLUMN_NAME_AB_RAW_ID to StringValue(rawId),
            COLUMN_NAME_AB_EXTRACTED_AT to TimestampWithTimezoneValue(extractedAt),
            COLUMN_NAME_AB_META to ObjectValue(meta),
            COLUMN_NAME_AB_GENERATION_ID to IntegerValue(generationId),
            *pairs,
        )

    fun outputRecord(
        rawId: String,
        extractedAt: String,
        meta: LinkedHashMap<String, Any>,
        generationId: Long,
        vararg pairs: Pair<String, Any>
    ) =
        mapOf(
            COLUMN_NAME_AB_RAW_ID to rawId,
            COLUMN_NAME_AB_EXTRACTED_AT to extractedAt,
            COLUMN_NAME_AB_META to meta,
            COLUMN_NAME_AB_GENERATION_ID to generationId,
            *pairs,
        )
}
