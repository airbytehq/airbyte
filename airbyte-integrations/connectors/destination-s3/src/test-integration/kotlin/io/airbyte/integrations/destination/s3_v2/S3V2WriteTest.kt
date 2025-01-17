/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_v2

import io.airbyte.cdk.load.data.avro.AvroExpectedRecordMapper
import io.airbyte.cdk.load.test.util.ExpectedRecordMapper
import io.airbyte.cdk.load.test.util.NoopDestinationCleaner
import io.airbyte.cdk.load.test.util.UncoercedExpectedRecordMapper
import io.airbyte.cdk.load.write.AllTypesBehavior
import io.airbyte.cdk.load.write.BasicFunctionalityIntegrationTest
import io.airbyte.cdk.load.write.SchematizedNestedValueBehavior
import io.airbyte.cdk.load.write.StronglyTyped
import io.airbyte.cdk.load.write.UnionBehavior
import io.airbyte.cdk.load.write.Untyped
import java.util.concurrent.TimeUnit
import org.junit.jupiter.api.Disabled
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.Timeout

@Timeout(60, unit = TimeUnit.MINUTES)
abstract class S3V2WriteTest(
    path: String,
    expectedRecordMapper: ExpectedRecordMapper,
    stringifySchemalessObjects: Boolean,
    schematizedObjectBehavior: SchematizedNestedValueBehavior,
    schematizedArrayBehavior: SchematizedNestedValueBehavior,
    unionBehavior: UnionBehavior,
    preserveUndeclaredFields: Boolean,
    /** This is false for staging mode, and true for non-staging mode. */
    commitDataIncrementally: Boolean = true,
    allTypesBehavior: AllTypesBehavior,
    nullEqualsUnset: Boolean = false,
    nullUnknownTypes: Boolean = false,
    envVars: Map<String, String> = emptyMap(),
) :
    BasicFunctionalityIntegrationTest(
        S3V2TestUtils.getConfig(path),
        S3V2Specification::class.java,
        S3V2DataDumper,
        NoopDestinationCleaner,
        expectedRecordMapper,
        additionalMicronautEnvs = S3V2Destination.additionalMicronautEnvs,
        isStreamSchemaRetroactive = false,
        supportsDedup = false,
        stringifySchemalessObjects = stringifySchemalessObjects,
        schematizedObjectBehavior = schematizedObjectBehavior,
        schematizedArrayBehavior = schematizedArrayBehavior,
        unionBehavior = unionBehavior,
        preserveUndeclaredFields = preserveUndeclaredFields,
        commitDataIncrementally = commitDataIncrementally,
        allTypesBehavior = allTypesBehavior,
        nullEqualsUnset = nullEqualsUnset,
        supportFileTransfer = true,
        envVars = envVars,
        nullUnknownTypes = nullUnknownTypes,
    ) {
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
}

class S3V2WriteTestJsonUncompressed :
    S3V2WriteTest(
        S3V2TestUtils.JSON_UNCOMPRESSED_CONFIG_PATH,
        UncoercedExpectedRecordMapper,
        stringifySchemalessObjects = false,
        unionBehavior = UnionBehavior.PASS_THROUGH,
        schematizedObjectBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        schematizedArrayBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        preserveUndeclaredFields = true,
        allTypesBehavior = Untyped,
    )

class S3V2WriteTestJsonRootLevelFlattening :
    S3V2WriteTest(
        S3V2TestUtils.JSON_ROOT_LEVEL_FLATTENING_CONFIG_PATH,
        UncoercedExpectedRecordMapper,
        stringifySchemalessObjects = false,
        unionBehavior = UnionBehavior.PASS_THROUGH,
        schematizedObjectBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        schematizedArrayBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        preserveUndeclaredFields = true,
        allTypesBehavior = Untyped,
    )

@Disabled("Un-disable once staging is re-enabled")
class S3V2WriteTestJsonStaging :
    S3V2WriteTest(
        S3V2TestUtils.JSON_STAGING_CONFIG_PATH,
        UncoercedExpectedRecordMapper,
        stringifySchemalessObjects = false,
        unionBehavior = UnionBehavior.PASS_THROUGH,
        schematizedObjectBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        schematizedArrayBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        preserveUndeclaredFields = true,
        allTypesBehavior = Untyped,
        commitDataIncrementally = false
    ) {
    @Test
    @Disabled("Staging mode is not supported for file transfers")
    override fun testBasicWriteFile() {}
}

class S3V2WriteTestJsonGzip :
    S3V2WriteTest(
        S3V2TestUtils.JSON_GZIP_CONFIG_PATH,
        UncoercedExpectedRecordMapper,
        stringifySchemalessObjects = false,
        unionBehavior = UnionBehavior.PASS_THROUGH,
        schematizedObjectBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        schematizedArrayBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        preserveUndeclaredFields = true,
        allTypesBehavior = Untyped,
    )

class S3V2WriteTestCsvUncompressed :
    S3V2WriteTest(
        S3V2TestUtils.CSV_UNCOMPRESSED_CONFIG_PATH,
        UncoercedExpectedRecordMapper,
        stringifySchemalessObjects = false,
        unionBehavior = UnionBehavior.PASS_THROUGH,
        schematizedObjectBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        schematizedArrayBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        preserveUndeclaredFields = true,
        allTypesBehavior = Untyped,
    ) {
    @Test
    override fun testBasicWriteFile() {
        super.testBasicWriteFile()
    }
}

class S3V2WriteTestCsvRootLevelFlattening :
    S3V2WriteTest(
        S3V2TestUtils.CSV_ROOT_LEVEL_FLATTENING_CONFIG_PATH,
        UncoercedExpectedRecordMapper,
        stringifySchemalessObjects = false,
        unionBehavior = UnionBehavior.PASS_THROUGH,
        schematizedObjectBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        schematizedArrayBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        preserveUndeclaredFields = false,
        allTypesBehavior = Untyped,
        nullEqualsUnset =
            true, // Technically true of unflattened as well, but no top-level fields are nullable
    )

class S3V2WriteTestCsvGzip :
    S3V2WriteTest(
        S3V2TestUtils.CSV_GZIP_CONFIG_PATH,
        UncoercedExpectedRecordMapper,
        stringifySchemalessObjects = false,
        unionBehavior = UnionBehavior.PASS_THROUGH,
        schematizedObjectBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        schematizedArrayBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        preserveUndeclaredFields = true,
        allTypesBehavior = Untyped,
    )

class S3V2WriteTestAvroUncompressed :
    S3V2WriteTest(
        S3V2TestUtils.AVRO_UNCOMPRESSED_CONFIG_PATH,
        AvroExpectedRecordMapper,
        stringifySchemalessObjects = true,
        unionBehavior = UnionBehavior.PASS_THROUGH,
        schematizedObjectBehavior = SchematizedNestedValueBehavior.STRONGLY_TYPE,
        schematizedArrayBehavior = SchematizedNestedValueBehavior.STRONGLY_TYPE,
        preserveUndeclaredFields = false,
        allTypesBehavior = StronglyTyped(integerCanBeLarge = false),
        nullEqualsUnset = true,
        nullUnknownTypes = true,
    ) {
    @Test
    override fun testUnknownTypes() {
        super.testUnknownTypes()
    }

    @Test
    override fun testFunkyCharacters() {
        super.testFunkyCharacters()
    }
}

class S3V2WriteTestAvroBzip2 :
    S3V2WriteTest(
        S3V2TestUtils.AVRO_BZIP2_CONFIG_PATH,
        AvroExpectedRecordMapper,
        stringifySchemalessObjects = true,
        unionBehavior = UnionBehavior.PASS_THROUGH,
        schematizedObjectBehavior = SchematizedNestedValueBehavior.STRONGLY_TYPE,
        schematizedArrayBehavior = SchematizedNestedValueBehavior.STRONGLY_TYPE,
        preserveUndeclaredFields = false,
        allTypesBehavior = StronglyTyped(integerCanBeLarge = false),
        nullEqualsUnset = true,
        nullUnknownTypes = true,
    )

class S3V2WriteTestParquetUncompressed :
    S3V2WriteTest(
        S3V2TestUtils.PARQUET_UNCOMPRESSED_CONFIG_PATH,
        AvroExpectedRecordMapper,
        stringifySchemalessObjects = true,
        unionBehavior = UnionBehavior.PROMOTE_TO_OBJECT,
        schematizedObjectBehavior = SchematizedNestedValueBehavior.STRONGLY_TYPE,
        schematizedArrayBehavior = SchematizedNestedValueBehavior.STRONGLY_TYPE,
        preserveUndeclaredFields = false,
        allTypesBehavior = StronglyTyped(integerCanBeLarge = false),
        nullEqualsUnset = true,
        nullUnknownTypes = true,
    )

class S3V2WriteTestParquetSnappy :
    S3V2WriteTest(
        S3V2TestUtils.PARQUET_SNAPPY_CONFIG_PATH,
        AvroExpectedRecordMapper,
        stringifySchemalessObjects = true,
        unionBehavior = UnionBehavior.PROMOTE_TO_OBJECT,
        schematizedObjectBehavior = SchematizedNestedValueBehavior.STRONGLY_TYPE,
        schematizedArrayBehavior = SchematizedNestedValueBehavior.STRONGLY_TYPE,
        preserveUndeclaredFields = false,
        allTypesBehavior = StronglyTyped(integerCanBeLarge = false),
        nullEqualsUnset = true,
        nullUnknownTypes = true,
    )

class S3V2WriteTestEndpointURL :
    S3V2WriteTest(
        S3V2TestUtils.ENDPOINT_URL_CONFIG_PATH,
        // this test is writing to CSV
        UncoercedExpectedRecordMapper,
        stringifySchemalessObjects = false,
        unionBehavior = UnionBehavior.PASS_THROUGH,
        schematizedObjectBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        schematizedArrayBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        preserveUndeclaredFields = false,
        allTypesBehavior = Untyped,
        nullEqualsUnset = true,
    )

class S3V2AmbiguousFilepath :
    S3V2WriteTest(
        S3V2TestUtils.AMBIGUOUS_FILEPATH_CONFIG_PATH,
        // this test is writing to CSV
        UncoercedExpectedRecordMapper,
        stringifySchemalessObjects = false,
        unionBehavior = UnionBehavior.PASS_THROUGH,
        schematizedObjectBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        schematizedArrayBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        preserveUndeclaredFields = true,
        allTypesBehavior = Untyped,
    )
