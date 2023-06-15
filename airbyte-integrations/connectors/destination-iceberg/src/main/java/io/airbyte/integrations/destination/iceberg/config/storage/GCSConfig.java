package io.airbyte.integrations.destination.iceberg.config.storage;

import static io.airbyte.integrations.destination.iceberg.IcebergConstants.GCS_BUCKET_LOCATION_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.GCS_WAREHOUSE_URI_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.GCS_PROJECT_ID_CONFIG_KEY;

import static org.apache.commons.lang3.StringUtils.isBlank;
import static org.apache.commons.lang3.StringUtils.isEmpty;

import com.google.cloud.storage.Storage;
import com.google.cloud.storage.StorageOptions;
import com.fasterxml.jackson.databind.JsonNode;
// import io.airbyte.integrations.destination.iceberg.config.storage.credential.S3AWSDefaultProfileCredentialConfig;
// import io.airbyte.integrations.destination.iceberg.config.storage.credential.S3AccessKeyCredentialConfig;
// import io.airbyte.integrations.destination.iceberg.config.storage.credential.S3CredentialConfig;
// import io.airbyte.integrations.destination.iceberg.config.storage.credential.S3CredentialType;
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
 * @author Thomas van Latum on 2023/06/13.
 */
@Slf4j
@Data
@Builder
@AllArgsConstructor
public class GCSConfig implements StorageConfig {
  
  private static final String SCHEMA_SUFFIX = "://";
  /**
   * Lock
   */
  private final Object lock = new Object();

  /**
    * Properties from Destination Config
    */
  private final String warehouseUri;
  private final String bucketLocation;
  private final String projectId;

  private Storage gcsClient;

  public static GCSConfig fromDestinationConfig(@Nonnull final JsonNode config) {
    GCSConfigBuilder builder = new GCSConfigBuilder().bucketLocation(getProperty(config, GCS_BUCKET_LOCATION_CONFIG_KEY));
    
    String warehouseUri = getProperty(config, GCS_WAREHOUSE_URI_CONFIG_KEY);
    if (isBlank(warehouseUri)) {
      throw new IllegalArgumentException("Warehouse URI cannot be blank");
    }
    if (!warehouseUri.startsWith("gs://")){
      throw new IllegalArgumentException("Warehouse URI must start with gs://");
    }
    builder.warehouseUri(warehouseUri);

    String projectId = getProperty(config, GCS_PROJECT_ID_CONFIG_KEY);
    if (isBlank(projectId)) {
      throw new IllegalArgumentException("Project ID cannot be blank");
    }

    return builder.build().setProperty();
  }

  private GCSConfig setProperty() {
    System.setProperty("gcs.location", bucketLocation);
    return this;
  }
  private static String getProperty(@Nonnull final JsonNode config, @Nonnull final String key) {
    final JsonNode node = config.get(key);
    if (node == null) {
    return null;
    }
    return node.asText();
  }

  public Storage getGCSClient() {
    synchronized (lock) {
      if (gcsClient == null) {
        return resetGCSClient();
      }
      return gcsClient;
    }
  }

  private Storage resetGCSClient() {
    synchronized (lock) {
      if (gcsClient != null) {
        //Investigate if this is necessary
      }
      gcsClient = createGCSClient();
      return gcsClient;
    }
  }

  private Storage createGCSClient() {
    log.info("Creating GCS client...");
    return StorageOptions.newBuilder().setProjectId(projectId).build().getService();
  }

  public void check() {
    final Storage gcsClient = this.getGCSClient();
    String prefix = this.warehouseUri.replaceAll("^s3[an]?://.+?/(.+?)/?$", "$1/");
    String tempObjectName = prefix + "_airbyte_connection_test_" +
        UUID.randomUUID().toString().replaceAll("-", "");
    String bucket = this.warehouseUri.replaceAll("^s3[an]?://(.+?)/.+$", "$1");

    log.error(prefix);
    log.info(tempObjectName);

    log.info(gcsClient.get(bucket).toString());

  }


  @Override
  public Map<String, String> sparkConfigMap(String catalogName) {
    Map<String, String> sparkConfig = new HashMap<>();
    // sparkConfig.put("spark.sql.catalog." + catalogName + ".io-impl", "org.apache.iceberg.aws.s3.S3FileIO");
    // sparkConfig.put("spark.sql.catalog." + catalogName + ".warehouse", this.warehouseUri);
    // sparkConfig.put("spark.sql.catalog." + catalogName + ".s3.endpoint", this.endpointWithSchema);
    // sparkConfig.put("spark.sql.catalog." + catalogName + ".s3.access-key-id", this.accessKeyId);
    // sparkConfig.put("spark.sql.catalog." + catalogName + ".s3.secret-access-key", this.secretKey);
    // sparkConfig.put("spark.sql.catalog." + catalogName + ".s3.path-style-access",
    //     String.valueOf(this.pathStyleAccess));
    // sparkConfig.put("spark.hadoop.fs.s3a.access.key", this.accessKeyId);
    // sparkConfig.put("spark.hadoop.fs.s3a.secret.key", this.secretKey);
    // sparkConfig.put("spark.hadoop.fs.s3a.path.style.access", String.valueOf(this.pathStyleAccess));
    // sparkConfig.put("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem");
    // sparkConfig.put("spark.hadoop.fs.s3a.endpoint", this.endpoint);
    // sparkConfig.put("spark.hadoop.fs.s3a.connection.ssl.enabled", String.valueOf(this.sslEnabled));
    // sparkConfig.put("spark.hadoop.fs.s3a.aws.credentials.provider",
    //     "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider");
    return sparkConfig;
  }

  @Override
  public Map<String, String> catalogInitializeProperties() {
    Map<String, String> properties = new HashMap<>();
    // properties.put(CatalogProperties.FILE_IO_IMPL, "org.apache.iceberg.aws.s3.S3FileIO");
    // properties.put("s3.endpoint", this.endpointWithSchema);
    // properties.put("s3.access-key-id", this.accessKeyId);
    // properties.put("s3.secret-access-key", this.secretKey);
    // properties.put("s3.path-style-access", String.valueOf(this.pathStyleAccess));
    return properties;
  }

}