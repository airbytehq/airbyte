/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.dev_null

import io.airbyte.cdk.load.test.util.NoopDestinationCleaner
import io.airbyte.cdk.load.test.util.NoopExpectedRecordMapper
import io.airbyte.cdk.load.write.BasicFunctionalityIntegrationTest
import io.airbyte.cdk.load.write.SchematizedNestedValueBehavior
import io.airbyte.cdk.load.write.UnionBehavior
import io.airbyte.cdk.load.write.Untyped
import org.junit.jupiter.api.Disabled
import org.junit.jupiter.api.Test

class DevNullBasicFunctionalityIntegrationTest :
    BasicFunctionalityIntegrationTest(
        DevNullTestUtils.loggingConfigContents,
        DevNullSpecificationOss::class.java,
        DevNullDestinationDataDumper,
        NoopDestinationCleaner,
        NoopExpectedRecordMapper,
        verifyDataWriting = false,
        isStreamSchemaRetroactive = false,
        supportsDedup = false,
        stringifySchemalessObjects = false,
        unionBehavior = UnionBehavior.PASS_THROUGH,
        schematizedObjectBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        schematizedArrayBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        preserveUndeclaredFields = false,
        commitDataIncrementally = false,
        allTypesBehavior = Untyped,
        supportFileTransfer = false,
    ) {
    @Test
    override fun testBasicWrite() {
        super.testBasicWrite()
    }

    @Test
    override fun testMidSyncCheckpointingStreamState() {
        super.testMidSyncCheckpointingStreamState()
    }

    @Test @Disabled("File transfer is not supported") override fun testBasicWriteFile() {}
}
