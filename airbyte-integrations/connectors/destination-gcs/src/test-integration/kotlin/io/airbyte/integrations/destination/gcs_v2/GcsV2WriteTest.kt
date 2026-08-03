/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_v2

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.BooleanType
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectTypeWithoutSchema
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.UnionType
import io.airbyte.cdk.load.data.avro.AvroExpectedRecordMapper
import io.airbyte.cdk.load.message.InputRecord
import io.airbyte.cdk.load.test.util.ExpectedRecordMapper
import io.airbyte.cdk.load.test.util.NoopDestinationCleaner
import io.airbyte.cdk.load.test.util.UncoercedExpectedRecordMapper
import io.airbyte.cdk.load.test.util.destination_process.DestinationUncleanExitException
import io.airbyte.cdk.load.write.AllTypesBehavior
import io.airbyte.cdk.load.write.BasicFunctionalityIntegrationTest
import io.airbyte.cdk.load.write.SchematizedNestedValueBehavior
import io.airbyte.cdk.load.write.StronglyTyped
import io.airbyte.cdk.load.write.UnionBehavior
import io.airbyte.cdk.load.write.UnknownTypesBehavior
import io.airbyte.cdk.load.write.Untyped
import java.util.concurrent.TimeUnit
import org.junit.jupiter.api.Assumptions
import org.junit.jupiter.api.Disabled
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.Timeout
import org.junit.jupiter.api.assertThrows

/**
 * Write integration tests. Abstract base with one concrete subclass per output format. Each
 * subclass builds its config via [GcsV2TestUtils.getConfigWithFormat] from `secrets/config.json`.
 */
@Timeout(60, unit = TimeUnit.MINUTES)
abstract class GcsV2WriteTest(
    configContents: String,
    expectedRecordMapper: ExpectedRecordMapper,
    stringifySchemalessObjects: Boolean,
    schematizedObjectBehavior: SchematizedNestedValueBehavior,
    schematizedArrayBehavior: SchematizedNestedValueBehavior,
    unionBehavior: UnionBehavior,
    commitDataIncrementally: Boolean = true,
    allTypesBehavior: AllTypesBehavior,
    nullEqualsUnset: Boolean = false,
    unknownTypesBehavior: UnknownTypesBehavior = UnknownTypesBehavior.PASS_THROUGH,
    private val mergesUnions: Boolean = false,
    mismatchedTypesUnrepresentable: Boolean = false,
) :
    BasicFunctionalityIntegrationTest(
        configContents,
        GcsV2Specification::class.java,
        GcsV2DataDumper,
        NoopDestinationCleaner,
        expectedRecordMapper,
        additionalMicronautEnvs = GcsV2Destination.additionalMicronautEnvs,
        isStreamSchemaRetroactive = false,
        dedupBehavior = null,
        stringifySchemalessObjects = stringifySchemalessObjects,
        schematizedObjectBehavior = schematizedObjectBehavior,
        schematizedArrayBehavior = schematizedArrayBehavior,
        unionBehavior = unionBehavior,
        commitDataIncrementally = commitDataIncrementally,
        allTypesBehavior = allTypesBehavior,
        nullEqualsUnset = nullEqualsUnset,
        supportFileTransfer = true,
        unknownTypesBehavior = unknownTypesBehavior,
        mismatchedTypesUnrepresentable = mismatchedTypesUnrepresentable,
    ) {
    @Test
    override fun testAppend() {
        super.testAppend()
    }

    @Disabled("Irrelevant for file destinations")
    @Test
    override fun testAppendSchemaEvolution() {
        super.testAppendSchemaEvolution()
    }

    @Disabled("For most test the file test is not needed since it doesn't apply compression")
    @Test
    override fun testBasicWriteFile() {
        super.testBasicWriteFile()
    }

    @Test
    fun conflictingTypesInMappedUnions() {
        Assumptions.assumeTrue(unionBehavior == UnionBehavior.PROMOTE_TO_OBJECT)
        val stream =
            DestinationStream(
                unmappedNamespace = randomizedNamespace,
                unmappedName = "stream",
                importType = Append,
                generationId = 1L,
                minimumGenerationId = 0L,
                syncId = 101L,
                schema =
                    ObjectType(
                        linkedMapOf(
                            "id" to FieldType(IntegerType, nullable = true),
                            "union_of_objects" to
                                FieldType(
                                    type =
                                        UnionType.of(
                                            ObjectType(
                                                linkedMapOf(
                                                    "field1" to FieldType(StringType, true),
                                                )
                                            ),
                                            ObjectTypeWithoutSchema
                                        ),
                                    nullable = true
                                )
                        )
                    ),
                namespaceMapper = namespaceMapperForMedium()
            )

        assertThrows<DestinationUncleanExitException> {
            runSync(
                updatedConfig,
                stream,
                listOf(
                        """{"id": 1, "union_of_objects": {"field1": "a"}}""",
                        """{"id": 2, "union_of_objects": {"undeclared": "field"}}"""
                    )
                    .map { InputRecord(stream, it, 1L) }
            )
        }
    }

    @Test
    fun testMappableTypesNestedInUnions() {
        Assumptions.assumeTrue(mergesUnions)
        val stream =
            DestinationStream(
                unmappedNamespace = randomizedNamespace,
                unmappedName = "stream",
                importType = Append,
                generationId = 1L,
                minimumGenerationId = 0L,
                syncId = 101L,
                schema =
                    ObjectType(
                        linkedMapOf(
                            "id" to FieldType(IntegerType, nullable = true),
                            "union_of_objects" to
                                FieldType(
                                    type =
                                        UnionType.of(
                                            ObjectType(
                                                linkedMapOf(
                                                    "field1" to FieldType(StringType, true),
                                                    "field2" to
                                                        FieldType(
                                                            ObjectType(
                                                                linkedMapOf(
                                                                    "nested_schemaless" to
                                                                        FieldType(
                                                                            ObjectTypeWithoutSchema,
                                                                            true
                                                                        ),
                                                                    "nested_union" to
                                                                        FieldType(
                                                                            UnionType.of(
                                                                                StringType,
                                                                                BooleanType
                                                                            ),
                                                                            true
                                                                        )
                                                                )
                                                            ),
                                                            true
                                                        )
                                                )
                                            ),
                                            StringType
                                        ),
                                    nullable = true
                                ),
                        )
                    ),
                namespaceMapper = namespaceMapperForMedium()
            )

        val expectedRecords =
            if (unionBehavior == UnionBehavior.PROMOTE_TO_OBJECT) {
                listOf(
                    """{"id": 1, "union_of_objects": {"field1": "a", "field2": {"nested_schemaless": "{\"field\": \"value\"}", "nested_union": {"type": "string", "string": "string"}}}}""",
                    """{"id": 2, "union_of_objects": {"field1": "b", "field2": {"nested_schemaless": "{\"field\": \"value\"}", "nested_union": {"type": "boolean", "boolean": true}}}}"""
                )
            } else {
                listOf(
                    """{"id": 1, "union_of_objects": {"field1": "a", "field2": {"nested_schemaless": "{\"field\": \"value\"}", "nested_union": "string"}}}""",
                    """{"id": 2, "union_of_objects": {"field1": "b", "field2": {"nested_schemaless": "{\"field\": \"value\"}", "nested_union": true}}}"""
                )
            }

        runSync(updatedConfig, stream, expectedRecords.map { InputRecord(stream, it, 1L) })
    }
}

// JSONL with GZIP compression (default).
class GcsV2WriteTestJsonl :
    GcsV2WriteTest(
        GcsV2TestUtils.getConfigWithFormat(GcsV2TestUtils.JSONL_FORMAT),
        UncoercedExpectedRecordMapper,
        stringifySchemalessObjects = false,
        schematizedObjectBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        schematizedArrayBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        unionBehavior = UnionBehavior.PASS_THROUGH,
        allTypesBehavior = Untyped,
    )

// JSONL without compression.
class GcsV2WriteTestJsonlUncompressed :
    GcsV2WriteTest(
        GcsV2TestUtils.getConfigWithFormat(GcsV2TestUtils.JSONL_UNCOMPRESSED_FORMAT),
        UncoercedExpectedRecordMapper,
        stringifySchemalessObjects = false,
        schematizedObjectBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        schematizedArrayBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        unionBehavior = UnionBehavior.PASS_THROUGH,
        allTypesBehavior = Untyped,
    )

class GcsV2WriteTestAvroSnappy :
    GcsV2WriteTest(
        GcsV2TestUtils.getConfigWithFormat(GcsV2TestUtils.AVRO_SNAPPY_FORMAT),
        AvroExpectedRecordMapper,
        stringifySchemalessObjects = true,
        schematizedObjectBehavior = SchematizedNestedValueBehavior.STRONGLY_TYPE,
        schematizedArrayBehavior = SchematizedNestedValueBehavior.STRONGLY_TYPE,
        unionBehavior = UnionBehavior.PASS_THROUGH,
        allTypesBehavior = StronglyTyped(integerCanBeLarge = false),
        nullEqualsUnset = true,
        unknownTypesBehavior = UnknownTypesBehavior.FAIL,
        mergesUnions = true,
    )

// Avro without compression.
class GcsV2WriteTestAvroUncompressed :
    GcsV2WriteTest(
        GcsV2TestUtils.getConfigWithFormat(GcsV2TestUtils.AVRO_UNCOMPRESSED_FORMAT),
        AvroExpectedRecordMapper,
        stringifySchemalessObjects = true,
        unionBehavior = UnionBehavior.PASS_THROUGH,
        schematizedObjectBehavior = SchematizedNestedValueBehavior.STRONGLY_TYPE,
        schematizedArrayBehavior = SchematizedNestedValueBehavior.STRONGLY_TYPE,
        allTypesBehavior = StronglyTyped(integerCanBeLarge = false),
        nullEqualsUnset = true,
        unknownTypesBehavior = UnknownTypesBehavior.FAIL,
        mergesUnions = true,
    )

// CSV with GZIP compression (default).
class GcsV2WriteTestCsv :
    GcsV2WriteTest(
        GcsV2TestUtils.getConfigWithFormat(GcsV2TestUtils.CSV_FORMAT),
        UncoercedExpectedRecordMapper,
        stringifySchemalessObjects = false,
        schematizedObjectBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        schematizedArrayBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        unionBehavior = UnionBehavior.PASS_THROUGH,
        allTypesBehavior = Untyped,
    )

// CSV without compression.
class GcsV2WriteTestCsvUncompressed :
    GcsV2WriteTest(
        GcsV2TestUtils.getConfigWithFormat(GcsV2TestUtils.CSV_UNCOMPRESSED_FORMAT),
        UncoercedExpectedRecordMapper,
        stringifySchemalessObjects = false,
        schematizedObjectBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        schematizedArrayBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        unionBehavior = UnionBehavior.PASS_THROUGH,
        allTypesBehavior = Untyped,
    )

// Parquet with Snappy codec.
class GcsV2WriteTestParquetSnappy :
    GcsV2WriteTest(
        GcsV2TestUtils.getConfigWithFormat(GcsV2TestUtils.PARQUET_SNAPPY_FORMAT),
        AvroExpectedRecordMapper,
        stringifySchemalessObjects = true,
        schematizedObjectBehavior = SchematizedNestedValueBehavior.STRONGLY_TYPE,
        schematizedArrayBehavior = SchematizedNestedValueBehavior.STRONGLY_TYPE,
        unionBehavior = UnionBehavior.PROMOTE_TO_OBJECT,
        allTypesBehavior = StronglyTyped(integerCanBeLarge = false),
        nullEqualsUnset = true,
        unknownTypesBehavior = UnknownTypesBehavior.FAIL,
        mergesUnions = true,
    )
