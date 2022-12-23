/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import com.amazonaws.services.s3.AmazonS3;
import io.airbyte.commons.string.Strings;
import io.airbyte.integrations.destination.gcs.GcsDestinationConfig;
import java.nio.file.Path;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class BigQueryGcsDestinationAcceptanceTest extends BigQueryDestinationAcceptanceTest {
  private AmazonS3 s3Client;
  protected boolean gcsTornDown = false;
  private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryGcsDestinationAcceptanceTest.class);

  @Override
  protected void setup(final TestDestinationEnv testEnv) throws Exception {
    bigquery = null;
    dataset = null;
    bqTornDown = false;
    gcsTornDown = false;

    final String datasetId = Strings.addRandomSuffix("airbyte_tests", "_", 8);
    config = BigQueryDestinationTestUtils.createConfig(Path.of("secrets/credentials-gcs-staging.json"), datasetId);
    setUpBigQuery(config, datasetId);
    final GcsDestinationConfig gcsDestinationConfig = GcsDestinationConfig
        .getGcsDestinationConfig(BigQueryUtils.getGcsJsonNodeConfig(config));
    this.s3Client = gcsDestinationConfig.getS3Client();

    addShutdownHook();
  }

  @Override
  protected void addShutdownHook() {
    Runtime.getRuntime().addShutdownHook(new Thread(() -> {
      if (!bqTornDown) {
        bqTornDown = BigQueryDestinationTestUtils.tearDownBigQuery(bigquery, dataset, LOGGER);
      }
      if(!gcsTornDown) {
        gcsTornDown = BigQueryDestinationTestUtils.tearDownGcs(s3Client, config, LOGGER);
      }
    }));
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    bqTornDown = BigQueryDestinationTestUtils.tearDownBigQuery(bigquery, dataset, LOGGER);
    gcsTornDown = BigQueryDestinationTestUtils.tearDownGcs(s3Client, config, LOGGER);
  }

}
