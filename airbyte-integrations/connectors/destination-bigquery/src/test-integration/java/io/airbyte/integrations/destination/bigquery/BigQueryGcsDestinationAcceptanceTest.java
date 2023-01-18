/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import static org.junit.jupiter.api.TestInstance.Lifecycle.PER_CLASS;

import com.amazonaws.services.s3.AmazonS3;
import io.airbyte.integrations.destination.gcs.GcsDestinationConfig;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import java.nio.file.Path;
import org.junit.jupiter.api.TestInstance;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@TestInstance(PER_CLASS)
public class BigQueryGcsDestinationAcceptanceTest extends AbstractBigQueryDestinationAcceptanceTest {

  private AmazonS3 s3Client;
  private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryGcsDestinationAcceptanceTest.class);

  /**
   * Sets up secretsFile path as well as BigQuery and GCS instances for verification and cleanup This
   * function will be called before EACH test.
   *
   * @see DestinationAcceptanceTest#setUpInternal()
   * @param testEnv - information about the test environment.
   * @throws Exception - can throw any exception, test framework will handle.
   */
  @Override
  protected void setup(TestDestinationEnv testEnv) throws Exception {
    // use secrets file with GCS staging config
    secretsFile = Path.of("secrets/credentials-gcs-staging.json");
    setUpBigQuery();

    // the setup steps below are specific to GCS staging use case
    final GcsDestinationConfig gcsDestinationConfig = GcsDestinationConfig
        .getGcsDestinationConfig(BigQueryUtils.getGcsJsonNodeConfig(config));
    this.s3Client = gcsDestinationConfig.getS3Client();
  }

  /**
   * Removes data from bigquery and GCS This function will be called after EACH test
   *
   * @see DestinationAcceptanceTest#tearDownInternal()
   * @param testEnv - information about the test environment.
   * @throws Exception - can throw any exception, test framework will handle.
   */
  @Override
  protected void tearDown(TestDestinationEnv testEnv) {
    tearDownBigQuery();
    tearDownGcs();
  }

  protected void tearDownGcs() {
    BigQueryDestinationTestUtils.tearDownGcs(s3Client, config, LOGGER);
  }

}
