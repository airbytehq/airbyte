/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.skeleton_directload

import io.airbyte.cdk.load.test.util.NoopDestinationCleaner
import io.airbyte.cdk.load.test.util.NoopExpectedRecordMapper
import io.airbyte.cdk.load.write.BasicFunctionalityIntegrationTest
import io.airbyte.cdk.load.write.SchematizedNestedValueBehavior
import io.airbyte.cdk.load.write.UnionBehavior
import io.airbyte.cdk.load.write.Untyped
import io.airbyte.integrations.destination.skeleton_directload.spec.SkeletonDirectLoadSpecification

class SkeletonDirectLoadBasicFunctionalityIntegrationTest :
    BasicFunctionalityIntegrationTest(
        SkeletonDirectLoadTestUtils.configContents(SkeletonDirectLoadTestUtils.mainConfigPath),
        SkeletonDirectLoadSpecification::class.java,
        SkeletonDirectLoadDataDumper,
        NoopDestinationCleaner,
        NoopExpectedRecordMapper,
        verifyDataWriting = false,
        isStreamSchemaRetroactive = false,
        dedupBehavior = null,
        stringifySchemalessObjects = false,
        schematizedObjectBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        schematizedArrayBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        unionBehavior = UnionBehavior.PASS_THROUGH,
        supportFileTransfer = false,
        commitDataIncrementally = false,
        allTypesBehavior = Untyped,
    )
