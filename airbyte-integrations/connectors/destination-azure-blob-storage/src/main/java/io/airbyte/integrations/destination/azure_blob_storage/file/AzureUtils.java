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
    } else {
      LOGGER.info("Selected loading method is set to: " + UploadingMethod.STANDARD);
      return UploadingMethod.STANDARD;
    }
  }

  public static JsonNode getStagingJsonConfig(final UploadingMethod uploadingMethod,
                                              final UploaderType uploaderType,
                                              final JsonNode config) {
    JsonNode stagingConfig = null;
    if (UploadingMethod.GCS.equals(uploadingMethod) && UploaderType.CSV.equals(uploaderType)) {
      stagingConfig = getGcsCsvJsonNodeConfig(config);
    }
    if (UploadingMethod.GCS.equals(uploadingMethod) && UploaderType.JSONL.equals(uploaderType)) {
      stagingConfig = getGcsJsonJsonNodeConfig(config);
    }
    return stagingConfig;
  }

  public static JsonNode getGcsCsvJsonNodeConfig(final JsonNode config) {
    final JsonNode loadingMethod = config.get(AzureConsts.LOADING_METHOD);
    final JsonNode gcsJsonNode = Jsons.jsonNode(ImmutableMap.builder()
            .put(AzureConsts.GCS_BUCKET_NAME, loadingMethod.get(AzureConsts.GCS_BUCKET_NAME))
            .put(AzureConsts.GCS_BUCKET_PATH, loadingMethod.get(AzureConsts.GCS_BUCKET_PATH))
            .put(AzureConsts.GCS_BUCKET_REGION, loadingMethod.get(AzureConsts.GCS_BUCKET_REGION))
            .put(AzureConsts.CREDENTIAL, loadingMethod.get(AzureConsts.CREDENTIAL))
            .put(AzureConsts.FORMAT, Jsons.deserialize("{\n"
                    + "  \"format_type\": \"CSV\",\n"
                    + "  \"flattening\": \"No flattening\"\n"
                    + "}"))
            .build());

    LOGGER.debug("Composed GCS config is: \n" + gcsJsonNode.toPrettyString());
    return gcsJsonNode;
  }

  public static JsonNode getGcsJsonJsonNodeConfig(final JsonNode config) {
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

}
