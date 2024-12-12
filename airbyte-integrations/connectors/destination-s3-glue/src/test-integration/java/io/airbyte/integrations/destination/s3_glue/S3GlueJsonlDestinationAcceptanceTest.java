/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_glue;

import io.airbyte.cdk.integrations.destination.s3.S3BaseJsonlDestinationAcceptanceTest;
import io.airbyte.cdk.integrations.standardtest.destination.argproviders.DataTypeTestArgumentProvider;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ArgumentsSource;

public class S3GlueJsonlDestinationAcceptanceTest extends S3BaseJsonlDestinationAcceptanceTest {

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

  @ParameterizedTest
  @ArgumentsSource(DataTypeTestArgumentProvider.class)
  public void testDataTypeTestWithNormalization(final String messagesFilename,
                                                final String catalogFilename,
                                                final DataTypeTestArgumentProvider.TestCompatibility testCompatibility)
      throws Exception {

    if (messagesFilename.contains("array")) {
      return;
    }

    super.testDataTypeTestWithNormalization(messagesFilename, catalogFilename, testCompatibility);
  }

}
