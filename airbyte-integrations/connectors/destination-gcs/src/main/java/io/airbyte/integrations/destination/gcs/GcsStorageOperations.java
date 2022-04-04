/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs;

import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.model.DeleteObjectsRequest.KeyVersion;
import com.amazonaws.services.s3.model.ObjectListing;
import io.airbyte.integrations.destination.NamingConventionTransformer;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.integrations.destination.s3.S3StorageOperations;
import java.util.List;
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
   * This method is overridden because GCS doesn't accept request to delete multiple objects. The
   * only difference is that the AmazonS3#deleteObjects method is replaced with
   * AmazonS3#deleteObject.
   */
  @Override
  public void cleanUpBucketObject(final String objectPath, final List<String> stagedFiles) {
    final String bucket = s3Config.getBucketName();
    ObjectListing objects = s3Client.listObjects(bucket, objectPath);
    while (objects.getObjectSummaries().size() > 0) {
      final List<KeyVersion> keysToDelete = objects.getObjectSummaries()
          .stream()
          .map(obj -> new KeyVersion(obj.getKey()))
          .filter(obj -> stagedFiles.isEmpty() || stagedFiles.contains(obj.getKey()))
          .toList();
      for (final KeyVersion keyToDelete : keysToDelete) {
        s3Client.deleteObject(bucket, keyToDelete.getKey());
      }
      LOGGER.info("Storage bucket {} has been cleaned-up ({} objects were deleted)...", objectPath, keysToDelete.size());
      if (objects.isTruncated()) {
        objects = s3Client.listNextBatchOfObjects(objects);
      } else {
        break;
      }
    }
  }

}
