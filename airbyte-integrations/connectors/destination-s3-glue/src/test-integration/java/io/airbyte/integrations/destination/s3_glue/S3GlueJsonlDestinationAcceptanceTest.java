/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_glue;

import io.airbyte.integrations.destination.s3.S3BaseJsonlDestinationAcceptanceTest;

public class S3GlueJsonlDestinationAcceptanceTest extends S3BaseJsonlDestinationAcceptanceTest {

  @Override
  protected void tearDown(TestDestinationEnv testEnv) {
    super.tearDown(testEnv);

    GlueDestinationConfig glueDestinationConfig = GlueDestinationConfig.getInstance(configJson);
    try (var glueTestClient = new GlueTestClient(glueDestinationConfig.getAWSGlueInstance())) {

      glueTestClient.purgeDatabase(glueDestinationConfig.getDatabase());

    }
  }

  @Override
  protected String getImageName() {
    return "airbyte/destination-s3-glue:dev";
  }

}
