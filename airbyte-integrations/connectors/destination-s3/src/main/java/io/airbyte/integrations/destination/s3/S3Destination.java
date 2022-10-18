/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.integrations.base.IntegrationRunner;

public class S3Destination extends BaseS3Destination {

  public S3Destination() {}

  @VisibleForTesting
  protected S3Destination(final S3DestinationConfigFactory s3DestinationConfigFactory) {
    super(s3DestinationConfigFactory);
  }

  public static void main(final String[] args) throws Exception {
    new IntegrationRunner(new S3Destination()).run(args);
  }

  @Override
  public StorageProvider storageProvider() {
    return StorageProvider.AWS_S3;
  }

}
