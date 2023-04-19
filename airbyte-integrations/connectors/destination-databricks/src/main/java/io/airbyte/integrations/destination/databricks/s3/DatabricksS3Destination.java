/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks.s3;

import io.airbyte.integrations.destination.databricks.DatabricksExternalStorageBaseDestination;
import io.airbyte.integrations.destination.databricks.DatabricksStorageConfigProvider;
import io.airbyte.integrations.destination.databricks.DatabricksStreamCopierFactory;
import io.airbyte.integrations.destination.s3.S3BaseChecks;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.integrations.destination.s3.S3StorageOperations;

public class DatabricksS3Destination extends DatabricksExternalStorageBaseDestination {

  @Override
  protected void checkPersistence(DatabricksStorageConfigProvider databricksConfig) {
    S3DestinationConfig s3Config = databricksConfig.getS3DestinationConfigOrThrow();
    S3BaseChecks.attemptS3WriteAndDelete(new S3StorageOperations(getNameTransformer(), s3Config.getS3Client(), s3Config), s3Config, "");
  }

  @Override
  protected DatabricksStreamCopierFactory getStreamCopierFactory() {
    return new DatabricksS3StreamCopierFactory();
  }

}
