package io.airbyte.integrations.destination.redshift.validator;

import com.fasterxml.jackson.databind.JsonNode;

/**
 * Validator for Destination Redshift Schema
 */
public class RedshiftValidatorUtil {

  private RedshiftValidatorUtil() {
  }

  public static boolean validateIfAllRequiredS3fieldsArePresent(final JsonNode uploadMode) {
    return isNullOrEmpty(uploadMode.get("s3_bucket_name"))
        && isNullOrEmpty(uploadMode.get("s3_bucket_region"))
        && isNullOrEmpty(uploadMode.get("access_key_id"))
        && isNullOrEmpty(uploadMode.get("secret_access_key"));
  }

  private static boolean isNullOrEmpty(final JsonNode jsonNode) {
    return null == jsonNode || "".equals(jsonNode.asText());
  }
}
