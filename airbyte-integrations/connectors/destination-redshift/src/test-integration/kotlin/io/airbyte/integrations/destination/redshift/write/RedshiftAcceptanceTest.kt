/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.write

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.config.DataChannelFormat
import io.airbyte.cdk.load.config.DataChannelMedium
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectTypeWithoutSchema
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.message.InputRecord
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.test.util.OutputRecord
import io.airbyte.cdk.load.write.BasicFunctionalityIntegrationTest
import io.airbyte.cdk.load.write.ColumnDropBehavior
import io.airbyte.cdk.load.write.DedupBehavior
import io.airbyte.cdk.load.write.SchematizedNestedValueBehavior
import io.airbyte.cdk.load.write.StronglyTyped
import io.airbyte.cdk.load.write.UnionBehavior
import io.airbyte.cdk.load.write.UnknownTypesBehavior
import io.airbyte.integrations.destination.redshift.config.RedshiftSpecification
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import java.nio.file.Files
import java.nio.file.Path
import org.junit.jupiter.api.AfterAll
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
        columnDropBehavior = ColumnDropBehavior.RETAIN,
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

    // ================================================================
    // Empty string vs null preservation tests
    // ================================================================

    @Test
    fun testEmptyStringsPreservedAndNullsCorrectForAllColumnTypes() {
        val schema =
            ObjectType(
                linkedMapOf(
                    "id" to FieldType(IntegerType, nullable = false),
                    "str_col" to FieldType(StringType, nullable = true),
                    "int_col" to FieldType(IntegerType, nullable = true),
                    "obj_col" to FieldType(ObjectTypeWithoutSchema, nullable = true),
                ),
            )

        val stream =
            DestinationStream(
                unmappedNamespace = randomizedNamespace,
                unmappedName = "test_empty_string_null",
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
                    data =
                        """{"id": 1, "str_col": "hello", "int_col": 42, "obj_col": {"key": "value"}}""",
                    emittedAtMs = 1234,
                ),
                InputRecord(
                    stream = stream,
                    data = """{"id": 2, "str_col": null, "int_col": null, "obj_col": null}""",
                    emittedAtMs = 1234,
                ),
                InputRecord(
                    stream = stream,
                    data = """{"id": 3, "str_col": "", "int_col": 0, "obj_col": {}}""",
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
                            "str_col" to "hello",
                            "int_col" to 42,
                            "obj_col" to mapOf("key" to "value"),
                        ),
                    airbyteMeta = OutputRecord.Meta(changes = emptyList(), syncId = 42),
                ),
                OutputRecord(
                    extractedAt = 1234,
                    generationId = 0,
                    data =
                        mapOf(
                            "id" to 2,
                            "str_col" to null,
                            "int_col" to null,
                            "obj_col" to null,
                        ),
                    airbyteMeta = OutputRecord.Meta(changes = emptyList(), syncId = 42),
                ),
                OutputRecord(
                    extractedAt = 1234,
                    generationId = 0,
                    data =
                        mapOf(
                            "id" to 3,
                            "str_col" to "",
                            "int_col" to 0,
                            "obj_col" to emptyMap<String, Any>(),
                        ),
                    airbyteMeta = OutputRecord.Meta(changes = emptyList(), syncId = 42),
                ),
            ),
            stream,
            primaryKey = listOf(listOf("id")),
            cursor = null,
        )
    }

    // ================================================================
    // SUPER column nested string size limit tests
    // ================================================================

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
