/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.mock_integration_test

import io.airbyte.cdk.load.test.util.NoopDestinationCleaner
import io.airbyte.cdk.load.test.util.NoopNameMapper
import io.airbyte.cdk.load.test.util.UncoercedExpectedRecordMapper
import io.airbyte.cdk.load.write.BasicFunctionalityIntegrationTest
import io.airbyte.cdk.load.write.SchematizedNestedValueBehavior
import io.airbyte.cdk.load.write.UnionBehavior
import io.airbyte.cdk.load.write.Untyped
import org.junit.jupiter.api.Disabled
import org.junit.jupiter.api.Test

class MockBasicFunctionalityIntegrationTest :
    BasicFunctionalityIntegrationTest(
        MockDestinationSpecification.CONFIG,
        MockDestinationSpecification::class.java,
        MockDestinationDataDumper,
        NoopDestinationCleaner,
        UncoercedExpectedRecordMapper,
        NoopNameMapper,
        isStreamSchemaRetroactive = false,
        supportsDedup = true,
        stringifySchemalessObjects = false,
        schematizedObjectBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        schematizedArrayBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        unionBehavior = UnionBehavior.PASS_THROUGH,
        preserveUndeclaredFields = true,
        supportFileTransfer = false,
        commitDataIncrementally = false,
        allTypesBehavior = Untyped,
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
        super.testNamespaces()
    }

    @Test
    override fun testFunkyCharacters() {
        super.testFunkyCharacters()
    }

    @Test
    override fun testTruncateRefresh() {
        super.testTruncateRefresh()
    }

    @Test
    override fun testInterruptedTruncateWithPriorData() {
        super.testInterruptedTruncateWithPriorData()
    }

    @Test
    override fun resumeAfterCancelledTruncate() {
        super.resumeAfterCancelledTruncate()
    }

    @Test
    override fun testAppend() {
        super.testAppend()
    }

    @Test
    override fun testAppendSchemaEvolution() {
        super.testAppendSchemaEvolution()
    }

    @Disabled("flaky")
    @Test
    override fun testDedup() {
        super.testDedup()
    }

    @Test
    override fun testContainerTypes() {
        super.testContainerTypes()
    }

    @Test
    override fun testUnions() {
        super.testUnions()
    }

    @Test
    override fun testBasicTypes() {
        super.testBasicTypes()
    }
}
