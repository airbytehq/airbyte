package io.airbyte.integrations.destination.gcs;

import com.amazonaws.services.s3.AmazonS3;
import io.airbyte.integrations.destination.NamingConventionTransformer;
import io.airbyte.integrations.destination.s3.BlobStorageOperations;
import io.airbyte.integrations.destination.s3.S3StorageOperations;

public class GcsStorageOperations extends S3StorageOperations implements BlobStorageOperations {

  public GcsStorageOperations(final NamingConventionTransformer nameTransformer,
                              final AmazonS3 s3Client,
                              final GcsDestinationConfig gcsConfig) {
    super(nameTransformer, s3Client, gcsConfig);
  }

}
