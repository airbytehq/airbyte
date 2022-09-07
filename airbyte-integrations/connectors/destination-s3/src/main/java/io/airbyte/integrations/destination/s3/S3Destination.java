/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3;

import io.airbyte.integrations.base.IntegrationRunner;

public class S3Destination extends BaseS3Destination {


  public S3Destination() {}

  public S3Destination(final S3DestinationConfigFactory s3DestinationConfigFactory) {
    super(s3DestinationConfigFactory);
  }

  public static void main(String[] args) throws Exception {
    new IntegrationRunner(new S3Destination()).run(args);
  }

  @Override
  public StorageProvider storageProvider() {
    return StorageProvider.AWS_S3;
  }
}
