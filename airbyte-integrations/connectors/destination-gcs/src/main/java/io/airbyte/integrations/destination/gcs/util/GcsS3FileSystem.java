/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs.util;

import java.io.IOException;
import org.apache.hadoop.fs.s3a.Retries;
import org.apache.hadoop.fs.s3a.S3AFileSystem;

/**
 * Patch {@link S3AFileSystem} to make it work for GCS.
 */
public class GcsS3FileSystem extends S3AFileSystem {

  /**
   * Method {@code doesBucketExistV2} used in the {@link S3AFileSystem#verifyBucketExistsV2} does not
   * work for GCS.
   */
  @Override
  @Retries.RetryTranslated
  protected void verifyBucketExistsV2() throws IOException {
    super.verifyBucketExists();
  }

}
