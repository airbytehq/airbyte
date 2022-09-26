/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.r2;

import io.airbyte.integrations.destination.s3.S3BaseParquetDestinationAcceptanceTest;
import io.airbyte.integrations.destination.s3.StorageProvider;
import org.junit.jupiter.api.Disabled;

/**
 * s3a client not supported by cloudflare R2
 */
@Disabled
public class R2ParquetDestinationAcceptanceTest extends S3BaseParquetDestinationAcceptanceTest {

  @Override
  protected String getImageName() {
    return "airbyte/destination-r2:dev";
  }

  @Override
  public StorageProvider storageProvider() {
    return StorageProvider.CF_R2;
  }

}
