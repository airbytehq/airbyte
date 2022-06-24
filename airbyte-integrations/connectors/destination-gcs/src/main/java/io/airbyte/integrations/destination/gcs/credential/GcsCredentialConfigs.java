/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs.credential;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;

public class GcsCredentialConfigs {

  public static GcsCredentialConfig getCredentialConfig(final JsonNode config) {
    final JsonNode credentialConfig = config.get("credential");
    final GcsCredentialType credentialType = GcsCredentialType.valueOf(credentialConfig.get("credential_type").asText().toUpperCase());

    if (credentialType == GcsCredentialType.HMAC_KEY) {
      return new GcsHmacKeyCredentialConfig(credentialConfig);
    }
    throw new RuntimeException("Unexpected credential: " + Jsons.serialize(credentialConfig));
  }

}
