package io.airbyte.integrations.destination.r2;

import io.airbyte.integrations.destination.s3.S3BaseJsonlDestinationAcceptanceTest;

public class R2JsonlDestinationAcceptanceTest extends S3BaseJsonlDestinationAcceptanceTest {

  @Override
  protected String getImageName() {
    return "airbyte/destination-r2:dev";
  }
}
