package io.airbyte.integrations.destination.iceberg.io;

import java.util.Map;
import org.apache.iceberg.aws.AwsClientFactory;
import org.apache.iceberg.aws.AwsProperties;
import org.apache.iceberg.aws.s3.S3FileIOAwsClientFactory;
import org.apache.iceberg.aws.s3.S3FileIOProperties;
import software.amazon.awssdk.auth.credentials.AwsBasicCredentials;
import software.amazon.awssdk.auth.credentials.AwsCredentialsProvider;
import software.amazon.awssdk.auth.credentials.StaticCredentialsProvider;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.dynamodb.DynamoDbClient;
import software.amazon.awssdk.services.glue.GlueClient;
import software.amazon.awssdk.services.kms.KmsClient;
import software.amazon.awssdk.services.s3.S3AsyncClient;
import software.amazon.awssdk.services.s3.S3Client;
import software.amazon.awssdk.services.s3.S3ClientBuilder;
import software.amazon.awssdk.services.s3.S3Configuration;

/**
 * Custom S3 client factory that disables chunked encoding for compatibility
 * with S3-compatible
 * storage systems (Alibaba OSS, MinIO, etc.) that don't support AWS's
 * proprietary chunked encoding.
 */
public class OssCompatibleS3ClientFactory implements S3FileIOAwsClientFactory, AwsClientFactory {

    private S3FileIOProperties s3FileIOProperties;
    private AwsProperties awsProperties;

    @Override
    public S3Client s3() {
        S3ClientBuilder builder = S3Client.builder();

        // Apply credentials
        String accessKeyId = s3FileIOProperties.accessKeyId();
        String secretAccessKey = s3FileIOProperties.secretAccessKey();
        if (accessKeyId != null && secretAccessKey != null) {
            AwsCredentialsProvider credentials = StaticCredentialsProvider.create(
                    AwsBasicCredentials.create(accessKeyId, secretAccessKey));
            builder.credentialsProvider(credentials);
        }

        // Apply endpoint first
        String endpoint = s3FileIOProperties.endpoint();
        boolean hasCustomEndpoint = endpoint != null && !endpoint.isEmpty();

        if (hasCustomEndpoint) {
            builder.endpointOverride(java.net.URI.create(endpoint));
            // When using custom endpoint (OSS), use a dummy region to prevent SDK from
            // trying to construct AWS-specific URLs
            builder.region(Region.of("me-central-1"));
        } else {
            // Only set region from environment if NOT using custom endpoint
            String region = System.getenv("AWS_REGION");
            if (region == null || region.isEmpty()) {
                region = "me-central-1"; // Default region for AWS
            }
            builder.region(Region.of(region));
        }

        // Build S3Configuration with chunked encoding DISABLED
        S3Configuration.Builder s3ConfigBuilder = S3Configuration.builder()
                .chunkedEncodingEnabled(false); // CRITICAL: Disable chunked encoding for OSS compatibility

        // OSS uses virtual-hosted style, NOT path-style
        // Only enable path-style if explicitly requested
        if (s3FileIOProperties.isPathStyleAccess()) {
            s3ConfigBuilder.pathStyleAccessEnabled(true);
        } else {
            s3ConfigBuilder.pathStyleAccessEnabled(false); // Virtual-hosted style for OSS
        }

        // Apply acceleration if enabled (usually not for S3-compatible storage)
        if (s3FileIOProperties.isAccelerationEnabled()) {
            s3ConfigBuilder.accelerateModeEnabled(true);
        }

        // Apply use ARN region if enabled
        if (s3FileIOProperties.isUseArnRegionEnabled()) {
            s3ConfigBuilder.useArnRegionEnabled(true);
        }

        builder.serviceConfiguration(s3ConfigBuilder.build());

        return builder.build();
    }

    @Override
    public S3AsyncClient s3Async() {
        // Return null - we don't need async client for this use case
        // Iceberg will fall back to sync client
        return null;
    }

    @Override
    public void initialize(Map<String, String> properties) {
        this.s3FileIOProperties = new S3FileIOProperties(properties);
        this.awsProperties = new AwsProperties(properties);
    }

    // AwsClientFactory interface methods - provide stub implementations
    @Override
    public GlueClient glue() {
        return null; // Not needed for S3-only operations
    }

    @Override
    public KmsClient kms() {
        return null; // Not needed for S3-only operations
    }

    @Override
    public DynamoDbClient dynamo() {
        return null; // Not needed for S3-only operations
    }
}
