/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.mock_integration_test

import io.airbyte.cdk.load.test.util.NoopDestinationCleaner
import io.airbyte.cdk.load.test.util.NoopExpectedRecordMapper
import io.airbyte.cdk.load.test.util.NoopNameMapper
import io.airbyte.cdk.load.write.BasicFunctionalityIntegrationTest
import org.junit.jupiter.api.Disabled
import org.junit.jupiter.api.Test

class MockBasicFunctionalityIntegrationTest :
    BasicFunctionalityIntegrationTest(
        MockDestinationSpecification.CONFIG,
        MockDestinationSpecification::class.java,
        MockDestinationDataDumper,
        NoopDestinationCleaner,
        NoopExpectedRecordMapper,
        NoopNameMapper,
        isStreamSchemaRetroactive = false,
        supportsDedup = true,
        stringifySchemalessObjects = false,
        promoteUnionToObject = false,
        preserveUndeclaredFields = true,
    ) {
    @Test
    override fun testBasicWrite() {
        super.testBasicWrite()
    }

    @Test
    @Disabled
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
    override fun testAppend() {
        super.testAppend()
    }

    @Test
    override fun testAppendSchemaEvolution() {
        super.testAppendSchemaEvolution()
    }

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
}
