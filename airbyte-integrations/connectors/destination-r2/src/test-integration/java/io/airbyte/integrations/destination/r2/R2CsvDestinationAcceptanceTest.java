/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.r2;

import io.airbyte.integrations.destination.s3.S3BaseCsvDestinationAcceptanceTest;
import io.airbyte.integrations.destination.s3.StorageProvider;

public class R2CsvDestinationAcceptanceTest extends S3BaseCsvDestinationAcceptanceTest {

  @Override
  protected String getImageName() {
    return "airbyte/destination-r2:dev";
  }

  @Override
  public StorageProvider storageProvider() {
    return StorageProvider.CF_R2;
  }

}
