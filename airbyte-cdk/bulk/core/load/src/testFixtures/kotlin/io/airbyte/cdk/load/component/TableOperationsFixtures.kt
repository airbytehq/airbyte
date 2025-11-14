/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.component

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.ArrayType
import io.airbyte.cdk.load.data.BooleanType
import io.airbyte.cdk.load.data.DateType
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NumberType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.TimeTypeWithTimezone
import io.airbyte.cdk.load.data.TimeTypeWithoutTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithoutTimezone
import io.airbyte.cdk.load.data.TimestampWithTimezoneValue
import io.airbyte.cdk.load.data.UnknownType
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_EXTRACTED_AT
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_GENERATION_ID
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_META
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_RAW_ID
import io.airbyte.cdk.load.table.CDC_DELETED_AT_COLUMN
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.cdk.load.table.TableName
import io.airbyte.cdk.load.util.Jsons
import java.util.UUID
import org.junit.jupiter.api.Assertions

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
    val TEST_STRING_SCHEMA = ObjectType(linkedMapOf(TEST_FIELD to FieldType(StringType, true)))

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

    val ALL_TYPES_SCHEMA =
        ObjectType(
            linkedMapOf(
                "string" to FieldType(StringType, true),
                "boolean" to FieldType(BooleanType, true),
                "integer" to FieldType(IntegerType, true),
                "number" to FieldType(NumberType, true),
                "date" to FieldType(DateType, true),
                "timestamp_tz" to FieldType(TimestampTypeWithTimezone, true),
                "timestamp_ntz" to FieldType(TimestampTypeWithoutTimezone, true),
                "time_tz" to FieldType(TimeTypeWithTimezone, true),
                "time_ntz" to FieldType(TimeTypeWithoutTimezone, true),
                "array" to FieldType(ArrayType(FieldType(StringType, true)), true),
                "object" to
                    FieldType(ObjectType(linkedMapOf("key" to FieldType(StringType, true))), true),
                "unknown" to FieldType(UnknownType(Jsons.readTree("""{"type": "potato"}""")), true),
            ),
        )
    val ALL_TYPES_MAPPING =
        ColumnNameMapping(
            mapOf(
                "string" to "string",
                "boolean" to "boolean",
                "integer" to "integer",
                "number" to "number",
                "date" to "date",
                "timestamp_tz" to "timestamp_tz",
                "timestamp_ntz" to "timestamp_ntz",
                "time_tz" to "time_tz",
                "time_ntz" to "time_ntz",
                "array" to "array",
                "object" to "object",
                "unknown" to "unknown",
            )
        )

    // Common column mappings
    val TEST_MAPPING = ColumnNameMapping(mapOf(TEST_FIELD to TEST_FIELD))
    val ID_AND_TEST_MAPPING =
        ColumnNameMapping(mapOf(TEST_FIELD to TEST_FIELD, ID_FIELD to ID_FIELD))

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
                "109d38b9-e001-4f62-86ce-4a457ab013a1",
                "2025-01-23T00:00:00Z",
                linkedMapOf(),
                generationId = 1,
                ID_FIELD to StringValue("0"),
                TEST_FIELD to IntegerValue(1000),
            ),
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
            // id=6: two records, no deletion. We should take the later record.
            inputRecord(
                "1c4d0fc5-1e1e-4f7e-87c8-a46a722ee984",
                "2025-01-23T00:00:00Z",
                linkedMapOf(),
                generationId = 1,
                ID_FIELD to StringValue("6"),
                TEST_FIELD to IntegerValue(42),
            ),
            inputRecord(
                "2ddf5ee9-08a1-4319-824d-187d878edac5",
                "2025-01-23T01:00:00Z",
                linkedMapOf(),
                generationId = 1,
                ID_FIELD to StringValue("6"),
                TEST_FIELD to IntegerValue(1006),
            ),
            // id=7: two new records; the earlier record is a delete.
            // We should keep the second record.
            inputRecord(
                "e8379b8f-e437-4d55-9d16-76f5e6e942d6",
                "2025-01-23T00:00:00Z",
                linkedMapOf(),
                generationId = 1,
                ID_FIELD to StringValue("7"),
                TEST_FIELD to IntegerValue(42),
                CDC_DELETED_AT_COLUMN to IntegerValue(1234),
            ),
            inputRecord(
                "e56fc753-b55a-439b-9b16-528596e2ca3a",
                "2025-01-23T01:00:00Z",
                linkedMapOf(),
                generationId = 1,
                ID_FIELD to StringValue("7"),
                TEST_FIELD to IntegerValue(1007),
            ),
            // id=8: earlier cursor than the existing record but later extracted_at.
            // we should discard this record (i.e. prefer cursor over extracted_at)
            inputRecord(
                "645efad2-f1e6-438a-b29f-15ae5d096015",
                "2025-01-23T00:00:00Z",
                linkedMapOf(),
                generationId = 1,
                ID_FIELD to StringValue("8"),
                TEST_FIELD to IntegerValue(8),
            ),
            // id=9: equal cursor to existing record but later extracted_at.
            // We should take this record (i.e. use extracted_at as tiebreaker)
            inputRecord(
                "f74b8ddb-45d0-4e30-af25-66885e57a0e6",
                "2025-01-23T00:00:00Z",
                linkedMapOf(),
                generationId = 1,
                ID_FIELD to StringValue("9"),
                TEST_FIELD to IntegerValue(9),
            ),
            // id=10: later cursor _and_ later extracted_at. Take this record.
            inputRecord(
                "877cceb6-23a6-4e7b-92e3-59ca46f8fd6c",
                "2025-01-23T00:00:00Z",
                linkedMapOf(),
                generationId = 1,
                ID_FIELD to StringValue("10"),
                TEST_FIELD to IntegerValue(1010),
            ),
            // id=11: earlier cursor and equal extracted_at. Discard this record.
            inputRecord(
                "20410b34-7bb0-4ba5-9c61-0dd23bfeee6d",
                "2025-01-22T00:00:00Z",
                linkedMapOf(),
                generationId = 1,
                ID_FIELD to StringValue("11"),
                TEST_FIELD to IntegerValue(11),
            ),
            // id=12: later cursor and equal extracted_at. Take this record.
            inputRecord(
                "70fdf9b0-ade0-4d30-9131-ba217ef506da",
                "2025-01-22T00:00:00Z",
                linkedMapOf(),
                generationId = 1,
                ID_FIELD to StringValue("12"),
                TEST_FIELD to IntegerValue(1012),
            ),
            // id=13: earlier cursor and earlier extracted_at. Discard.
            inputRecord(
                "20949d9b-8ffc-4497-85e4-cda14abc4049",
                "2025-01-21T00:00:00Z",
                linkedMapOf(),
                generationId = 1,
                ID_FIELD to StringValue("13"),
                TEST_FIELD to IntegerValue(13),
            ),
            // id=14: equal cursor and earlier extracted_at. Discard.
            inputRecord(
                "5808a0ef-3c6d-4d9a-851c-edbbc4852e18",
                "2025-01-21T00:00:00Z",
                linkedMapOf(),
                generationId = 1,
                ID_FIELD to StringValue("14"),
                TEST_FIELD to IntegerValue(14),
            ),
            // id=15: later cursor and earlier extracted_at. Take this record.
            inputRecord(
                "373127a7-a40e-4e23-890b-1a52114686ee",
                "2025-01-21T00:00:00Z",
                linkedMapOf(),
                generationId = 1,
                ID_FIELD to StringValue("15"),
                TEST_FIELD to IntegerValue(1015),
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
            inputRecord(
                "8086bdd6-6cf5-479e-a819-e5f347373804",
                "2025-01-22T00:00:00Z",
                linkedMapOf(),
                generationId = 1,
                ID_FIELD to StringValue("8"),
                TEST_FIELD to IntegerValue(1008),
            ),
            inputRecord(
                "b60e8b33-32f4-4da0-934b-87d14d9ed354",
                "2025-01-22T00:00:00Z",
                linkedMapOf(),
                generationId = 1,
                ID_FIELD to StringValue("9"),
                TEST_FIELD to IntegerValue(9),
            ),
            inputRecord(
                "e79d163e-b594-4016-89b9-a85e385778bd",
                "2025-01-22T00:00:00Z",
                linkedMapOf(),
                generationId = 1,
                ID_FIELD to StringValue("10"),
                TEST_FIELD to IntegerValue(10),
            ),
            inputRecord(
                "3d345fb2-254e-4968-89a6-f896a05fb831",
                "2025-01-22T00:00:00Z",
                linkedMapOf(),
                generationId = 1,
                ID_FIELD to StringValue("11"),
                TEST_FIELD to IntegerValue(1011),
            ),
            inputRecord(
                "9c5262e6-44e3-41de-9a5a-c31bc0efdb68",
                "2025-01-22T00:00:00Z",
                linkedMapOf(),
                generationId = 1,
                ID_FIELD to StringValue("12"),
                TEST_FIELD to IntegerValue(12),
            ),
            inputRecord(
                "739a9347-267b-48af-a172-2030320e2193",
                "2025-01-22T00:00:00Z",
                linkedMapOf(),
                generationId = 1,
                ID_FIELD to StringValue("13"),
                TEST_FIELD to IntegerValue(1013),
            ),
            inputRecord(
                "70243c59-eadb-4840-90fa-be4ed57609fc",
                "2025-01-22T00:00:00Z",
                linkedMapOf(),
                generationId = 1,
                ID_FIELD to StringValue("14"),
                TEST_FIELD to IntegerValue(14),
            ),
            inputRecord(
                "966e89ec-c0d2-4358-b8e5-bf9c713f5396",
                "2025-01-22T00:00:00Z",
                linkedMapOf(),
                generationId = 1,
                ID_FIELD to StringValue("15"),
                TEST_FIELD to IntegerValue(15),
            ),
        )

    val UPSERT_EXPECTED_RECORDS: List<Map<String, Any>> =
        listOf(
            outputRecord(
                "109d38b9-e001-4f62-86ce-4a457ab013a1",
                "2025-01-23T00:00:00Z",
                linkedMapOf(),
                generationId = 1L,
                ID_FIELD to "0",
                TEST_FIELD to 1000L,
            ),
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
            outputRecord(
                "2ddf5ee9-08a1-4319-824d-187d878edac5",
                "2025-01-23T01:00:00Z",
                linkedMapOf(),
                1L,
                ID_FIELD to "6",
                TEST_FIELD to 1006L,
            ),
            outputRecord(
                "e56fc753-b55a-439b-9b16-528596e2ca3a",
                "2025-01-23T01:00:00Z",
                linkedMapOf(),
                1L,
                ID_FIELD to "7",
                TEST_FIELD to 1007L,
            ),
            outputRecord(
                "8086bdd6-6cf5-479e-a819-e5f347373804",
                "2025-01-22T00:00:00Z",
                linkedMapOf(),
                1L,
                ID_FIELD to "8",
                TEST_FIELD to 1008L,
            ),
            outputRecord(
                "f74b8ddb-45d0-4e30-af25-66885e57a0e6",
                "2025-01-23T00:00:00Z",
                linkedMapOf(),
                1L,
                ID_FIELD to "9",
                TEST_FIELD to 9L,
            ),
            outputRecord(
                "877cceb6-23a6-4e7b-92e3-59ca46f8fd6c",
                "2025-01-23T00:00:00Z",
                linkedMapOf(),
                1L,
                ID_FIELD to "10",
                TEST_FIELD to 1010L,
            ),
            outputRecord(
                "3d345fb2-254e-4968-89a6-f896a05fb831",
                "2025-01-22T00:00:00Z",
                linkedMapOf(),
                1L,
                ID_FIELD to "11",
                TEST_FIELD to 1011L,
            ),
            outputRecord(
                "70fdf9b0-ade0-4d30-9131-ba217ef506da",
                "2025-01-22T00:00:00Z",
                linkedMapOf(),
                1L,
                ID_FIELD to "12",
                TEST_FIELD to 1012L,
            ),
            outputRecord(
                "739a9347-267b-48af-a172-2030320e2193",
                "2025-01-22T00:00:00Z",
                linkedMapOf(),
                1L,
                ID_FIELD to "13",
                TEST_FIELD to 1013L,
            ),
            outputRecord(
                "70243c59-eadb-4840-90fa-be4ed57609fc",
                "2025-01-22T00:00:00Z",
                linkedMapOf(),
                1L,
                ID_FIELD to "14",
                TEST_FIELD to 14L,
            ),
            outputRecord(
                "373127a7-a40e-4e23-890b-1a52114686ee",
                "2025-01-21T00:00:00Z",
                linkedMapOf(),
                1L,
                ID_FIELD to "15",
                TEST_FIELD to 1015L,
            ),
        )

    // Generate unique test table and test namespaces
    fun generateTestTableName(
        prefix: String,
        namespace: String,
    ): TableName {
        return TableName(
            namespace,
            "$prefix-${UUID.randomUUID()}"
            // this is a hack for now - eventually we probably want to plumb in a
            // TableNameGenerator,
            // but until then - underscores are generally nicer than hyphens.
            .replace('-', '_'),
        )
    }

    fun generateTestNamespace(prefix: String): String {
        return "$prefix-${UUID.randomUUID()}"
        // this is a hack for now - eventually we probably want to plumb in a TableNameGenerator,
        // but until then - underscores are generally nicer than hyphens.
        .replace('-', '_')
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

    fun <V> List<Map<String, V>>.sortBy(key: String) =
        // sketchy unchecked cast is intentional, we're assuming that the tests are written such
        // that the sort key is always comparable.
        // In practice, it's generally some sort of ID column (int/string/etc.).
        this.sortedBy { it[key] as Comparable<Any> }

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

    fun <V> List<Map<String, V>>.removeNulls() =
        this.map { record -> record.filterValues { it != null } }

    suspend fun TestTableOperationsClient.insertRecords(
        table: TableName,
        records: List<Map<String, AirbyteValue>>,
        columnNameMapping: ColumnNameMapping,
    ) = insertRecords(table, records.applyColumnNameMapping(columnNameMapping))

    suspend fun TestTableOperationsClient.insertRecords(
        table: TableName,
        columnNameMapping: ColumnNameMapping,
        vararg records: Map<String, AirbyteValue>,
    ) = insertRecords(table, records.toList(), columnNameMapping)

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

    fun assertEquals(
        expectedRecords: List<Map<String, Any>>,
        actualRecords: List<Map<String, Any>>,
        sortKey: String,
        message: String,
    ) =
        Assertions.assertEquals(
            expectedRecords.sortBy(sortKey).joinToString("\n"),
            actualRecords.sortBy(sortKey).joinToString("\n"),
            message,
        )
}
