/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.write

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectTypeWithoutSchema
import io.airbyte.cdk.load.message.InputRecord
import io.airbyte.cdk.load.test.util.OutputRecord
import io.airbyte.cdk.load.write.BasicFunctionalityIntegrationTest
import io.airbyte.cdk.load.write.ColumnDropBehavior
import io.airbyte.cdk.load.write.DedupBehavior
import io.airbyte.cdk.load.write.SchematizedNestedValueBehavior
import io.airbyte.cdk.load.write.StronglyTyped
import io.airbyte.cdk.load.write.UnionBehavior
import io.airbyte.cdk.load.write.UnknownTypesBehavior
import io.airbyte.integrations.destination.postgres.PostgresConfigUpdater
import io.airbyte.integrations.destination.postgres.PostgresContainerHelper
import io.airbyte.integrations.destination.postgres.spec.PostgresConfigurationFactory
import io.airbyte.integrations.destination.postgres.spec.PostgresSpecification
import io.airbyte.integrations.destination.postgres.spec.PostgresSpecificationCloud
import org.junit.jupiter.api.Assumptions.assumeTrue
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test

class PostgresAcceptanceTest :
    BasicFunctionalityIntegrationTest(
        configContents =
            """{
                        "host": "replace_me_host",
                        "port": replace_me_port,
                        "database": "replace_me_database",
                        "schema": "public",
                        "username": "replace_me_username",
                        "password": "replace_me_password"
                    }""",
        configSpecClass = PostgresSpecificationCloud::class.java,
        dataDumper =
            PostgresDataDumper { spec ->
                val configOverrides = buildConfigOverridesForTestContainer()
                PostgresConfigurationFactory()
                    .makeWithOverrides(spec as PostgresSpecification, configOverrides)
            },
        destinationCleaner = PostgresDataCleaner,
        isStreamSchemaRetroactive = true,
        dedupBehavior = DedupBehavior(DedupBehavior.CdcDeletionMode.HARD_DELETE),
        stringifySchemalessObjects = false,
        schematizedObjectBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        schematizedArrayBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        unionBehavior = UnionBehavior.PASS_THROUGH,
        stringifyUnionObjects = false,
        commitDataIncrementally = false,
        commitDataIncrementallyOnAppend = false,
        commitDataIncrementallyToEmptyDestinationOnAppend = true,
        commitDataIncrementallyToEmptyDestinationOnDedupe = false,
        allTypesBehavior =
            StronglyTyped(
                integerCanBeLarge = false,
                numberCanBeLarge = true,
                nestedFloatLosesPrecision = true,
            ),
        unknownTypesBehavior = UnknownTypesBehavior.PASS_THROUGH,
        nullEqualsUnset = true,
        columnDropBehavior = ColumnDropBehavior.RETAIN,
        configUpdater = PostgresConfigUpdater(),
        recordMangler = PostgresTimestampNormalizationMapper,
    ) {

    @Test
    fun testNullCharactersNestedInValues() {
        assumeTrue(verifyDataWriting)
        val stream = makeNullCharacterStream("null_characters_in_values")
        runSync(
            updatedConfig,
            stream,
            listOf(
                InputRecord(
                    stream,
                    """
                        {
                          "id": 1,
                          "schemaless_object": {
                            "objectValue": "before\u0000after",
                            "arrayValue": [{ "nested": "a\u0000b" }]
                          }
                        }""".trimIndent(),
                    emittedAtMs = 1602637589100,
                    checkpointId = checkpointKeyForMedium()?.checkpointId,
                )
            )
        )

        dumpAndDiffRecords(
            parsedConfig,
            listOf(
                OutputRecord(
                    extractedAt = 1602637589100,
                    generationId = 42,
                    data =
                        mapOf(
                            "id" to 1,
                            "schemaless_object" to
                                mapOf(
                                    "objectValue" to "beforeafter",
                                    "arrayValue" to listOf(mapOf("nested" to "ab")),
                                ),
                        ),
                    airbyteMeta = OutputRecord.Meta(syncId = 42),
                )
            ),
            stream,
            primaryKey = listOf(listOf("id")),
            cursor = null,
        )
    }

    @Test
    fun testNullCharactersInObjectKeys() {
        assumeTrue(verifyDataWriting)
        val stream = makeNullCharacterStream("null_characters_in_keys")
        runSync(
            updatedConfig,
            stream,
            listOf(
                InputRecord(
                    stream,
                    """
                        {
                          "id": 1,
                          "schemaless_object": {
                            "key\u0000name": [{ "nested\u0000key": "value" }]
                          }
                        }""".trimIndent(),
                    emittedAtMs = 1602637589100,
                    checkpointId = checkpointKeyForMedium()?.checkpointId,
                )
            )
        )

        dumpAndDiffRecords(
            parsedConfig,
            listOf(
                OutputRecord(
                    extractedAt = 1602637589100,
                    generationId = 42,
                    data =
                        mapOf(
                            "id" to 1,
                            "schemaless_object" to
                                mapOf("keyname" to listOf(mapOf("nestedkey" to "value"))),
                        ),
                    airbyteMeta = OutputRecord.Meta(syncId = 42),
                )
            ),
            stream,
            primaryKey = listOf(listOf("id")),
            cursor = null,
        )
    }

    private fun makeNullCharacterStream(name: String) =
        DestinationStream(
            unmappedNamespace = randomizedNamespace,
            unmappedName = name,
            generationId = 42,
            minimumGenerationId = 0,
            syncId = 42,
            namespaceMapper = namespaceMapperForMedium(),
            tableSchema =
                makeTableSchema(
                    ObjectType(
                        linkedMapOf(
                            "id" to FieldType(IntegerType, nullable = true),
                            "schemaless_object" to
                                FieldType(ObjectTypeWithoutSchema, nullable = true),
                        )
                    ),
                    Append,
                ),
        )

    companion object {
        @JvmStatic
        @BeforeAll
        fun beforeAll() {
            PostgresContainerHelper.start()
        }
    }
}
