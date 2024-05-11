/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.util;

import static io.airbyte.integrations.destination.redshift.constants.RedshiftDestinationConstants.UPLOADING_METHOD;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import lombok.extern.log4j.Log4j2;

/**
 * Helper class for Destination Redshift connector.
 */
@Log4j2
public class RedshiftUtil {

  private RedshiftUtil() {}

  /**
   * We check whether config located in root of node. (This check is done for Backward compatibility)
   *
   * @param config Configuration parameters
   * @return JSON representation of the configuration
   */
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

  public static void checkSvvTableAccess(final JdbcDatabase database) throws Exception {
    log.info("checking SVV_TABLE_INFO permissions");
    database.queryJsons("SELECT 1 FROM SVV_TABLE_INFO LIMIT 1;");
  }

}
