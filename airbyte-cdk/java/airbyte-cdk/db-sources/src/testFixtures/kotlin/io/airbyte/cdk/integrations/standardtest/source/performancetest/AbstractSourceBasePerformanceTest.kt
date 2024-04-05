/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.standardtest.source.performancetest

import io.airbyte.cdk.integrations.standardtest.source.AbstractSourceConnectorTest
import io.airbyte.cdk.integrations.standardtest.source.TestDestinationEnv

/**
 * This abstract class contains common methods for both steams - Fill Db scripts and Performance
 * tests.
 */
abstract class AbstractSourceBasePerformanceTest : AbstractSourceConnectorTest() {
    /**
     * The column name will be used for a test column in the test tables. Override it if default
     * name is not valid for your source.
     */
    protected val testColumnName
        get() = TEST_COLUMN_NAME
    /**
     * The stream name template will be used for a test tables. Override it if default name is not
     * valid for your source.
     */
    protected val testStreamNameTemplate
        get() = TEST_STREAM_NAME_TEMPLATE
    @Throws(Exception::class)
    override fun setupEnvironment(environment: TestDestinationEnv?) {
        // DO NOTHING. Mandatory to override. DB will be setup as part of each test
    }

    companion object {
        protected const val TEST_COLUMN_NAME: String = "test_column"
        protected const val TEST_STREAM_NAME_TEMPLATE: String = "test_%S"
    }
}
