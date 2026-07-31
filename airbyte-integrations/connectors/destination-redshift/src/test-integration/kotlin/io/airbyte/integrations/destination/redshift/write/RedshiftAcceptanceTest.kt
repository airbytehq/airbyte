/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.write

import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.config.DataChannelFormat
import io.airbyte.cdk.load.config.DataChannelMedium
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.TimestampTypeWithTimezone
import io.airbyte.cdk.load.data.TimestampWithTimezoneValue
import io.airbyte.cdk.load.message.InputRecord
import io.airbyte.cdk.load.test.util.OutputRecord
import io.airbyte.cdk.load.write.BasicFunctionalityIntegrationTest
import io.airbyte.cdk.load.write.DedupBehavior
import io.airbyte.cdk.load.write.SchematizedNestedValueBehavior
import io.airbyte.cdk.load.write.StronglyTyped
import io.airbyte.cdk.load.write.UnionBehavior
import io.airbyte.cdk.load.write.UnknownTypesBehavior
import io.airbyte.integrations.destination.redshift.config.RedshiftSpecification
import java.nio.file.Files
import java.nio.file.Path
import org.junit.jupiter.api.AfterAll
import org.junit.jupiter.api.Assumptions.assumeTrue
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Disabled
import org.junit.jupiter.api.Test

/**
 * Full end-to-end acceptance test for the Redshift destination in S3 staging mode.
 *
 * Runs the connector as a process via the CDK test harness and verifies typed final-table output.
 * Config is read from the `secrets/test_cluster.json` secrets file, which must contain valid
 * Redshift cluster + S3 staging credentials.
 */
abstract class RedshiftBaseAcceptanceTest(
    dataChannelFormat: DataChannelFormat = DataChannelFormat.JSONL,
    dataChannelMedium: DataChannelMedium = DataChannelMedium.STDIO,
    unknownTypesBehavior: UnknownTypesBehavior = UnknownTypesBehavior.PASS_THROUGH,
    isStreamSchemaRetroactiveForUnknownTypeToString: Boolean = true,
) :
    BasicFunctionalityIntegrationTest(
        configContents = Files.readString(Path.of(CONFIG_PATH)),
        configSpecClass = RedshiftSpecification::class.java,
        dataDumper = RedshiftDataDumper { RedshiftTestConfigProvider.configFrom(it) },
        destinationCleaner = RedshiftDataCleaner,
        recordMangler = RedshiftExpectedRecordMapper,
        isStreamSchemaRetroactive = true,
        isStreamSchemaRetroactiveForUnknownTypeToString =
            isStreamSchemaRetroactiveForUnknownTypeToString,
        dedupBehavior = DedupBehavior(DedupBehavior.CdcDeletionMode.HARD_DELETE),
        stringifySchemalessObjects = false,
        schematizedObjectBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        schematizedArrayBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        unionBehavior = UnionBehavior.STRINGIFY,
        stringifyUnionObjects = true,
        commitDataIncrementally = false,
        commitDataIncrementallyOnAppend = false,
        commitDataIncrementallyToEmptyDestinationOnAppend = true,
        commitDataIncrementallyToEmptyDestinationOnDedupe = false,
        allTypesBehavior =
            StronglyTyped(
                integerCanBeLarge = false,
                numberCanBeLarge = false,
                numberIsFixedPointPrecision38Scale9 = true,
                truncatedNumbersPopulateAirbyteMeta = false,
            ),
        unknownTypesBehavior = unknownTypesBehavior,
        nullEqualsUnset = true,
        dataChannelFormat = dataChannelFormat,
        dataChannelMedium = dataChannelMedium,
    ) {
    companion object {
        @JvmStatic
        @BeforeAll
        fun warmUpSharedDataSource() {
            RedshiftTestDataSourceProvider.get()
        }

        @JvmStatic
        @AfterAll
        fun closeSharedDataSource() {
            RedshiftTestDataSourceProvider.close()
        }
    }
}

/** Default acceptance test using JSONL over STDIO (standard data channel). */
class RedshiftAcceptanceTest : RedshiftBaseAcceptanceTest() {
    @Test
    @Disabled("Disabled due to frequent timeouts syncing 21 streams via S3 staging")
    override fun testManyStreamsCompletion() {
        super.testManyStreamsCompletion()
    }

    @Test
    @Disabled("Disabled due to frequent timeouts syncing 13 funky-character streams via S3 staging")
    override fun testFunkyCharacters() {
        super.testFunkyCharacters()
    }

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

/**
 * Acceptance test using Protobuf over Socket data channel. Protobuf cannot represent unknown types,
 * so those are nullified instead of passed through.
 */
class RedshiftProtoAcceptanceTest :
    RedshiftBaseAcceptanceTest(
        dataChannelFormat = DataChannelFormat.PROTOBUF,
        dataChannelMedium = DataChannelMedium.SOCKET,
        unknownTypesBehavior = UnknownTypesBehavior.NULL,
        isStreamSchemaRetroactiveForUnknownTypeToString = false,
    )
