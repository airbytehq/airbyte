/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.Map;

public class S3DestinationTestUtils {

  private static final String ACCESS_KEY_CONFIG_SECRET_PATH = "secrets/s3_dest_min_required_permissions_creds.json";
  private static final String ASSUME_ROLE_CONFIG_SECRET_PATH = "secrets/s3_dest_assume_role_config.json";
  private static final String ASSUME_ROLE_INTERNAL_CREDENTIALS_SECRET_PATH = "secrets/s3_dest_iam_role_credentials_for_assume_role_auth.json";

  private static final String POLICY_MANAGER_CREDENTIALS_SECRET_PATH = "secrets/s3_dest_policy_manager_credentials.json";

  public static JsonNode getBaseConfigJsonFilePath() {
    return Jsons.deserialize(IOs.readFile(Path.of(ACCESS_KEY_CONFIG_SECRET_PATH)));
  }

  public static JsonNode getAssumeRoleConfig() {
    return Jsons.deserialize(IOs.readFile(Path.of(ASSUME_ROLE_CONFIG_SECRET_PATH)));
  }

  private static Map<String, String> getCredentials(String secretPath) {
    var retVal = new HashMap<String, String>();
    for (Map.Entry<String, JsonNode> e : Jsons.deserialize(IOs.readFile(Path.of(secretPath))).properties()) {
      retVal.put(e.getKey(), e.getValue().textValue());
    }
    return retVal;
  }

  public static Map<String, String> getAssumeRoleInternalCredentials() {
    return getCredentials(ASSUME_ROLE_INTERNAL_CREDENTIALS_SECRET_PATH);
  }

  public static Map<String, String> getPolicyManagerCredentials() {
    return getCredentials(POLICY_MANAGER_CREDENTIALS_SECRET_PATH);
  }

}
