/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.util;

import static io.airbyte.integrations.destination.redshift.constants.RedshiftDestinationConstants.UPLOADING_METHOD;

import com.fasterxml.jackson.databind.JsonNode;

/**
 * Helper class for Destination Redshift connector.
 */
public class RedshiftUtil {

  private RedshiftUtil() {}

  // We check whether config located in root of node. (This check is done for Backward compatibility)
  public static JsonNode findS3Options(final JsonNode config) {
    return config.has(UPLOADING_METHOD) ? config.get(UPLOADING_METHOD) : config;
  }

  public static boolean anyOfS3FieldsAreNullOrEmpty(final JsonNode jsonNode) {
    return isNullOrEmpty(jsonNode.get("s3_bucket_name"))
        && isNullOrEmpty(jsonNode.get("s3_bucket_region"))
        && isNullOrEmpty(jsonNode.get("access_key_id"))
        && isNullOrEmpty(jsonNode.get("secret_access_key"));
  }

  private static boolean isNullOrEmpty(final JsonNode jsonNode) {
    return null == jsonNode || "".equals(jsonNode.asText());
  }

}
