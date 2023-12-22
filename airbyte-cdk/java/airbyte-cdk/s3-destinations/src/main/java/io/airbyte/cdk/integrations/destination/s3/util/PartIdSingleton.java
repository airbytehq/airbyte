package io.airbyte.cdk.integrations.destination.s3.util;

import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.model.ObjectListing;
import io.airbyte.cdk.integrations.destination.s3.S3DestinationConfig;
import java.util.UUID;

public class PartIdSingleton {
  private static PartIdSingleton instance = null;
  private Integer startingCount = null;
  private Integer invocationCount = 0;
  private Boolean usingUUIDs = null;
  private Boolean locked = false;

  private PartIdSingleton() {}

  public static synchronized PartIdSingleton getInstance() {
    if (instance == null) {
      instance = new PartIdSingleton();
    }

    return instance;
  }

  public synchronized String getPartId(final AmazonS3 s3Client, final S3DestinationConfig s3Config, final String objectPath) throws InterruptedException {
    initialize(s3Client, s3Config, objectPath);

    if (usingUUIDs) {
      return UUID.randomUUID().toString();
    } else {
      invocationCount++;
      return Integer.toString(startingCount + invocationCount); // this will produce 1-indexed file names.
    }
  }

  /**
   * We can now assume that S3's directory listing is factual (no lag with new files)
   * But, we need to be sure that multiple threads aren't both looking to write the next ID at the same time.
   */

  // TODO: Caching needs to be per objectPath, not globally
  private synchronized void initialize (final AmazonS3 s3Client, final S3DestinationConfig s3Config, final String objectPath) throws InterruptedException {
    // usingUUIDs being null can also be a signal for the need to load what's in the bucket the first time
    if (usingUUIDs != null) {
      return;
    }

    final String bucket = s3Config.getBucketName();

    if (locked) {
      // TODO: Sleepy Recursion is bad.
      Thread.sleep(1000);
      initialize(s3Client, s3Config, objectPath);
    } else {
      locked = true;

      try {
        final ObjectListing objects = s3Client.listObjects(bucket, objectPath);
        if (objects.isTruncated()) {
          usingUUIDs = true;
          startingCount = objects.getObjectSummaries().size();
        } else {
          usingUUIDs = false;
        }
      } finally {
        locked = false;
      }
    }
  }
}

