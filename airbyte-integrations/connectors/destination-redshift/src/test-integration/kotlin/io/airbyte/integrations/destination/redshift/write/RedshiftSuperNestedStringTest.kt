/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.write

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.message.InputRecord
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.test.util.OutputRecord
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import org.junit.jupiter.api.Test

/**
 * Integration test verifying that SUPER columns containing nested strings exceeding Redshift's
 * 65,535-byte VARCHAR scalar limit are correctly nullified during the write pipeline.
 *
 * Redshift SUPER columns enforce a per-string-scalar limit of 65,535 bytes. When loading via CSV
 * COPY, individual string values within a SUPER JSON object that exceed this limit cause Redshift
 * error 1224. The connector prevents this by nullifying the entire SUPER column value and recording
 * a DESTINATION_FIELD_SIZE_LIMITATION change in _airbyte_meta.
 */
class RedshiftSuperNestedStringTest : RedshiftBaseAcceptanceTest() {

    @Test
    fun testSuperColumnNullifiedWhenNestedStringExceeds65535Bytes() {
        val schema =
            ObjectType(
                linkedMapOf(
                    "id" to FieldType(IntegerType, nullable = true),
                    "payload" to
                        FieldType(
                            ObjectType(
                                linkedMapOf(
                                    "small_field" to FieldType(StringType, nullable = true),
                                    "large_field" to FieldType(StringType, nullable = true),
                                )
                            ),
                            nullable = true,
                        ),
                ),
            )

        val stream =
            DestinationStream(
                unmappedNamespace = randomizedNamespace,
                unmappedName = "test_super_nested_string",
                generationId = 0,
                minimumGenerationId = 0,
                syncId = 42,
                namespaceMapper = namespaceMapperForMedium(),
                tableSchema = makeTableSchema(schema, Append),
            )

        // Build a JSON string with a nested field exceeding 65,535 bytes.
        // This simulates the real-world case of a base64-encoded image embedded in a JSON object.
        val oversizedString = "a".repeat(65_536)

        runSync(
            updatedConfig,
            stream,
            listOf(
                InputRecord(
                    stream = stream,
                    data =
                        """{"id": 1, "payload": {"small_field": "ok", "large_field": "$oversizedString"}}""",
                    emittedAtMs = 1234,
                ),
            ),
        )

        dumpAndDiffRecords(
            parsedConfig,
            listOf(
                OutputRecord(
                    extractedAt = 1234,
                    generationId = 0,
                    data =
                        mapOf(
                            "id" to 1,
                            "payload" to null,
                        ),
                    airbyteMeta =
                        OutputRecord.Meta(
                            changes =
                                listOf(
                                    Meta.Change(
                                        field = "payload",
                                        change = AirbyteRecordMessageMetaChange.Change.NULLED,
                                        reason =
                                            AirbyteRecordMessageMetaChange.Reason
                                                .DESTINATION_FIELD_SIZE_LIMITATION,
                                    ),
                                ),
                            syncId = 42,
                        ),
                ),
            ),
            stream,
            primaryKey = listOf(listOf("id")),
            cursor = null,
        )
    }

    @Test
    fun testSuperColumnPreservedWhenNestedStringsWithinLimit() {
        val schema =
            ObjectType(
                linkedMapOf(
                    "id" to FieldType(IntegerType, nullable = true),
                    "payload" to
                        FieldType(
                            ObjectType(
                                linkedMapOf(
                                    "name" to FieldType(StringType, nullable = true),
                                    "value" to FieldType(StringType, nullable = true),
                                )
                            ),
                            nullable = true,
                        ),
                ),
            )

        val stream =
            DestinationStream(
                unmappedNamespace = randomizedNamespace,
                unmappedName = "test_super_nested_string_ok",
                generationId = 0,
                minimumGenerationId = 0,
                syncId = 42,
                namespaceMapper = namespaceMapperForMedium(),
                tableSchema = makeTableSchema(schema, Append),
            )

        runSync(
            updatedConfig,
            stream,
            listOf(
                InputRecord(
                    stream = stream,
                    data = """{"id": 1, "payload": {"name": "test_user", "value": "small_data"}}""",
                    emittedAtMs = 1234,
                ),
            ),
        )

        dumpAndDiffRecords(
            parsedConfig,
            listOf(
                OutputRecord(
                    extractedAt = 1234,
                    generationId = 0,
                    data =
                        mapOf(
                            "id" to 1,
                            "payload" to
                                mapOf(
                                    "name" to "test_user",
                                    "value" to "small_data",
                                ),
                        ),
                    airbyteMeta =
                        OutputRecord.Meta(
                            changes = emptyList(),
                            syncId = 42,
                        ),
                ),
            ),
            stream,
            primaryKey = listOf(listOf("id")),
            cursor = null,
        )
    }
}
