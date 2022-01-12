/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_blob_storage.file;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class AzureUtils {

  private static final Logger LOGGER = LoggerFactory.getLogger(AzureUtils.class);

  public static UploadingMethod getLoadingMethod(final JsonNode config) {
    final JsonNode loadingMethod = config.get(AzureConsts.LOADING_METHOD);
    if (loadingMethod != null && AzureConsts.GCS_STAGING.equals(loadingMethod.get(AzureConsts.METHOD).asText())) {
      LOGGER.info("Selected loading method is set to: " + UploadingMethod.GCS);
      return UploadingMethod.GCS;
    }
    if (loadingMethod != null && AzureConsts.S3_STAGING.equals(loadingMethod.get(AzureConsts.METHOD).asText())) {
      LOGGER.info("Selected loading method is set to: " + UploadingMethod.S3);
      return UploadingMethod.S3;
    } else {
      LOGGER.info("Selected loading method is set to: " + UploadingMethod.STANDARD);
      return UploadingMethod.STANDARD;
    }
  }

  public static JsonNode getStagingJsonConfig(final UploadingMethod uploadingMethod,
                                              final UploaderType uploaderType,
                                              final JsonNode config) {
    JsonNode stagingConfig = null;
    if (UploadingMethod.GCS.equals(uploadingMethod)) {
      if (UploaderType.CSV.equals(uploaderType)){
        stagingConfig = getGcsCsvJsonNodeConfig(config);
      }
      if (UploaderType.JSONL.equals(uploaderType)) {
        stagingConfig = getGcsJsonJsonNodeConfig(config);
      }
    }
    if (UploadingMethod.S3.equals(uploadingMethod)) {
      if (UploaderType.CSV.equals(uploaderType)){
        stagingConfig = getS3CsvJsonNodeConfig(config);
      }
      if (UploaderType.JSONL.equals(uploaderType)) {
        stagingConfig = getS3JsonJsonNodeConfig(config);
      }
    }
    return stagingConfig;
  }

  public static UploaderType getUploaderType(final JsonNode config) {
    final JsonNode format = config.get(AzureConsts.FORMAT);
    if (format != null && AzureConsts.FORMAT_CSV.equals(format.get(AzureConsts.FORMAT_TYPE).asText())) {
      LOGGER.info("Selected upload file type is: " + UploaderType.CSV);
      return UploaderType.CSV;
    } else {
      LOGGER.info("Selected upload file type is: " + UploaderType.JSONL);
      return UploaderType.JSONL;
    }
  }

  public static boolean isKeepFilesInStorage(final JsonNode config) {
    final JsonNode loadingMethod = config.get(AzureConsts.LOADING_METHOD);
    if (AzureConsts.GCS_STAGING.equals(loadingMethod.get(AzureConsts.METHOD).asText())) {
      return isKeepFilesInGcsStorage(loadingMethod);
    }
    if (AzureConsts.S3_STAGING.equals(loadingMethod.get(AzureConsts.METHOD).asText())) {
      return isKeepFilesInS3Storage(loadingMethod);
    } else {
      return false;
    }
  }

  private static boolean isKeepFilesInGcsStorage(final JsonNode loadingMethod) {
    if (loadingMethod != null && loadingMethod.get(AzureConsts.KEEP_GCS_FILES) != null
            && AzureConsts.KEEP_GCS_FILES_VAL
            .equals(loadingMethod.get(AzureConsts.KEEP_GCS_FILES).asText())) {
      LOGGER.info("All tmp files GCS will be kept in bucket when replication is finished");
      return true;
    } else {
      LOGGER.info("All tmp files will be removed from GCS when replication is finished");
      return false;
    }
  }

  private static boolean isKeepFilesInS3Storage(final JsonNode loadingMethod) {
    if (loadingMethod != null && loadingMethod.get(AzureConsts.KEEP_S3_FILES) != null
            && AzureConsts.KEEP_S3_FILES_VAL
            .equals(loadingMethod.get(AzureConsts.KEEP_S3_FILES).asText())) {
      LOGGER.info("All tmp files S3 will be kept in bucket when replication is finished");
      return true;
    } else {
      LOGGER.info("All tmp files will be removed from S3 when replication is finished");
      return false;
    }
  }

  private static JsonNode getGcsCsvJsonNodeConfig(final JsonNode config) {
    final JsonNode loadingMethod = config.get(AzureConsts.LOADING_METHOD);
    final String flattening = config.get(AzureConsts.FORMAT).get(AzureConsts.FORMAT_FLATTENING).asText();
    final JsonNode gcsJsonNode = Jsons.jsonNode(ImmutableMap.builder()
            .put(AzureConsts.GCS_BUCKET_NAME, loadingMethod.get(AzureConsts.GCS_BUCKET_NAME))
            .put(AzureConsts.GCS_BUCKET_PATH, loadingMethod.get(AzureConsts.GCS_BUCKET_PATH))
            .put(AzureConsts.GCS_BUCKET_REGION, loadingMethod.get(AzureConsts.GCS_BUCKET_REGION))
            .put(AzureConsts.CREDENTIAL, loadingMethod.get(AzureConsts.CREDENTIAL))
            .put(AzureConsts.FORMAT, Jsons.deserialize("{\n"
                    + "  \"format_type\": \"CSV\",\n"
                    + "  \"flattening\": \"" + flattening + "\"\n"
                    + "}"))
            .build());

    LOGGER.debug("Composed GCS config is: \n" + gcsJsonNode.toPrettyString());
    return gcsJsonNode;
  }

  private static JsonNode getGcsJsonJsonNodeConfig(final JsonNode config) {
    final JsonNode loadingMethod = config.get(AzureConsts.LOADING_METHOD);
    final JsonNode gcsJsonNode = Jsons.jsonNode(ImmutableMap.builder()
            .put(AzureConsts.GCS_BUCKET_NAME, loadingMethod.get(AzureConsts.GCS_BUCKET_NAME))
            .put(AzureConsts.GCS_BUCKET_PATH, loadingMethod.get(AzureConsts.GCS_BUCKET_PATH))
            .put(AzureConsts.GCS_BUCKET_REGION, loadingMethod.get(AzureConsts.GCS_BUCKET_REGION))
            .put(AzureConsts.CREDENTIAL, loadingMethod.get(AzureConsts.CREDENTIAL))
            .put(AzureConsts.FORMAT, Jsons.deserialize("{\n"
                    + "  \"format_type\": \"JSONL\",\n"
                    + "  \"flattening\": \"No flattening\"\n"
                    + "}"))
            .build());

    LOGGER.debug("Composed GCS config is: \n" + gcsJsonNode.toPrettyString());
    return gcsJsonNode;
  }

  private static JsonNode getS3CsvJsonNodeConfig(final JsonNode config) {
    final JsonNode loadingMethod = config.get(AzureConsts.LOADING_METHOD);
    final String flattening = config.get(AzureConsts.FORMAT).get(AzureConsts.FORMAT_FLATTENING).asText();
    final JsonNode s3JsonNode = Jsons.jsonNode(ImmutableMap.builder()
            .put(AzureConsts.S3_ENDPOINT,
                    loadingMethod.has(AzureConsts.S3_ENDPOINT) ? loadingMethod.get(AzureConsts.S3_ENDPOINT) : "")
            .put(AzureConsts.S3_BUCKET_NAME, loadingMethod.get(AzureConsts.S3_BUCKET_NAME))
            .put(AzureConsts.S3_BUCKET_PATH, loadingMethod.get(AzureConsts.S3_BUCKET_PATH))
            .put(AzureConsts.S3_BUCKET_REGION, loadingMethod.get(AzureConsts.S3_BUCKET_REGION))
            .put(AzureConsts.S3_ACCESS_KEY_ID, loadingMethod.get(AzureConsts.CREDENTIAL).get(AzureConsts.S3_ACCESS_KEY_ID))
            .put(AzureConsts.S3_SECRET_ACCESS_KEY, loadingMethod.get(AzureConsts.CREDENTIAL).get(AzureConsts.S3_SECRET_ACCESS_KEY))
            .put(AzureConsts.FORMAT, Jsons.deserialize("{\n"
                    + "  \"format_type\": \"CSV\",\n"
                    + "  \"flattening\": \"" + flattening + "\"\n"
                    + "}"))
            .build());

    LOGGER.debug("Composed S3 config is: \n" + s3JsonNode.toPrettyString());
    return s3JsonNode;
  }

  private static JsonNode getS3JsonJsonNodeConfig(final JsonNode config) {
    final JsonNode loadingMethod = config.get(AzureConsts.LOADING_METHOD);
    final JsonNode s3JsonNode = Jsons.jsonNode(ImmutableMap.builder()
            .put(AzureConsts.S3_ENDPOINT,
                    loadingMethod.has(AzureConsts.S3_ENDPOINT) ? loadingMethod.get(AzureConsts.S3_ENDPOINT) : "")
            .put(AzureConsts.S3_BUCKET_NAME, loadingMethod.get(AzureConsts.S3_BUCKET_NAME))
            .put(AzureConsts.S3_BUCKET_PATH, loadingMethod.get(AzureConsts.S3_BUCKET_PATH))
            .put(AzureConsts.S3_BUCKET_REGION, loadingMethod.get(AzureConsts.S3_BUCKET_REGION))
            .put(AzureConsts.S3_ACCESS_KEY_ID, loadingMethod.get(AzureConsts.CREDENTIAL).get(AzureConsts.S3_ACCESS_KEY_ID))
            .put(AzureConsts.S3_SECRET_ACCESS_KEY, loadingMethod.get(AzureConsts.CREDENTIAL).get(AzureConsts.S3_SECRET_ACCESS_KEY))
            .put(AzureConsts.FORMAT, Jsons.deserialize("{\n"
                    + "  \"format_type\": \"JSONL\",\n"
                    + "  \"flattening\": \"No flattening\"\n"
                    + "}"))
            .build());

    LOGGER.debug("Composed S3 config is: \n" + s3JsonNode.toPrettyString());
    return s3JsonNode;
  }

}
