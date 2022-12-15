/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3;

import io.airbyte.integrations.base.adaptive.AdaptiveDestinationRunner;

public class S3DestinationRunner {

  public static void main(final String[] args) throws Exception {
    AdaptiveDestinationRunner.baseOnEnv()
        .withOssDestination(S3Destination::new)
        .withCloudDestination(S3DestinationStrictEncrypt::new)
        .run(args);
  }

}
