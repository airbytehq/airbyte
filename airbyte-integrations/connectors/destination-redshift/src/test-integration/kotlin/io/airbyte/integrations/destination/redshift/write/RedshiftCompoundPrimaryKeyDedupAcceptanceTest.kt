/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.write

import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.TimestampTypeWithTimezone
import io.airbyte.cdk.load.data.TimestampWithTimezoneValue
import io.airbyte.cdk.load.message.InputRecord
import io.airbyte.cdk.load.test.util.OutputRecord
import org.junit.jupiter.api.Assumptions.assumeTrue
import org.junit.jupiter.api.Test

class RedshiftCompoundPrimaryKeyDedupAcceptanceTest : RedshiftBaseAcceptanceTest() {
    @Test
    fun testDedupWithNullableCompoundPrimaryKey() {
        assumeTrue(verifyDataWriting)
        assumeTrue(dedupBehavior != null)

        val primaryKeyColumns = listOf("pk1", "pk2", "pk3", "pk4", "pk5", "pk6", "pk7", "pk8")
        val importType =
            Dedupe(
                primaryKey = primaryKeyColumns.map { listOf(it) },
                cursor = listOf("updated_at"),
            )
        val schema =
            ObjectType(
                linkedMapOf(
                    "pk1" to FieldType(IntegerType, true),
                    "pk2" to FieldType(IntegerType, true),
                    "pk3" to FieldType(IntegerType, true),
                    "pk4" to FieldType(IntegerType, true),
                    "pk5" to FieldType(IntegerType, true),
                    "pk6" to FieldType(IntegerType, true),
                    "pk7" to FieldType(IntegerType, true),
                    "pk8" to FieldType(IntegerType, true),
                    "updated_at" to FieldType(TimestampTypeWithTimezone, false),
                    "value" to FieldType(StringType, true),
                )
            )

        fun makeStream(syncId: Long) =
            DestinationStream(
                unmappedNamespace = randomizedNamespace,
                unmappedName = "compound_pk_dedup",
                generationId = 42,
                minimumGenerationId = 0,
                syncId = syncId,
                namespaceMapper = namespaceMapperForMedium(),
                tableSchema = makeTableSchema(schema, importType),
            )

        val firstStream = makeStream(syncId = 42)
        fun record(stream: DestinationStream, data: String, extractedAt: Long) =
            InputRecord(
                stream,
                data = data,
                emittedAtMs = extractedAt,
                checkpointId = checkpointKeyForMedium()?.checkpointId,
            )

        val keyA =
            """{"pk1": 1, "pk2": 10, "pk3": 3, "pk4": 40, "pk5": 5, "pk6": 60, "pk7": 7, "pk8": 80}"""
        val keyB =
            """{"pk1": 2, "pk2": 20, "pk3": null, "pk4": 40, "pk5": null, "pk6": 60, "pk7": 70, "pk8": null}"""

        runSync(
            updatedConfig,
            firstStream,
            listOf(
                record(
                    firstStream,
                    recordData(keyA, "2026-01-01T00:00:00Z", "first"),
                    extractedAt = 1000,
                ),
                record(
                    firstStream,
                    recordData(keyA, "2026-01-01T00:01:00Z", "deduped"),
                    extractedAt = 1000,
                ),
                record(
                    firstStream,
                    recordData(keyB, "2026-01-01T00:02:00Z", "second"),
                    extractedAt = 1000,
                ),
            ),
        )

        val secondStream = makeStream(syncId = 43)
        runSync(
            updatedConfig,
            secondStream,
            listOf(
                record(
                    secondStream,
                    recordData(keyA, "2026-01-01T00:03:00Z", "updated"),
                    extractedAt = 2000,
                ),
                record(
                    secondStream,
                    """{"pk1": 9, "pk2": null, "pk3": 9, "pk4": null, "pk5": 9, "pk6": 9, "pk7": null, "pk8": 9, "updated_at": "2026-01-01T00:05:00Z", "value": "inserted"}""",
                    extractedAt = 2000,
                ),
            ),
        )

        dumpAndDiffRecords(
            parsedConfig,
            listOf(
                outputRecord(
                    keyA,
                    extractedAt = 2000,
                    updatedAt = "2026-01-01T00:03:00Z",
                    value = "updated",
                    syncId = 43,
                ),
                outputRecord(
                    keyB,
                    extractedAt = 1000,
                    updatedAt = "2026-01-01T00:02:00Z",
                    value = "second",
                    syncId = 42,
                ),
                outputRecord(
                    """{"pk1": 9, "pk2": null, "pk3": 9, "pk4": null, "pk5": 9, "pk6": 9, "pk7": null, "pk8": 9}""",
                    extractedAt = 2000,
                    updatedAt = "2026-01-01T00:05:00Z",
                    value = "inserted",
                    syncId = 43,
                ),
            ),
            secondStream,
            primaryKey = primaryKeyColumns.map { listOf(it) },
            cursor = listOf("updated_at"),
        )
    }

    private fun recordData(key: String, updatedAt: String, value: String): String =
        key.dropLast(1) + """, "updated_at": "$updatedAt", "value": "$value"}"""

    private fun outputRecord(
        key: String,
        extractedAt: Long,
        updatedAt: String,
        value: String,
        syncId: Long,
    ): OutputRecord {
        val keyValues =
            key.removePrefix("{").removeSuffix("}").split(", ").associate { entry ->
                val (name, rawValue) = entry.split(": ")
                name.removeSurrounding("\"") to rawValue.toIntOrNull()
            }
        return OutputRecord(
            extractedAt = extractedAt,
            generationId = 42,
            data =
                keyValues +
                    mapOf(
                        "updated_at" to TimestampWithTimezoneValue(updatedAt),
                        "value" to value,
                    ),
            airbyteMeta = OutputRecord.Meta(syncId = syncId),
        )
    }
}
