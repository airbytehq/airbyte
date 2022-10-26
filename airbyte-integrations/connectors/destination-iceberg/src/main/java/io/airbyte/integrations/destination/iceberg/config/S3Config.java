package io.airbyte.integrations.destination.iceberg.config;

import static io.airbyte.integrations.destination.iceberg.IcebergConstants.S3_ACCESS_KEY_ID_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.S3_BUCKET_NAME_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.S3_BUCKET_PATH_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.S3_BUCKET_REGION_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.S3_ENDPOINT_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.S3_PATH_STYLE_ACCESS_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.S3_SECRET_KEY_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.S3_SSL_ENABLED_CONFIG_KEY;

import com.amazonaws.ClientConfiguration;
import com.amazonaws.Protocol;
import com.amazonaws.auth.AWSCredentialsProvider;
import com.amazonaws.client.builder.AwsClientBuilder;
import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.AmazonS3ClientBuilder;
import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.destination.iceberg.config.credential.S3AWSDefaultProfileCredentialConfig;
import io.airbyte.integrations.destination.iceberg.config.credential.S3AccessKeyCredentialConfig;
import io.airbyte.integrations.destination.iceberg.config.credential.S3CredentialConfig;
import io.airbyte.integrations.destination.iceberg.config.credential.S3CredentialType;
import javax.annotation.Nonnull;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.extern.slf4j.Slf4j;

/**
 * @author Leibniz on 2022/10/26.
 */
@Slf4j
@Data
@Builder
@AllArgsConstructor
public class S3Config {

    private final Object lock = new Object();
    private final String endpoint;
    private final String bucketName;
    private final String bucketPath;
    private final String bucketRegion;
    private final String accessKeyId;
    private final String secretKey;
    private final S3CredentialConfig credentialConfig;
    private final boolean pathStyleAccess;
    private final boolean sslEnabled;
    private final IcebergCatalogConfig catalogConfig;
    private AmazonS3 s3Client;

    public static S3Config fromDestinationConfig(@Nonnull final JsonNode config) {
        S3ConfigBuilder builder = new S3ConfigBuilder().bucketName(getProperty(config, S3_BUCKET_NAME_CONFIG_KEY))
            .bucketRegion(getProperty(config, S3_BUCKET_REGION_CONFIG_KEY))
            .bucketPath(getProperty(config, S3_BUCKET_PATH_CONFIG_KEY))
            .endpoint(getProperty(config, S3_ENDPOINT_CONFIG_KEY));

        if (config.has(S3_ACCESS_KEY_ID_CONFIG_KEY)) {
            String accessKeyId = getProperty(config, S3_ACCESS_KEY_ID_CONFIG_KEY);
            String secretAccessKey = getProperty(config, S3_SECRET_KEY_CONFIG_KEY);
            builder.credentialConfig(new S3AccessKeyCredentialConfig(accessKeyId, secretAccessKey))
                .accessKeyId(accessKeyId)
                .secretKey(secretAccessKey);
        } else {
            builder.credentialConfig(new S3AWSDefaultProfileCredentialConfig()).accessKeyId("").secretKey("");
        }

        if (config.has(S3_PATH_STYLE_ACCESS_CONFIG_KEY)) {
            builder.pathStyleAccess(config.get(S3_PATH_STYLE_ACCESS_CONFIG_KEY).booleanValue());
        } else {
            builder.pathStyleAccess(false);
        }

        if (config.has(S3_SSL_ENABLED_CONFIG_KEY)) {
            builder.sslEnabled(config.get(S3_SSL_ENABLED_CONFIG_KEY).booleanValue());
        } else {
            builder.sslEnabled(true);
        }

        builder.catalogConfig(IcebergCatalogConfig.fromDestinationConfig(config));
        return builder.build();
    }

    private static String getProperty(@Nonnull final JsonNode config, @Nonnull final String key) {
        final JsonNode node = config.get(key);
        if (node == null) {
            return null;
        }
        return node.asText();
    }

    public AmazonS3 getS3Client() {
        synchronized (lock) {
            if (s3Client == null) {
                return resetS3Client();
            }
            return s3Client;
        }
    }

    AmazonS3 resetS3Client() {
        synchronized (lock) {
            if (s3Client != null) {
                s3Client.shutdown();
            }
            s3Client = createS3Client();
            return s3Client;
        }
    }

    protected AmazonS3 createS3Client() {
        log.info("Creating S3 client...");

        final AWSCredentialsProvider credentialsProvider = credentialConfig.getS3CredentialsProvider();
        final S3CredentialType credentialType = credentialConfig.getCredentialType();

        if (S3CredentialType.DEFAULT_PROFILE == credentialType) {
            return AmazonS3ClientBuilder.standard()
                .withRegion(bucketRegion)
                .withCredentials(credentialsProvider)
                .build();
        }

        if (null == endpoint || endpoint.isEmpty()) {
            return AmazonS3ClientBuilder.standard()
                .withCredentials(credentialsProvider)
                .withRegion(bucketRegion)
                .build();
        }

        final ClientConfiguration clientConfiguration = new ClientConfiguration().withProtocol(Protocol.HTTPS);
        clientConfiguration.setSignerOverride("AWSS3V4SignerType");

        return AmazonS3ClientBuilder.standard()
            .withEndpointConfiguration(new AwsClientBuilder.EndpointConfiguration(endpoint, bucketRegion))
            .withPathStyleAccessEnabled(true)
            .withClientConfiguration(clientConfiguration)
            .withCredentials(credentialsProvider)
            .build();
    }

    public static class S3ConfigFactory {

        public S3Config parseS3Config(final JsonNode config) {
            return S3Config.fromDestinationConfig(config);
        }
    }
}
