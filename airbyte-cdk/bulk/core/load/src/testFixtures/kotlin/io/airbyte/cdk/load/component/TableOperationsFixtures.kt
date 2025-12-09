/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.component

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
import io.airbyte.cdk.load.schema.model.StreamTableSchema
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.table.CDC_DELETED_AT_COLUMN
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.cdk.load.util.Jsons
import io.airbyte.cdk.util.invert
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
    const val DESCRIPTION_FIELD = "description"

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
                DESCRIPTION_FIELD to FieldType(StringType, true),
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
                DESCRIPTION_FIELD to DESCRIPTION_FIELD,
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
                DESCRIPTION_FIELD to
                    StringValue(
                        "New record, no existing record. Upsert should insert this record."
                    ),
            ),
            inputRecord(
                "295eb05d-da91-4cf5-8d26-a2bf8b6e8ef7",
                "2025-01-23T00:00:00Z",
                linkedMapOf(),
                generationId = 1,
                ID_FIELD to StringValue("3"),
                TEST_FIELD to IntegerValue(1002),
                CDC_DELETED_AT_COLUMN to IntegerValue(1234),
                DESCRIPTION_FIELD to
                    StringValue(
                        "New deletion record with later cursor and extracted_at than existing record. Upsert should delete the existing record."
                    ),
            ),
            inputRecord(
                "35295b83-302f-49c3-af0f-cf093bc46def",
                "2025-01-23T00:00:00Z",
                linkedMapOf(),
                generationId = 1,
                ID_FIELD to StringValue("5"),
                TEST_FIELD to IntegerValue(5),
                DESCRIPTION_FIELD to
                    StringValue(
                        "Incoming record with no existing record, but there's a second incoming deletion record with later extracted_at. Upsert should discard this record."
                    ),
            ),
            inputRecord(
                "5773cf6f-f8b7-48f2-8f23-728a4a4eb56d",
                "2025-01-23T01:00:00Z",
                linkedMapOf(),
                generationId = 1,
                ID_FIELD to StringValue("5"),
                TEST_FIELD to IntegerValue(5),
                CDC_DELETED_AT_COLUMN to IntegerValue(1234),
                DESCRIPTION_FIELD to
                    StringValue("Incoming deletion record. This record should be discarded."),
            ),
            inputRecord(
                "1c4d0fc5-1e1e-4f7e-87c8-a46a722ee984",
                "2025-01-23T00:00:00Z",
                linkedMapOf(),
                generationId = 1,
                ID_FIELD to StringValue("6"),
                TEST_FIELD to IntegerValue(6),
                DESCRIPTION_FIELD to
                    StringValue(
                        "Incoming record with no existing record, but there's a second incoming record with later extracted_at. Upsert should discard this record."
                    ),
            ),
            inputRecord(
                "2ddf5ee9-08a1-4319-824d-187d878edac5",
                "2025-01-23T01:00:00Z",
                linkedMapOf(),
                generationId = 1,
                ID_FIELD to StringValue("6"),
                TEST_FIELD to IntegerValue(6),
                DESCRIPTION_FIELD to
                    StringValue(
                        "Incoming record with no existing record. Upsert should insert this record."
                    ),
            ),
            inputRecord(
                "e8379b8f-e437-4d55-9d16-76f5e6e942d6",
                "2025-01-23T00:00:00Z",
                linkedMapOf(),
                generationId = 1,
                ID_FIELD to StringValue("7"),
                TEST_FIELD to IntegerValue(7),
                CDC_DELETED_AT_COLUMN to IntegerValue(1234),
                DESCRIPTION_FIELD to
                    StringValue(
                        "Incoming deletion record, but there's a second incoming record with later extracted_at. Upsert should discard this record."
                    ),
            ),
            inputRecord(
                "e56fc753-b55a-439b-9b16-528596e2ca3a",
                "2025-01-23T01:00:00Z",
                linkedMapOf(),
                generationId = 1,
                ID_FIELD to StringValue("7"),
                TEST_FIELD to IntegerValue(7),
                DESCRIPTION_FIELD to
                    StringValue(
                        "Incoming record with no existing record. Upsert should insert this record."
                    ),
            ),
            inputRecord(
                "645efad2-f1e6-438a-b29f-15ae5d096015",
                "2025-01-23T00:00:00Z",
                linkedMapOf(),
                generationId = 1,
                ID_FIELD to StringValue("8"),
                TEST_FIELD to IntegerValue(8),
                DESCRIPTION_FIELD to
                    StringValue(
                        "Incoming record with earlier cursor and later extracted_at than existing record. Upsert should discard this record (prefer cursor over extracted_at)."
                    ),
            ),
            inputRecord(
                "f74b8ddb-45d0-4e30-af25-66885e57a0e6",
                "2025-01-23T00:00:00Z",
                linkedMapOf(),
                generationId = 1,
                ID_FIELD to StringValue("9"),
                TEST_FIELD to IntegerValue(9),
                DESCRIPTION_FIELD to
                    StringValue(
                        "Incoming record with equal cursor and later extracted_at than existing record. Upsert should update with this record (break ties with extracted_at)."
                    ),
            ),
            inputRecord(
                "877cceb6-23a6-4e7b-92e3-59ca46f8fd6c",
                "2025-01-23T00:00:00Z",
                linkedMapOf(),
                generationId = 1,
                ID_FIELD to StringValue("10"),
                TEST_FIELD to IntegerValue(1010),
                DESCRIPTION_FIELD to
                    StringValue(
                        "Incoming record with later cursor and later extracted_at than existing record. Upsert should update with this record."
                    ),
            ),
            inputRecord(
                "20410b34-7bb0-4ba5-9c61-0dd23bfeee6d",
                "2025-01-22T00:00:00Z",
                linkedMapOf(),
                generationId = 1,
                ID_FIELD to StringValue("11"),
                TEST_FIELD to IntegerValue(11),
                DESCRIPTION_FIELD to
                    StringValue(
                        "Incoming record with earlier cursor and equal extracted_at than existing record. Upsert should discard this record."
                    ),
            ),
            inputRecord(
                "70fdf9b0-ade0-4d30-9131-ba217ef506da",
                "2025-01-22T00:00:00Z",
                linkedMapOf(),
                generationId = 1,
                ID_FIELD to StringValue("12"),
                TEST_FIELD to IntegerValue(1012),
                DESCRIPTION_FIELD to
                    StringValue(
                        "Incoming record with later cursor and equal extracted_at than existing record. Upsert should update with this record."
                    ),
            ),
            inputRecord(
                "20949d9b-8ffc-4497-85e4-cda14abc4049",
                "2025-01-21T00:00:00Z",
                linkedMapOf(),
                generationId = 1,
                ID_FIELD to StringValue("13"),
                TEST_FIELD to IntegerValue(13),
                DESCRIPTION_FIELD to
                    StringValue(
                        "Incoming record with earlier cursor and earlier extracted_at than existing record. Upsert should discard this record."
                    ),
            ),
            inputRecord(
                "5808a0ef-3c6d-4d9a-851c-edbbc4852e18",
                "2025-01-21T00:00:00Z",
                linkedMapOf(),
                generationId = 1,
                ID_FIELD to StringValue("14"),
                TEST_FIELD to IntegerValue(14),
                DESCRIPTION_FIELD to
                    StringValue(
                        "Incoming record with equal cursor and earlier extracted_at than existing record. Upsert should discard this record."
                    ),
            ),
            inputRecord(
                "373127a7-a40e-4e23-890b-1a52114686ee",
                "2025-01-21T00:00:00Z",
                linkedMapOf(),
                generationId = 1,
                ID_FIELD to StringValue("15"),
                TEST_FIELD to IntegerValue(1015),
                DESCRIPTION_FIELD to
                    StringValue(
                        "Incoming record with later cursor and earlier extracted_at than existing record. Upsert should update with this record."
                    ),
            ),
        )

    /**
     * These represent the records that already exist in the destination. See also
     * [UPSERT_SOURCE_RECORDS].
     */
    val UPSERT_TARGET_RECORDS: List<Map<String, AirbyteValue>> =
        listOf(
            inputRecord(
                "6317026e-12f9-4713-976e-ce43901bd7ce",
                "2025-01-22T00:00:00Z",
                linkedMapOf(),
                1,
                ID_FIELD to StringValue("1"),
                TEST_FIELD to IntegerValue(1),
                DESCRIPTION_FIELD to
                    StringValue(
                        "Existing record, no incoming record. Upsert should preserve this record."
                    ),
            ),
            // TODO what about destinations with CDC soft deletes?
            // https://github.com/airbytehq/airbyte-internal-issues/issues/14911
            inputRecord(
                "0c9770d2-d68d-4525-9bf2-d462527e25ab",
                "2025-01-22T00:00:00Z",
                linkedMapOf(),
                generationId = 1,
                ID_FIELD to StringValue("3"),
                TEST_FIELD to IntegerValue(3),
                DESCRIPTION_FIELD to
                    StringValue(
                        "Existing record with incoming deletion record with later cursor and extracted_at. Upsert should delete this record."
                    ),
            ),
            inputRecord(
                "8086bdd6-6cf5-479e-a819-e5f347373804",
                "2025-01-22T00:00:00Z",
                linkedMapOf(),
                generationId = 1,
                ID_FIELD to StringValue("8"),
                TEST_FIELD to IntegerValue(1008),
                DESCRIPTION_FIELD to
                    StringValue(
                        "Existing record with later cursor and earlier extracted_at than incoming record. Upsert should preserve this record (prefer cursor over extracted_at)."
                    ),
            ),
            inputRecord(
                "b60e8b33-32f4-4da0-934b-87d14d9ed354",
                "2025-01-22T00:00:00Z",
                linkedMapOf(),
                generationId = 1,
                ID_FIELD to StringValue("9"),
                TEST_FIELD to IntegerValue(9),
                DESCRIPTION_FIELD to
                    StringValue(
                        "Existing record with equal cursor and earlier extracted_at than incoming record. Upsert should discard this record (break ties with extracted_at)."
                    ),
            ),
            inputRecord(
                "e79d163e-b594-4016-89b9-a85e385778bd",
                "2025-01-22T00:00:00Z",
                linkedMapOf(),
                generationId = 1,
                ID_FIELD to StringValue("10"),
                TEST_FIELD to IntegerValue(10),
                DESCRIPTION_FIELD to
                    StringValue(
                        "Existing record with earlier cursor and earlier extracted_at than incoming record. Upsert should discard this record."
                    ),
            ),
            inputRecord(
                "3d345fb2-254e-4968-89a6-f896a05fb831",
                "2025-01-22T00:00:00Z",
                linkedMapOf(),
                generationId = 1,
                ID_FIELD to StringValue("11"),
                TEST_FIELD to IntegerValue(1011),
                DESCRIPTION_FIELD to
                    StringValue(
                        "Existing record with later cursor and equal extracted_at than incoming record. Upsert should preserve this record."
                    ),
            ),
            inputRecord(
                "9c5262e6-44e3-41de-9a5a-c31bc0efdb68",
                "2025-01-22T00:00:00Z",
                linkedMapOf(),
                generationId = 1,
                ID_FIELD to StringValue("12"),
                TEST_FIELD to IntegerValue(12),
                DESCRIPTION_FIELD to
                    StringValue(
                        "Existing record with earlier cursor and equal extracted_at than incoming record. Upsert should discard this record."
                    ),
            ),
            inputRecord(
                "739a9347-267b-48af-a172-2030320e2193",
                "2025-01-22T00:00:00Z",
                linkedMapOf(),
                generationId = 1,
                ID_FIELD to StringValue("13"),
                TEST_FIELD to IntegerValue(1013),
                DESCRIPTION_FIELD to
                    StringValue(
                        "Existing record with later cursor and later extracted_at than incoming record. Upsert should preserve this record."
                    ),
            ),
            inputRecord(
                "70243c59-eadb-4840-90fa-be4ed57609fc",
                "2025-01-22T00:00:00Z",
                linkedMapOf(),
                generationId = 1,
                ID_FIELD to StringValue("14"),
                TEST_FIELD to IntegerValue(14),
                DESCRIPTION_FIELD to
                    StringValue(
                        "Existing record with equal cursor and later extracted_at than incoming record. Upsert should preserve this record."
                    ),
            ),
            inputRecord(
                "966e89ec-c0d2-4358-b8e5-bf9c713f5396",
                "2025-01-22T00:00:00Z",
                linkedMapOf(),
                generationId = 1,
                ID_FIELD to StringValue("15"),
                TEST_FIELD to IntegerValue(15),
                DESCRIPTION_FIELD to
                    StringValue(
                        "Existing record with earlier cursor and later extracted_at than existing record. Upsert should discard this record."
                    ),
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
                DESCRIPTION_FIELD to
                    "New record, no existing record. Upsert should insert this record.",
            ),
            outputRecord(
                "6317026e-12f9-4713-976e-ce43901bd7ce",
                "2025-01-22T00:00:00Z",
                linkedMapOf(),
                generationId = 1L,
                ID_FIELD to "1",
                TEST_FIELD to 1L,
                DESCRIPTION_FIELD to
                    "Existing record, no incoming record. Upsert should preserve this record.",
            ),
            outputRecord(
                "2ddf5ee9-08a1-4319-824d-187d878edac5",
                "2025-01-23T01:00:00Z",
                linkedMapOf(),
                1L,
                ID_FIELD to "6",
                TEST_FIELD to 6L,
                DESCRIPTION_FIELD to
                    "Incoming record with no existing record. Upsert should insert this record.",
            ),
            outputRecord(
                "e56fc753-b55a-439b-9b16-528596e2ca3a",
                "2025-01-23T01:00:00Z",
                linkedMapOf(),
                1L,
                ID_FIELD to "7",
                TEST_FIELD to 7L,
                DESCRIPTION_FIELD to
                    "Incoming record with no existing record. Upsert should insert this record.",
            ),
            outputRecord(
                "8086bdd6-6cf5-479e-a819-e5f347373804",
                "2025-01-22T00:00:00Z",
                linkedMapOf(),
                1L,
                ID_FIELD to "8",
                TEST_FIELD to 1008L,
                DESCRIPTION_FIELD to
                    "Existing record with later cursor and earlier extracted_at than incoming record. Upsert should preserve this record (prefer cursor over extracted_at).",
            ),
            outputRecord(
                "f74b8ddb-45d0-4e30-af25-66885e57a0e6",
                "2025-01-23T00:00:00Z",
                linkedMapOf(),
                1L,
                ID_FIELD to "9",
                TEST_FIELD to 9L,
                DESCRIPTION_FIELD to
                    "Incoming record with equal cursor and later extracted_at than existing record. Upsert should update with this record (break ties with extracted_at).",
            ),
            outputRecord(
                "877cceb6-23a6-4e7b-92e3-59ca46f8fd6c",
                "2025-01-23T00:00:00Z",
                linkedMapOf(),
                1L,
                ID_FIELD to "10",
                TEST_FIELD to 1010L,
                DESCRIPTION_FIELD to
                    "Incoming record with later cursor and later extracted_at than existing record. Upsert should update with this record.",
            ),
            outputRecord(
                "3d345fb2-254e-4968-89a6-f896a05fb831",
                "2025-01-22T00:00:00Z",
                linkedMapOf(),
                1L,
                ID_FIELD to "11",
                TEST_FIELD to 1011L,
                DESCRIPTION_FIELD to
                    "Existing record with later cursor and equal extracted_at than incoming record. Upsert should preserve this record.",
            ),
            outputRecord(
                "70fdf9b0-ade0-4d30-9131-ba217ef506da",
                "2025-01-22T00:00:00Z",
                linkedMapOf(),
                1L,
                ID_FIELD to "12",
                TEST_FIELD to 1012L,
                DESCRIPTION_FIELD to
                    "Incoming record with later cursor and equal extracted_at than existing record. Upsert should update with this record.",
            ),
            outputRecord(
                "739a9347-267b-48af-a172-2030320e2193",
                "2025-01-22T00:00:00Z",
                linkedMapOf(),
                1L,
                ID_FIELD to "13",
                TEST_FIELD to 1013L,
                DESCRIPTION_FIELD to
                    "Existing record with later cursor and later extracted_at than incoming record. Upsert should preserve this record.",
            ),
            outputRecord(
                "70243c59-eadb-4840-90fa-be4ed57609fc",
                "2025-01-22T00:00:00Z",
                linkedMapOf(),
                1L,
                ID_FIELD to "14",
                TEST_FIELD to 14L,
                DESCRIPTION_FIELD to
                    "Existing record with equal cursor and later extracted_at than incoming record. Upsert should preserve this record.",
            ),
            outputRecord(
                "373127a7-a40e-4e23-890b-1a52114686ee",
                "2025-01-21T00:00:00Z",
                linkedMapOf(),
                1L,
                ID_FIELD to "15",
                TEST_FIELD to 1015L,
                DESCRIPTION_FIELD to
                    "Incoming record with later cursor and earlier extracted_at than existing record. Upsert should update with this record.",
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
    fun createStream(
        namespace: String,
        name: String,
        tableSchema: StreamTableSchema,
        generationId: Long = 1,
        minimumGenerationId: Long = 0,
        syncId: Long = 1,
    ): DestinationStream =
        DestinationStream(
            unmappedNamespace = namespace,
            unmappedName = name,
            importType = tableSchema.importType,
            generationId = generationId,
            minimumGenerationId = minimumGenerationId,
            syncId = syncId,
            schema = ObjectType(LinkedHashMap(tableSchema.columnSchema.inputSchema)),
            namespaceMapper = NamespaceMapper(),
            tableSchema = tableSchema,
        )

    fun <V> List<Map<String, V>>.sortBy(key: String) =
        // sketchy unchecked cast is intentional, we're assuming that the tests are written such
        // that the sort key is always comparable.
        // In practice, it's generally some sort of ID column (int/string/etc.).
        @Suppress("UNCHECKED_CAST") this.sortedBy { it[key] as Comparable<Any> }

    fun <V> Map<String, V>.prettyString() =
        "{" + this.entries.sortedBy { it.key }.joinToString(", ") + "}"

    fun <V> List<Map<String, V>>.applyColumnNameMapping(mapping: ColumnNameMapping) =
        map { record ->
            record.mapKeys { (k, _) -> mapping[k] ?: k }
        }
    fun <V> List<Map<String, V>>.reverseColumnNameMapping(
        columnNameMapping: ColumnNameMapping,
        airbyteMetaColumnMapping: Map<String, String>
    ): List<Map<String, V>> {
        val totalMapping = ColumnNameMapping(columnNameMapping + airbyteMetaColumnMapping)
        return map { record -> record.mapKeys { (k, _) -> totalMapping.invert()[k] ?: k } }
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

    fun inputRecord(vararg pairs: Pair<String, AirbyteValue>) =
        inputRecord(
            rawId = UUID.randomUUID().toString(),
            extractedAt = "2025-01-23T00:00:00Z",
            meta = linkedMapOf(),
            generationId = 1,
            pairs = pairs,
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
        expectedRecords: List<Map<String, Any?>>,
        actualRecords: List<Map<String, Any?>>,
        sortKey: String,
        message: String,
    ) =
        Assertions.assertEquals(
            expectedRecords.sortBy(sortKey).joinToString("\n") { it.prettyString() },
            actualRecords.sortBy(sortKey).joinToString("\n") { it.prettyString() },
            message,
        )
}
