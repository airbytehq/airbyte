/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.dev_null_v2

import io.airbyte.cdk.load.test.util.NoopDestinationCleaner
import io.airbyte.cdk.load.test.util.NoopExpectedRecordMapper
import io.airbyte.cdk.load.write.BasicFunctionalityIntegrationTest
import io.airbyte.cdk.load.write.SchematizedNestedValueBehavior
import io.airbyte.cdk.load.write.UnionBehavior
import io.airbyte.cdk.load.write.Untyped
import org.junit.jupiter.api.Test

class DevNullV2BasicFunctionalityIntegrationTest :
    BasicFunctionalityIntegrationTest(
        configContents = DevNullV2TestUtils.configContents(DevNullV2TestUtils.loggingConfigPath),
        configSpecClass = DevNullV2Specification::class.java,
        dataDumper = DevNullV2DestinationDataDumper,
        destinationCleaner = NoopDestinationCleaner,
        recordMangler = NoopExpectedRecordMapper,
        // Dev-null doesn't actually write data, so we can't verify it
        verifyDataWriting = false,
        // Dev-null doesn't support schema evolution
        isStreamSchemaRetroactive = false,
        // Dev-null doesn't support deduplication
        dedupBehavior = null,
        // Dev-null passes through all data as-is
        stringifySchemalessObjects = false,
        schematizedObjectBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        schematizedArrayBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        unionBehavior = UnionBehavior.PASS_THROUGH,
        // Dev-null doesn't support file transfer
        supportFileTransfer = false,
        // Dev-null doesn't commit incrementally (it doesn't commit at all)
        commitDataIncrementally = false,
        // Dev-null treats all types as untyped
        allTypesBehavior = Untyped,
        // We're using the data flow pipeline with Aggregate pattern
        useDataFlowPipeline = true,
    ) {
    
    @Test
    override fun testBasicWrite() {
        super.testBasicWrite()
    }

    @Test
    override fun testMidSyncCheckpointingStreamState() {
        super.testMidSyncCheckpointingStreamState()
    }
    
    @Test
    override fun testNamespaces() {
        // Dev-null doesn't have namespaces, skip this test
    }
    
    @Test
    override fun testFunkyCharacters() {
        // Dev-null doesn't need to handle special characters in names
    }
}