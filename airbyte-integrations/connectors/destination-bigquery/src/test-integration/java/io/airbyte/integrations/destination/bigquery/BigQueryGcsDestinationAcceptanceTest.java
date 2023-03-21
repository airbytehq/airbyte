/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import static org.assertj.core.api.AssertionsForClassTypes.assertThat;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.TestInstance.Lifecycle.PER_CLASS;

import com.amazonaws.services.s3.AmazonS3;
import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.string.Strings;
import io.airbyte.config.StandardCheckConnectionOutput;
import io.airbyte.config.StandardCheckConnectionOutput.Status;
import io.airbyte.integrations.destination.gcs.GcsDestinationConfig;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import java.nio.file.Path;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestInstance;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@TestInstance(PER_CLASS)
public class BigQueryGcsDestinationAcceptanceTest extends AbstractBigQueryDestinationAcceptanceTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryGcsDestinationAcceptanceTest.class);
  private static final String NO_GCS_CREATE_PRIVILEGES_ERR_MSG =
      "User does not have bigquery.datasets.create permission in project";
  private static final String NO_GCS_WRITE_PRIVILEGES_ERR_MSG =
      "User does not have bigquery.jobs.create permission in project ";
  private AmazonS3 s3Client;

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

  @Test
  public void testCheckWithNoCreateGcsPermissionConnection() throws Exception {
    String datasetId = Strings.addRandomSuffix("bq_dest_integration_test", "_", 8);
    JsonNode config = BigQueryDestinationTestUtils.createConfig(
        Path.of("secrets/copy_gcs_no_create_roles_config.json"), datasetId);

    StandardCheckConnectionOutput standardCheckConnectionOutput = runCheck(config);

    assertEquals(Status.FAILED, standardCheckConnectionOutput.getStatus());
    assertThat(standardCheckConnectionOutput.getMessage()).contains(NO_GCS_CREATE_PRIVILEGES_ERR_MSG);
  }

  @Test
  public void testCheckWithNoWriteGcsPermissionConnection() throws Exception {
    String datasetId = Strings.addRandomSuffix("bq_dest_integration_test", "_", 8);
    JsonNode config = BigQueryDestinationTestUtils.createConfig(
        Path.of("secrets/copy_gcs_no_write_roles_config.json"), datasetId);

    StandardCheckConnectionOutput standardCheckConnectionOutput = runCheck(config);

    assertEquals(Status.FAILED, standardCheckConnectionOutput.getStatus());
    assertThat(standardCheckConnectionOutput.getMessage()).contains(NO_GCS_WRITE_PRIVILEGES_ERR_MSG);
  }

}
