/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.r2;

import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.destination.s3.BaseS3Destination;
import io.airbyte.integrations.destination.s3.StorageProvider;

public class R2Destination extends BaseS3Destination {

  public static void main(String[] args) throws Exception {
    System.setProperty("com.amazonaws.services.s3.disableGetObjectMD5Validation", "true");
    System.setProperty("com.amazonaws.services.s3.disablePutObjectMD5Validation", "true");
    new IntegrationRunner(new R2Destination()).run(args);
  }

  @Override
  public StorageProvider storageProvider() {
    return StorageProvider.CF_R2;
  }

}
