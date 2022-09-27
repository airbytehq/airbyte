/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.r2;

import io.airbyte.integrations.destination.s3.S3BaseCsvGzipDestinationAcceptanceTest;
import io.airbyte.integrations.destination.s3.StorageProvider;

public class R2CsvGzipDestinationAcceptanceTest extends S3BaseCsvGzipDestinationAcceptanceTest {

  @Override
  protected String getImageName() {
    return "airbyte/destination-r2:dev";
  }

  @Override
  public StorageProvider storageProvider() {
    return StorageProvider.CF_R2;
  }

}
