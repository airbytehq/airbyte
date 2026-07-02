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
 * Mirror of S3V2WriteTest. Same shape: an abstract base wired to the CDK
 * [BasicFunctionalityIntegrationTest] with a config path + [GcsV2DataDumper] + [GcsV2Specification]
 * , then one concrete subclass per output format we exercise.
 *
 * Differences from S3V2WriteTest (all because GCS auth is HMAC-only, no STS):
 * - No `micronautProperties = ...assumeRoleCredentials.asMicronautProperties()`. GCS has no
 * assume-role, so there is nothing to inject; the base default (empty map) is used.
 * - [GcsV2Destination.additionalMicronautEnvs] still contributes the "aws" env — see the class docs
 * there for why a GCS connector needs it (GcsClientFactory delegates to S3ClientFactory).
 * - Only STDIO/JSONL medium is exercised (no SOCKET/PROTOBUF variants) since the GCS v2 connector
 * ships the same object-storage loader as S3 and the socket path is covered by destination-s3.
 *
 * All non-file-destination tests are enabled so this runs as soon as the secrets JSON configs
 * exist. `mergesUnions`-gated tests only fire for the Avro subclass.
 */
@Timeout(60, unit = TimeUnit.MINUTES)
abstract class GcsV2WriteTest(
    path: String,
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
        GcsV2TestUtils.getConfig(path),
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
        // Avro and parquet both merge unions and map complex types to other types. Validate
        // that the behavior still works as expected when nested within a union.
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

class GcsV2WriteTestJsonl :
    GcsV2WriteTest(
        GcsV2TestUtils.JSONL_CONFIG_PATH,
        UncoercedExpectedRecordMapper,
        stringifySchemalessObjects = false,
        schematizedObjectBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        schematizedArrayBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        unionBehavior = UnionBehavior.PASS_THROUGH,
        allTypesBehavior = Untyped,
    )

class GcsV2WriteTestAvroSnappy :
    GcsV2WriteTest(
        GcsV2TestUtils.AVRO_SNAPPY_CONFIG_PATH,
        AvroExpectedRecordMapper,
        stringifySchemalessObjects = true,
        schematizedObjectBehavior = SchematizedNestedValueBehavior.STRONGLY_TYPE,
        schematizedArrayBehavior = SchematizedNestedValueBehavior.STRONGLY_TYPE,
        unionBehavior = UnionBehavior.PASS_THROUGH,
        // this is technically false. Avro + parquet do have limits on numbers.
        // But float64 is weird, in that the actual _limits_ are unreasonably large -
        // but at that size, you have very little precision.
        // This is actually covered by the nested/topLevelFloatLosesPrecision test cases.
        allTypesBehavior = StronglyTyped(integerCanBeLarge = false),
        nullEqualsUnset = true,
        unknownTypesBehavior = UnknownTypesBehavior.FAIL,
        mergesUnions = true,
    )

// AVRO without file-level compression -> `.avro` (Avro is not a file-compression provider).
class GcsV2WriteTestAvroUncompressed :
    GcsV2WriteTest(
        GcsV2TestUtils.AVRO_UNCOMPRESSED_CONFIG_PATH,
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

// CSV with the CDK default compression (GZIP) -> `.csv.gz`.
class GcsV2WriteTestCsv :
    GcsV2WriteTest(
        GcsV2TestUtils.CSV_CONFIG_PATH,
        UncoercedExpectedRecordMapper,
        stringifySchemalessObjects = false,
        schematizedObjectBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        schematizedArrayBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        unionBehavior = UnionBehavior.PASS_THROUGH,
        allTypesBehavior = Untyped,
    )

// CSV with explicit "No Compression" -> `.csv` (proves the compression toggle).
class GcsV2WriteTestCsvUncompressed :
    GcsV2WriteTest(
        GcsV2TestUtils.CSV_UNCOMPRESSED_CONFIG_PATH,
        UncoercedExpectedRecordMapper,
        stringifySchemalessObjects = false,
        schematizedObjectBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        schematizedArrayBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        unionBehavior = UnionBehavior.PASS_THROUGH,
        allTypesBehavior = Untyped,
    )

// Parquet (snappy internal codec) -> `.parquet` (Parquet is not a file-compression provider;
// compression lives inside the parquet container). Note unionBehavior = PROMOTE_TO_OBJECT, as S3.
class GcsV2WriteTestParquetSnappy :
    GcsV2WriteTest(
        GcsV2TestUtils.PARQUET_SNAPPY_CONFIG_PATH,
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
