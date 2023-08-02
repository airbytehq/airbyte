/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.TestInstance.Lifecycle.PER_CLASS;

import com.amazonaws.services.s3.AmazonS3;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.DestinationConfig;
import io.airbyte.integrations.destination.gcs.GcsDestinationConfig;
import io.airbyte.integrations.destination.record_buffer.FileBuffer;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import java.nio.file.Path;
import org.junit.jupiter.api.Test;
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

    DestinationConfig.initialize(config);

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

  /*
   * FileBuffer Default Tests
   */
  @Test
  public void testGetFileBufferDefault() {
    final BigQueryDestination destination = new BigQueryDestination();
    assertEquals(destination.getNumberOfFileBuffers(config),
        FileBuffer.DEFAULT_MAX_CONCURRENT_STREAM_IN_BUFFER);
  }

  @Test
  public void testGetFileBufferMaxLimited() {
    final JsonNode defaultConfig = Jsons.clone(config);
    ((ObjectNode) defaultConfig.get(BigQueryConsts.LOADING_METHOD)).put(FileBuffer.FILE_BUFFER_COUNT_KEY, 100);
    final BigQueryDestination destination = new BigQueryDestination();
    assertEquals(FileBuffer.MAX_CONCURRENT_STREAM_IN_BUFFER, destination.getNumberOfFileBuffers(defaultConfig));
  }

  @Test
  public void testGetMinimumFileBufferCount() {
    final JsonNode defaultConfig = Jsons.clone(config);
    ((ObjectNode) defaultConfig.get(BigQueryConsts.LOADING_METHOD)).put(FileBuffer.FILE_BUFFER_COUNT_KEY, 1);
    final BigQueryDestination destination = new BigQueryDestination();
    // User cannot set number of file counts below the default file buffer count, which is existing
    // behavior
    assertEquals(FileBuffer.DEFAULT_MAX_CONCURRENT_STREAM_IN_BUFFER, destination.getNumberOfFileBuffers(defaultConfig));
  }

}
