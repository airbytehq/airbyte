/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs;

import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.model.DeleteObjectsRequest.KeyVersion;
import io.airbyte.integrations.destination.NamingConventionTransformer;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.integrations.destination.s3.S3StorageOperations;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class GcsStorageOperations extends S3StorageOperations {

  private static final Logger LOGGER = LoggerFactory.getLogger(GcsStorageOperations.class);

  public GcsStorageOperations(final NamingConventionTransformer nameTransformer,
                              final AmazonS3 s3Client,
                              final S3DestinationConfig s3Config) {
    super(nameTransformer, s3Client, s3Config);
  }

  /**
   * GCS only supports the legacy AmazonS3#doesBucketExist method.
   */
  @Override
  protected boolean doesBucketExist(final String bucket) {
    return s3Client.doesBucketExist(bucket);
  }

  /**
   * This method is overridden because GCS doesn't accept request to delete multiple objects. The only
   * difference is that the AmazonS3#deleteObjects method is replaced with AmazonS3#deleteObject.
   */
  @Override
  protected void cleanUpObjects(final String bucket, final List<KeyVersion> keysToDelete) {
    for (final KeyVersion keyToDelete : keysToDelete) {
      LOGGER.info("Deleting object {}", keyToDelete.getKey());
      s3Client.deleteObject(bucket, keyToDelete.getKey());
    }
  }

  @Override
  protected Map<String, String> getMetadataMapping() {
    return new HashMap<>();
  }

}
