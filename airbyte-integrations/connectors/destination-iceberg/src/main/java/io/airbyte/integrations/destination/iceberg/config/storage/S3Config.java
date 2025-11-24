/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.config.storage;

import static io.airbyte.integrations.destination.iceberg.IcebergConstants.HTTP_PREFIX;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.S3_ACCESS_KEY_ID_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.S3_BUCKET_REGION_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.S3_ENDPOINT_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.S3_PATH_STYLE_ACCESS_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.S3_SECRET_KEY_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.S3_WAREHOUSE_URI_CONFIG_KEY;
import static org.apache.commons.lang3.StringUtils.isBlank;
import static org.apache.commons.lang3.StringUtils.isEmpty;

import com.amazonaws.ClientConfiguration;
import com.amazonaws.Protocol;
import com.amazonaws.auth.AWSCredentialsProvider;
import com.amazonaws.client.builder.AwsClientBuilder;
import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.AmazonS3ClientBuilder;
import com.amazonaws.services.s3.model.ListObjectsRequest;
import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.destination.iceberg.config.storage.credential.S3AWSDefaultProfileCredentialConfig;
import io.airbyte.integrations.destination.iceberg.config.storage.credential.S3AccessKeyCredentialConfig;
import io.airbyte.integrations.destination.iceberg.config.storage.credential.S3CredentialConfig;
import io.airbyte.integrations.destination.iceberg.config.storage.credential.S3CredentialType;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import javax.annotation.Nonnull;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.extern.slf4j.Slf4j;
import org.apache.iceberg.CatalogProperties;

/**
 * @author Leibniz on 2022/10/26.
 */
@Slf4j
@Data
@Builder
@AllArgsConstructor
public class S3Config implements StorageConfig {

  private static final String SCHEMA_SUFFIX = "://";
  /**
   * Lock
   */
  private final Object lock = new Object();

  /**
   * Properties from Destination Config
   */
  private final String endpoint;
  private final String endpointWithSchema;
  private final String warehouseUri;
  private final String bucketRegion;
  private final String accessKeyId;
  private final String secretKey;
  private final S3CredentialConfig credentialConfig;
  private final boolean pathStyleAccess;
  private final boolean sslEnabled;

  private AmazonS3 s3Client;

  public static S3Config fromDestinationConfig(@Nonnull final JsonNode config) {
    S3ConfigBuilder builder = new S3ConfigBuilder().bucketRegion(getProperty(config, S3_BUCKET_REGION_CONFIG_KEY));

    String warehouseUri = getProperty(config, S3_WAREHOUSE_URI_CONFIG_KEY);
    if (isBlank(warehouseUri)) {
      throw new IllegalArgumentException(S3_WAREHOUSE_URI_CONFIG_KEY + " cannot be null");
    }
    if (!warehouseUri.startsWith("s3://") && !warehouseUri.startsWith("s3n://")
        && !warehouseUri.startsWith("s3a://")) {
      throw new IllegalArgumentException(
          S3_WAREHOUSE_URI_CONFIG_KEY + " must starts with 's3://' or 's3n://' or 's3a://'");
    }
    builder.warehouseUri(warehouseUri);

    String endpointStr = getProperty(config, S3_ENDPOINT_CONFIG_KEY);
    if (isBlank(endpointStr)) {
      // use Amazon S3
      builder.sslEnabled(true);
    } else {
      boolean sslEnabled = !endpointStr.startsWith(HTTP_PREFIX);
      String pureEndpoint = removeSchemaSuffix(endpointStr);
      builder.sslEnabled(sslEnabled);
      builder.endpoint(pureEndpoint);
      if (sslEnabled) {
        builder.endpointWithSchema("https://" + pureEndpoint);
      } else {
        builder.endpointWithSchema(HTTP_PREFIX + pureEndpoint);
      }
    }

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
      builder.pathStyleAccess(true);
    }

    return builder.build().setProperty();
  }

  private S3Config setProperty() {
    System.setProperty("aws.region", bucketRegion);
    System.setProperty("aws.accessKeyId", accessKeyId);
    System.setProperty("aws.secretAccessKey", secretKey);
    return this;
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

  private AmazonS3 resetS3Client() {
    synchronized (lock) {
      if (s3Client != null) {
        s3Client.shutdown();
      }
      s3Client = createS3Client();
      return s3Client;
    }
  }

  private AmazonS3 createS3Client() {
    log.info("Creating S3 client...");

    final AWSCredentialsProvider credentialsProvider = credentialConfig.getS3CredentialsProvider();
    final S3CredentialType credentialType = credentialConfig.getCredentialType();

    if (S3CredentialType.DEFAULT_PROFILE == credentialType) {
      return AmazonS3ClientBuilder.standard()
          .withRegion(bucketRegion)
          .withCredentials(credentialsProvider)
          .build();
    }

    if (isEmpty(endpoint)) {
      return AmazonS3ClientBuilder.standard()
          .withCredentials(credentialsProvider)
          .withRegion(bucketRegion)
          .build();
    }

    final ClientConfiguration clientConfiguration = new ClientConfiguration().withProtocol(Protocol.HTTPS);
    clientConfiguration.setSignerOverride("AWSS3V4SignerType");

    return AmazonS3ClientBuilder.standard()
        .withEndpointConfiguration(new AwsClientBuilder.EndpointConfiguration(endpointWithSchema, bucketRegion))
        .withPathStyleAccessEnabled(true)
        .withClientConfiguration(clientConfiguration)
        .withCredentials(credentialsProvider)
        .build();
  }

  public void check() {
    final AmazonS3 s3Client = this.getS3Client();

    // normalize path
    String prefix = this.warehouseUri.replaceAll("^s3[an]?://.+?/(.+?)/?$", "$1/");
    String tempObjectName = prefix + "_airbyte_connection_test_" +
        UUID.randomUUID().toString().replaceAll("-", "");
    String bucket = this.warehouseUri.replaceAll("^s3[an]?://(.+?)/.+$", "$1");

    // check bucket exists
    if (!s3Client.doesBucketExistV2(bucket)) {
      log.info("Bucket {} does not exist; creating...", bucket);
      s3Client.createBucket(bucket);
      log.info("Bucket {} has been created.", bucket);
    }

    // try puts temp object
    s3Client.putObject(bucket, tempObjectName, "check-content");

    // check listObjects
    log.info("Started testing if IAM user can call listObjects on the destination bucket");
    final ListObjectsRequest request = new ListObjectsRequest().withBucketName(bucket).withMaxKeys(1);
    s3Client.listObjects(request);
    log.info("Finished checking for listObjects permission");

    // delete temp object
    s3Client.deleteObject(bucket, tempObjectName);
  }

  private static String removeSchemaSuffix(String endpoint) {
    if (endpoint.contains(SCHEMA_SUFFIX)) {
      int schemaSuffixIndex = endpoint.indexOf(SCHEMA_SUFFIX) + SCHEMA_SUFFIX.length();
      return endpoint.substring(schemaSuffixIndex);
    } else {
      return endpoint;
    }
  }

  @Override
  public Map<String, String> sparkConfigMap(String catalogName) {
    Map<String, String> sparkConfig = new HashMap<>();
    sparkConfig.put("spark.sql.catalog." + catalogName + ".io-impl", "org.apache.iceberg.aws.s3.S3FileIO");
    sparkConfig.put("spark.sql.catalog." + catalogName + ".warehouse", this.warehouseUri);
    if (this.endpointWithSchema != null && !this.endpointWithSchema.isEmpty()) {
      sparkConfig.put("spark.sql.catalog." + catalogName + ".s3.endpoint", this.endpointWithSchema);
    }
    sparkConfig.put("spark.sql.catalog." + catalogName + ".s3.access-key-id", this.accessKeyId);
    sparkConfig.put("spark.sql.catalog." + catalogName + ".s3.secret-access-key", this.secretKey);
    sparkConfig.put("spark.sql.catalog." + catalogName + ".s3.path-style-access",
        String.valueOf(this.pathStyleAccess));
    sparkConfig.put("spark.hadoop.fs.s3a.access.key", this.accessKeyId);
    sparkConfig.put("spark.hadoop.fs.s3a.secret.key", this.secretKey);
    sparkConfig.put("spark.hadoop.fs.s3a.path.style.access", String.valueOf(this.pathStyleAccess));
    sparkConfig.put("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem");
    if (this.endpoint != null && !this.endpoint.isEmpty()) {
      sparkConfig.put("spark.hadoop.fs.s3a.endpoint", this.endpoint);
    }
    sparkConfig.put("spark.hadoop.fs.s3a.connection.ssl.enabled", String.valueOf(this.sslEnabled));
    sparkConfig.put("spark.hadoop.fs.s3a.aws.credentials.provider",
        "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider");
    return sparkConfig;
  }

  @Override
  public Map<String, String> catalogInitializeProperties() {
    Map<String, String> properties = new HashMap<>();
    properties.put(CatalogProperties.FILE_IO_IMPL, "org.apache.iceberg.aws.s3.S3FileIO");
    if (this.endpointWithSchema != null && !this.endpointWithSchema.isEmpty()) {
      properties.put("s3.endpoint", this.endpointWithSchema);
    }
    properties.put("s3.access-key-id", this.accessKeyId);
    properties.put("s3.secret-access-key", this.secretKey);
    properties.put("s3.path-style-access", String.valueOf(this.pathStyleAccess));
    return properties;
  }

}
