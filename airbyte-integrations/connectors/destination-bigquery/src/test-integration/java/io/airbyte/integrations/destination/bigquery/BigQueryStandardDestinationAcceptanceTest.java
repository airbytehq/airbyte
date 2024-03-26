/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import static org.junit.jupiter.api.TestInstance.Lifecycle.PER_CLASS;

import io.airbyte.cdk.integrations.standardtest.destination.DestinationAcceptanceTest;
import java.nio.file.Path;
import java.util.HashSet;
import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.TestInstance;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Disabled
@TestInstance(PER_CLASS)
public class BigQueryStandardDestinationAcceptanceTest extends AbstractBigQueryDestinationAcceptanceTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryStandardDestinationAcceptanceTest.class);

  /**
   * Sets up secretsFile path and BigQuery instance for verification and cleanup This function will be
   * called before EACH test.
   *
   * @param testEnv - information about the test environment.
   * @param TEST_SCHEMAS
   * @throws Exception - can throw any exception, test framework will handle.
   * @see DestinationAcceptanceTest#setUpInternal()
   */
  @Override
  protected void setup(final TestDestinationEnv testEnv, final HashSet<String> TEST_SCHEMAS) throws Exception {
    secretsFile = Path.of("secrets/credentials-standard.json");
    setUpBigQuery();
    removeOldNamespaces();
  }

  /**
   * Removes data from bigquery This function will be called after EACH test
   *
   * @param testEnv - information about the test environment.
   * @throws Exception - can throw any exception, test framework will handle.
   * @see DestinationAcceptanceTest#tearDownInternal()
   */
  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    tearDownBigQuery();
  }

}
