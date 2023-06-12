package io.airbyte.integrations.destination.iceberg.config.storage;

import static io.airbyte.integrations.destination.iceberg.IcebergConstants.S3_ACCESS_KEY_ID_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.S3_BUCKET_REGION_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.S3_ENDPOINT_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.S3_PATH_STYLE_ACCESS_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.S3_SECRET_KEY_CONFIG_KEY;
import static io.airbyte.integrations.destination.iceberg.IcebergConstants.S3_WAREHOUSE_URI_CONFIG_KEY;
import static org.apache.commons.lang3.StringUtils.isBlank;
import static org.apache.commons.lang3.StringUtils.isEmpty;

import com.google.cloud.storage.Storage;
// import com.amazonaws.ClientConfiguration;
// import com.amazonaws.Protocol;
// import com.amazonaws.auth.AWSCredentialsProvider;
// import com.amazonaws.client.builder.AwsClientBuilder;
// import com.amazonaws.services.s3.AmazonS3;
// import com.amazonaws.services.s3.AmazonS3ClientBuilder;
// import com.amazonaws.services.s3.model.ListObjectsRequest;
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
public class GCSConfig implements StorageConfig {
  
  private static final String SCHEMA_SUFFIX = "://";
  /**
   * Lock
   */
  private final Object lock = new Object();

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
        gcsClient.close();
      }
      gcsClient = createGCSClient();
      return gcsClient;
    }
  }

  private Storage createGCSClient() {
    log.info("Creating GCS client...");
    return StorageOptions.getDefaultInstance().getService();
  }

  public void check() {
    final Storage gcsClient = this.getGCSClient();
  }

}