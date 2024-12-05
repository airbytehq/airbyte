/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_v2

import io.airbyte.cdk.load.test.util.NoopDestinationCleaner
import io.airbyte.cdk.load.test.util.NoopExpectedRecordMapper
import io.airbyte.cdk.load.write.AllTypesBehavior
import io.airbyte.cdk.load.write.BasicFunctionalityIntegrationTest
import io.airbyte.cdk.load.write.StronglyTyped
import io.airbyte.cdk.load.write.Untyped
import java.util.concurrent.TimeUnit
import org.junit.jupiter.api.Disabled
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.Timeout

@Timeout(20, unit = TimeUnit.MINUTES)
abstract class S3V2WriteTest(
    path: String,
    stringifySchemalessObjects: Boolean,
    promoteUnionToObject: Boolean,
    preserveUndeclaredFields: Boolean,
    /** This is false for staging mode, and true for non-staging mode. */
    commitDataIncrementally: Boolean = true,
    allTypesBehavior: AllTypesBehavior,
    nullEqualsUnset: Boolean = false,
) :
    BasicFunctionalityIntegrationTest(
        S3V2TestUtils.getConfig(path),
        S3V2Specification::class.java,
        S3V2DataDumper,
        NoopDestinationCleaner,
        NoopExpectedRecordMapper,
        isStreamSchemaRetroactive = false,
        supportsDedup = false,
        stringifySchemalessObjects = stringifySchemalessObjects,
        promoteUnionToObject = promoteUnionToObject,
        preserveUndeclaredFields = preserveUndeclaredFields,
        commitDataIncrementally = commitDataIncrementally,
        allTypesBehavior = allTypesBehavior,
        nullEqualsUnset = nullEqualsUnset,
    ) {
    @Disabled("Irrelevant for file destinations")
    @Test
    override fun testAppendSchemaEvolution() {
        super.testAppendSchemaEvolution()
    }

    @Disabled("Temporarily disable because failing in CI")
    @Test
    override fun testBasicWriteFile() {
        super.testBasicWriteFile()
    }
}

class S3V2WriteTestJsonUncompressed :
    S3V2WriteTest(
        S3V2TestUtils.JSON_UNCOMPRESSED_CONFIG_PATH,
        stringifySchemalessObjects = false,
        promoteUnionToObject = false,
        preserveUndeclaredFields = true,
        allTypesBehavior = Untyped,
    ) {
    @Test
    override fun testInterruptedTruncateWithPriorData() {
        super.testInterruptedTruncateWithPriorData()
    }
}

class S3V2WriteTestJsonRootLevelFlattening :
    S3V2WriteTest(
        S3V2TestUtils.JSON_ROOT_LEVEL_FLATTENING_CONFIG_PATH,
        stringifySchemalessObjects = false,
        promoteUnionToObject = false,
        preserveUndeclaredFields = true,
        allTypesBehavior = Untyped,
    ) {
    @Test
    override fun testInterruptedTruncateWithPriorData() {
        super.testInterruptedTruncateWithPriorData()
    }
}

@Disabled("Un-disable once staging is re-enabled")
class S3V2WriteTestJsonStaging :
    S3V2WriteTest(
        S3V2TestUtils.JSON_STAGING_CONFIG_PATH,
        stringifySchemalessObjects = false,
        promoteUnionToObject = false,
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
        stringifySchemalessObjects = false,
        promoteUnionToObject = false,
        preserveUndeclaredFields = true,
        allTypesBehavior = Untyped,
    )

class S3V2WriteTestCsvUncompressed :
    S3V2WriteTest(
        S3V2TestUtils.CSV_UNCOMPRESSED_CONFIG_PATH,
        stringifySchemalessObjects = false,
        promoteUnionToObject = false,
        preserveUndeclaredFields = true,
        allTypesBehavior = Untyped,
    )

class S3V2WriteTestCsvRootLevelFlattening :
    S3V2WriteTest(
        S3V2TestUtils.CSV_ROOT_LEVEL_FLATTENING_CONFIG_PATH,
        stringifySchemalessObjects = false,
        promoteUnionToObject = false,
        preserveUndeclaredFields = false,
        allTypesBehavior = Untyped,
        nullEqualsUnset =
            true, // Technically true of unflattened as well, but no top-level fields are nullable
    )

class S3V2WriteTestCsvGzip :
    S3V2WriteTest(
        S3V2TestUtils.CSV_GZIP_CONFIG_PATH,
        stringifySchemalessObjects = false,
        promoteUnionToObject = false,
        preserveUndeclaredFields = true,
        allTypesBehavior = Untyped,
    )

class S3V2WriteTestAvroUncompressed :
    S3V2WriteTest(
        S3V2TestUtils.AVRO_UNCOMPRESSED_CONFIG_PATH,
        stringifySchemalessObjects = true,
        promoteUnionToObject = false,
        preserveUndeclaredFields = false,
        allTypesBehavior = StronglyTyped(integerCanBeLarge = false),
        nullEqualsUnset = true,
    )

class S3V2WriteTestAvroBzip2 :
    S3V2WriteTest(
        S3V2TestUtils.AVRO_BZIP2_CONFIG_PATH,
        stringifySchemalessObjects = true,
        promoteUnionToObject = false,
        preserveUndeclaredFields = false,
        allTypesBehavior = StronglyTyped(integerCanBeLarge = false),
        nullEqualsUnset = true,
    )

class S3V2WriteTestParquetUncompressed :
    S3V2WriteTest(
        S3V2TestUtils.PARQUET_UNCOMPRESSED_CONFIG_PATH,
        stringifySchemalessObjects = true,
        promoteUnionToObject = true,
        preserveUndeclaredFields = false,
        allTypesBehavior = StronglyTyped(integerCanBeLarge = false),
        nullEqualsUnset = true,
    )

class S3V2WriteTestParquetSnappy :
    S3V2WriteTest(
        S3V2TestUtils.PARQUET_SNAPPY_CONFIG_PATH,
        stringifySchemalessObjects = true,
        promoteUnionToObject = true,
        preserveUndeclaredFields = false,
        allTypesBehavior = StronglyTyped(integerCanBeLarge = false),
        nullEqualsUnset = true,
    )

class S3V2WriteTestEndpointURL :
    S3V2WriteTest(
        S3V2TestUtils.ENDPOINT_URL_CONFIG_PATH,
        stringifySchemalessObjects = false,
        promoteUnionToObject = false,
        preserveUndeclaredFields = false,
        allTypesBehavior = Untyped,
        nullEqualsUnset = true,
    )
