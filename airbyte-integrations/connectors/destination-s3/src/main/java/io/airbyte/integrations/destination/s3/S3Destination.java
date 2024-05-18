/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.cdk.integrations.base.IntegrationRunner;
import io.airbyte.cdk.integrations.destination.s3.BaseS3Destination;
import io.airbyte.cdk.integrations.destination.s3.S3DestinationConfigFactory;
import io.airbyte.cdk.integrations.destination.s3.StorageProvider;
import java.util.Map;

public class S3Destination extends BaseS3Destination {

  public S3Destination() {}

  @VisibleForTesting
  protected S3Destination(final S3DestinationConfigFactory s3DestinationConfigFactory, Map<String, String> env) {
    super(s3DestinationConfigFactory, env);
  }

  public static void main(final String[] args) throws Exception {
    new IntegrationRunner(new S3Destination()).run(args);
  }

  @Override
  public StorageProvider storageProvider() {
    return StorageProvider.AWS_S3;
  }

}
