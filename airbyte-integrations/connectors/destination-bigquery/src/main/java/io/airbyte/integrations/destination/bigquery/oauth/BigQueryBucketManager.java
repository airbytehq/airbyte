package io.airbyte.integrations.destination.bigquery.oauth;

import static io.airbyte.integrations.destination.bigquery.BigQueryConsts.CREDENTIALS;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.auth.oauth2.AccessToken;
import com.google.auth.oauth2.GoogleCredentials;
import com.google.auth.oauth2.UserCredentials;
import com.google.cloud.storage.Bucket;
import com.google.cloud.storage.BucketInfo;
import com.google.cloud.storage.Storage;
import com.google.cloud.storage.StorageClass;
import com.google.cloud.storage.StorageOptions;
import io.airbyte.integrations.destination.bigquery.BigQueryConsts;
import io.airbyte.integrations.destination.bigquery.BigQueryUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class BigQueryBucketManager {

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryBucketManager.class);

  public static Bucket createBucketWithStorageClassAndLocation(JsonNode config) {

    LOGGER.info("Trying to create new bucket...");

    JsonNode gcsAvroJsonNodeConfig = BigQueryUtils.getGcsAvroJsonNodeConfig(config);

    final String projectId = config.get(BigQueryConsts.CONFIG_PROJECT_ID).asText();
    final String bucketName = gcsAvroJsonNodeConfig.get(BigQueryConsts.GCS_BUCKET_NAME).asText();
    String dataSetLocation = BigQueryUtils.getDatasetLocation(config);

    AccessToken accessToken = new AccessToken(config.get(CREDENTIALS).get("access_token").asText(), null);
    String refreshToken = config.get(CREDENTIALS).get("refresh_token").asText();

    GoogleCredentials credential =
        UserCredentials.newBuilder()
            .setClientId(config.get(CREDENTIALS).get("client_id").asText())
            .setClientSecret(config.get(CREDENTIALS).get("client_secret").asText())
            .setAccessToken(accessToken)
            .setRefreshToken(refreshToken)
            .build();

    Storage storage = StorageOptions.newBuilder()
        .setCredentials(credential)
        .setProjectId(projectId)
        .build()
        .getService();
    // See the StorageClass documentation for other valid storage classes:
    // https://googleapis.dev/java/google-cloud-clients/latest/com/google/cloud/storage/StorageClass.html
    StorageClass storageClass = StorageClass.COLDLINE;

    // See this documentation for other valid locations:
    // http://g.co/cloud/storage/docs/bucket-locations#location-mr

    Bucket bucket =
        storage.create(
            BucketInfo.newBuilder(bucketName)
                .setStorageClass(storageClass)
                .setLocation(dataSetLocation)
                .build());

    LOGGER.info("Created bucket {} in {}  with storage class {} ", bucket.getName(), bucket.getLocation(), bucket.getStorageClass());
    return bucket;
  }
}
