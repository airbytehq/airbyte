package io.airbyte.integrations.destination.r2;

import io.airbyte.integrations.destination.s3.S3BaseCsvGzipDestinationAcceptanceTest;

public class R2CsvGzipDestinationAcceptanceTest extends S3BaseCsvGzipDestinationAcceptanceTest {

  @Override
  protected String getImageName() {
    return "airbyte/destination-r2:dev";
  }
}
