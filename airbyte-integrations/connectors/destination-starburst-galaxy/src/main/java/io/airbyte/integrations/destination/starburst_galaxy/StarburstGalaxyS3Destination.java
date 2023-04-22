/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.starburst_galaxy;

import static io.airbyte.integrations.destination.s3.S3BaseChecks.attemptS3WriteAndDelete;

import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.integrations.destination.s3.S3StorageOperations;

public class StarburstGalaxyS3Destination
    extends StarburstGalaxyBaseDestination {

  @Override
  protected void checkPersistence(StarburstGalaxyStagingStorageConfig galaxyStorageConfig) {
    S3DestinationConfig s3Config = galaxyStorageConfig.getS3DestinationConfigOrThrow();
    attemptS3WriteAndDelete(new S3StorageOperations(getNameTransformer(), s3Config.getS3Client(), s3Config), s3Config, "");
  }

  @Override
  protected StarburstGalaxyStreamCopierFactory getStreamCopierFactory() {
    return new StarburstGalaxyS3StreamCopierFactory();
  }

}
