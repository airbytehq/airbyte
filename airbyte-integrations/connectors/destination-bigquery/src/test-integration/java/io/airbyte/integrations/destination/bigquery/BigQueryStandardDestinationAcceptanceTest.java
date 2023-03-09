/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import static org.junit.jupiter.api.TestInstance.Lifecycle.PER_CLASS;

import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import java.nio.file.Path;
import org.junit.jupiter.api.TestInstance;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@TestInstance(PER_CLASS)
public class BigQueryStandardDestinationAcceptanceTest extends AbstractBigQueryDestinationAcceptanceTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryStandardDestinationAcceptanceTest.class);

  /**
   * Sets up secretsFile path and BigQuery instance for verification and cleanup This function will be
   * called before EACH test.
   *
   * @see DestinationAcceptanceTest#setUpInternal()
   * @param testEnv - information about the test environment.
   * @throws Exception - can throw any exception, test framework will handle.
   */
  @Override
  protected void setup(TestDestinationEnv testEnv) throws Exception {
    secretsFile = Path.of("secrets/credentials-standard.json");
    setUpBigQuery();
  }

  /**
   * Removes data from bigquery This function will be called after EACH test
   *
   * @see DestinationAcceptanceTest#tearDownInternal()
   * @param testEnv - information about the test environment.
   * @throws Exception - can throw any exception, test framework will handle.
   */
  @Override
  protected void tearDown(TestDestinationEnv testEnv) {
    tearDownBigQuery();
  }

}
