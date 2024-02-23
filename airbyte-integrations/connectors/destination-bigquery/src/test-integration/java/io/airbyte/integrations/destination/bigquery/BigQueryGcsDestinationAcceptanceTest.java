/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import static org.junit.jupiter.api.TestInstance.Lifecycle.PER_CLASS;

import com.amazonaws.services.s3.AmazonS3;
import io.airbyte.cdk.integrations.base.DestinationConfig;
import io.airbyte.cdk.integrations.destination.gcs.GcsDestinationConfig;
import io.airbyte.cdk.integrations.standardtest.destination.DestinationAcceptanceTest;
import java.nio.file.Path;
import java.util.HashSet;
import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.TestInstance;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Disabled
@TestInstance(PER_CLASS)
public class BigQueryGcsDestinationAcceptanceTest extends AbstractBigQueryDestinationAcceptanceTest {

  private AmazonS3 s3Client;
  private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryGcsDestinationAcceptanceTest.class);

  /**
   * Sets up secretsFile path as well as BigQuery and GCS instances for verification and cleanup This
   * function will be called before EACH test.
   *
   * @param testEnv - information about the test environment.
   * @param TEST_SCHEMAS
   * @throws Exception - can throw any exception, test framework will handle.
   * @see DestinationAcceptanceTest#setUpInternal()
   */
  @Override
  protected void setup(final TestDestinationEnv testEnv, final HashSet<String> TEST_SCHEMAS) throws Exception {
    // use secrets file with GCS staging config
    secretsFile = Path.of("secrets/credentials-gcs-staging.json");
    setUpBigQuery();
    removeOldNamespaces();

    DestinationConfig.initialize(config);

    // the setup steps below are specific to GCS staging use case
    final GcsDestinationConfig gcsDestinationConfig = GcsDestinationConfig
        .getGcsDestinationConfig(BigQueryUtils.getGcsJsonNodeConfig(config));
    this.s3Client = gcsDestinationConfig.getS3Client();
  }

  /**
   * Removes data from bigquery and GCS This function will be called after EACH test
   *
   * @param testEnv - information about the test environment.
   * @throws Exception - can throw any exception, test framework will handle.
   * @see DestinationAcceptanceTest#tearDownInternal()
   */
  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    tearDownBigQuery();
    tearDownGcs();
  }

  protected void tearDownGcs() {
    BigQueryDestinationTestUtils.tearDownGcs(s3Client, config, LOGGER);
  }

}
