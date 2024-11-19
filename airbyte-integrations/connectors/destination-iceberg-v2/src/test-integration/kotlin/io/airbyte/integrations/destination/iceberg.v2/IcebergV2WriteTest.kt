/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.v2

import io.airbyte.cdk.load.test.util.FakeDataDumper
import io.airbyte.cdk.load.test.util.NoopDestinationCleaner
import io.airbyte.cdk.load.test.util.NoopExpectedRecordMapper
import io.airbyte.cdk.load.write.BasicFunctionalityIntegrationTest
import io.airbyte.cdk.load.write.StronglyTyped
import org.junit.jupiter.api.Disabled

abstract class IcebergV2WriteTest(path: String) :
    BasicFunctionalityIntegrationTest(
        IcebergV2TestUtil.getConfig(path),
        IcebergV2Specification::class.java,
        FakeDataDumper,
        NoopDestinationCleaner,
        NoopExpectedRecordMapper,
        // TODO let's validate these - I'm making some assumptions about how iceberg works
        isStreamSchemaRetroactive = true,
        supportsDedup = false,
        stringifySchemalessObjects = true,
        promoteUnionToObject = true,
        preserveUndeclaredFields = false,
        commitDataIncrementally = false,
        allTypesBehavior = StronglyTyped(),
    )

// TODO replace this with a real test class for an actual config
@Disabled("nowhere even close to functional")
class FakeIcebergWriteTest : IcebergV2WriteTest(IcebergV2TestUtil.SOME_RANDOM_S3_CONFIG)
