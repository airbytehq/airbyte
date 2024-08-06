/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.bigquery

import com.amazonaws.services.s3.AmazonS3
import io.airbyte.cdk.integrations.base.DestinationConfig
import io.airbyte.cdk.integrations.destination.gcs.GcsDestinationConfig
import io.airbyte.integrations.destination.bigquery.BigQueryUtils.getGcsJsonNodeConfig
import java.nio.file.Path
import org.junit.jupiter.api.Disabled
import org.junit.jupiter.api.TestInstance
import org.slf4j.Logger
import org.slf4j.LoggerFactory

@Disabled
@TestInstance(TestInstance.Lifecycle.PER_CLASS)
class BigQueryGcsDestinationAcceptanceTest : AbstractBigQueryDestinationAcceptanceTest() {
    private var s3Client: AmazonS3? = null

    /**
     * Sets up secretsFile path as well as BigQuery and GCS instances for verification and cleanup
     * This function will be called before EACH test.
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
        // use secrets file with GCS staging config
        secretsFile = Path.of("secrets/credentials-gcs-staging.json")
        setUpBigQuery()
        removeOldNamespaces()

        DestinationConfig.initialize(_config)

        // the setup steps below are specific to GCS staging use case
        val gcsDestinationConfig: GcsDestinationConfig =
            GcsDestinationConfig.getGcsDestinationConfig(getGcsJsonNodeConfig(_config!!))
        this.s3Client = gcsDestinationConfig.getS3Client()
    }

    /**
     * Removes data from bigquery and GCS This function will be called after EACH test
     *
     * @param testEnv
     * - information about the test environment.
     * @throws Exception
     * - can throw any exception, test framework will handle.
     * @see DestinationAcceptanceTest.tearDownInternal
     */
    override fun tearDown(testEnv: TestDestinationEnv) {
        tearDownBigQuery()
        tearDownGcs()
    }

    protected fun tearDownGcs() {
        BigQueryDestinationTestUtils.tearDownGcs(s3Client, _config, LOGGER)
    }

    companion object {
        private val LOGGER: Logger =
            LoggerFactory.getLogger(BigQueryGcsDestinationAcceptanceTest::class.java)
    }
}
