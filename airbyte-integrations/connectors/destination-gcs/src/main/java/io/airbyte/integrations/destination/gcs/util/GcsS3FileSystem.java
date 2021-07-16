package io.airbyte.integrations.destination.gcs.util;

import java.io.IOException;
import org.apache.hadoop.fs.s3a.Retries;
import org.apache.hadoop.fs.s3a.S3AFileSystem;

public class GcsS3FileSystem extends S3AFileSystem {

  /**
   * {@code doesBucketExistV2} does not work for GCS.
   */
  @Override
  @Retries.RetryTranslated
  protected void verifyBucketExistsV2() throws IOException {
    super.verifyBucketExists();
  }

}
