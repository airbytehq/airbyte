package io.airbyte.integrations.destination.bigquery;

import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.model.DeleteObjectsRequest.KeyVersion;
import com.amazonaws.services.s3.model.S3ObjectSummary;
import com.fasterxml.jackson.databind.JsonNode;
import com.google.auth.oauth2.ServiceAccountCredentials;
import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.BigQueryOptions;
import com.google.cloud.bigquery.Dataset;
import com.google.cloud.bigquery.DatasetInfo;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.ImmutableMap.Builder;
import io.airbyte.commons.json.Jsons;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.LinkedList;
import java.util.List;
import org.slf4j.Logger;

public class BigQueryDestinationTestUtils {

  public static JsonNode createConfig(Path configFile, String datasetId) throws IOException {
    final String tmpConfigAsString = Files.readString(configFile);
    final JsonNode tmpConfigJson = Jsons.deserialize(tmpConfigAsString);
    final JsonNode tmpCredentialsJson = tmpConfigJson.get(BigQueryConsts.BIGQUERY_BASIC_CONFIG);
    Builder<Object, Object> mapBuilder = ImmutableMap.builder();
    mapBuilder.put(BigQueryConsts.CONFIG_PROJECT_ID, tmpCredentialsJson.get(BigQueryConsts.CONFIG_PROJECT_ID).asText());
    mapBuilder.put(BigQueryConsts.CONFIG_CREDS, tmpCredentialsJson.toString());
    mapBuilder.put(BigQueryConsts.CONFIG_DATASET_ID, datasetId);
    mapBuilder.put(BigQueryConsts.CONFIG_DATASET_LOCATION, tmpConfigJson.get(BigQueryConsts.CONFIG_DATASET_LOCATION).asText());
    if(tmpConfigJson.has(BigQueryConsts.CONFIG_IMPERSONATE_ACCOUNT)) {
      mapBuilder.put(BigQueryConsts.CONFIG_IMPERSONATE_ACCOUNT, tmpConfigJson.get(BigQueryConsts.CONFIG_IMPERSONATE_ACCOUNT).asText());
    }

    //if current test config includes GCS staging - add the staging configuration to the returned config object
    if(tmpConfigJson.has(BigQueryConsts.LOADING_METHOD)) {
      final JsonNode loadingMethodJson = tmpConfigJson.get(BigQueryConsts.LOADING_METHOD);
      mapBuilder.put(BigQueryConsts.LOADING_METHOD, loadingMethodJson);
    }

    return Jsons.jsonNode(mapBuilder.build());
  }

  public static Dataset initDataSet(JsonNode config, BigQuery bigquery, String datasetId) {
    final DatasetInfo datasetInfo = DatasetInfo.newBuilder(datasetId)
        .setLocation(config.get(BigQueryConsts.CONFIG_DATASET_LOCATION).asText()).build();
    try {
      return bigquery.create(datasetInfo);
    } catch(Exception ex) {
      if(ex.getMessage().indexOf("Already Exists") > -1) {
        return bigquery.getDataset(datasetId);
      }
    }
    return null;
  }

  public static BigQuery initBigQuery(JsonNode config, String projectId) throws IOException {
    final ServiceAccountCredentials credentials = ServiceAccountCredentials
        .fromStream(new ByteArrayInputStream(config.get(BigQueryConsts.CONFIG_CREDS).asText().getBytes(StandardCharsets.UTF_8)));
    return BigQueryOptions.newBuilder()
        .setProjectId(projectId)
        .setCredentials(credentials)
        .build()
        .getService();
  }

  public static boolean tearDownBigQuery(BigQuery bigquery, Dataset dataset, Logger LOGGER) {
    // allows deletion of a dataset that has contents
    final BigQuery.DatasetDeleteOption option = BigQuery.DatasetDeleteOption.deleteContents();
    if(bigquery == null || dataset == null) {
      return false;
    }
    try {
      final boolean success = bigquery.delete(dataset.getDatasetId(), option);
      if (success) {
        LOGGER.info("BQ Dataset " + dataset + " deleted...");
        return true;
      } else {
        LOGGER.info("BQ Dataset cleanup for " + dataset + " failed!");
        return false;
      }
    } catch (Exception ex) {
      return false;
    }
  }

  /**
   * Remove all the GCS output from the tests.
   */
  public static boolean tearDownGcs(AmazonS3 s3Client, JsonNode config, Logger LOGGER) {
    if(s3Client == null) {
      return false;
    }

    final JsonNode properties = config.get(BigQueryConsts.LOADING_METHOD);
    final String gcsBucketName = properties.get(BigQueryConsts.GCS_BUCKET_NAME).asText();
    final String gcs_bucket_path = properties.get(BigQueryConsts.GCS_BUCKET_PATH).asText();
    try {
      final List<KeyVersion> keysToDelete = new LinkedList<>();
      final List<S3ObjectSummary> objects = s3Client
          .listObjects(gcsBucketName, gcs_bucket_path)
          .getObjectSummaries();
      for (final S3ObjectSummary object : objects) {
        keysToDelete.add(new KeyVersion(object.getKey()));
      }

      if (keysToDelete.size() > 0) {
        LOGGER.info("Tearing down test bucket path: {}/{}", gcsBucketName, gcs_bucket_path);
        // Google Cloud Storage doesn't accept request to delete multiple objects
        for (final KeyVersion keyToDelete : keysToDelete) {
          s3Client.deleteObject(gcsBucketName, keyToDelete.getKey());
        }
        LOGGER.info("Deleted {} file(s).", keysToDelete.size());
      }
      return true;
    } catch (Exception ex) {
      return false;
    }
  }
}
