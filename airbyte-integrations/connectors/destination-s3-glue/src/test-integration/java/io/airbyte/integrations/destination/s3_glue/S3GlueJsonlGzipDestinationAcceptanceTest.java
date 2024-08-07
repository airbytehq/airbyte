/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_glue;

import io.airbyte.cdk.integrations.destination.s3.S3BaseJsonlGzipDestinationAcceptanceTest;

public class S3GlueJsonlGzipDestinationAcceptanceTest extends S3BaseJsonlGzipDestinationAcceptanceTest {

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    super.tearDown(testEnv);

    final GlueDestinationConfig glueDestinationConfig = GlueDestinationConfig.getInstance(configJson);
    try (final var glueTestClient = new GlueTestClient(glueDestinationConfig.getAWSGlueInstance())) {

      glueTestClient.purgeDatabase(glueDestinationConfig.getDatabase());

    }
  }

  @Override
  protected String getImageName() {
    return "airbyte/destination-s3-glue:dev";
  }

}
