package io.airbyte.integrations.destination.bigquery.helpers;

import com.amazonaws.services.s3.AmazonS3;
import io.airbyte.cdk.integrations.destination.s3.S3BaseChecks;
import io.airbyte.cdk.integrations.destination.gcs.GcsDestinationConfig;
import jakarta.inject.Singleton;

import java.io.IOException;

@Singleton
public class CheckPermissionHelper {

    public void testUpload(final GcsDestinationConfig destinationConfig) throws IOException {
        final AmazonS3 s3Client = destinationConfig.getS3Client();

        // Test single upload (for small files) permissions
        S3BaseChecks.testSingleUpload(s3Client, destinationConfig.getBucketName(), destinationConfig.getBucketPath());

        // Test multipart upload with stream transfer manager
        S3BaseChecks.testMultipartUpload(s3Client, destinationConfig.getBucketName(), destinationConfig.getBucketPath());
    }
}
