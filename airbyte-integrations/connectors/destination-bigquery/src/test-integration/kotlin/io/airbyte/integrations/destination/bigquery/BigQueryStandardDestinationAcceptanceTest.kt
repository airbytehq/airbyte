/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.bigquery

import java.nio.file.Path
import org.junit.jupiter.api.Disabled
import org.junit.jupiter.api.TestInstance
import org.slf4j.Logger
import org.slf4j.LoggerFactory

@Disabled
@TestInstance(TestInstance.Lifecycle.PER_CLASS)
class BigQueryStandardDestinationAcceptanceTest : AbstractBigQueryDestinationAcceptanceTest() {
    /**
     * Sets up secretsFile path and BigQuery instance for verification and cleanup This function
     * will be called before EACH test.
     *
     * @param testEnv
     * - information about the test environment.
     * @param TEST_SCHEMAS
     * @throws Exception
     * - can throw any exception, test framework will handle.
     * @see DestinationAcceptanceTest.setUpInternal
     */
    @Throws(Exception::class)
    override fun setup(testEnv: TestDestinationEnv, TEST_SCHEMAS: HashSet<String>) {
        secretsFile = Path.of("secrets/credentials-standard.json")
        setUpBigQuery()
        removeOldNamespaces()
    }

    /**
     * Removes data from bigquery This function will be called after EACH test
     *
     * @param testEnv
     * - information about the test environment.
     * @throws Exception
     * - can throw any exception, test framework will handle.
     * @see DestinationAcceptanceTest.tearDownInternal
     */
    override fun tearDown(testEnv: TestDestinationEnv) {
        tearDownBigQuery()
    }

    companion object {
        private val LOGGER: Logger =
            LoggerFactory.getLogger(BigQueryStandardDestinationAcceptanceTest::class.java)
    }
}
