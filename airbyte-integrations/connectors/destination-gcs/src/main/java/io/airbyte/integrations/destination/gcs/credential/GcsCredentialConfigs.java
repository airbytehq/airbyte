package io.airbyte.integrations.destination.gcs.credential;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;

public class GcsCredentialConfigs {

  public static GcsCredentialConfig getCredentialConfig(JsonNode config) {
    JsonNode credentialConfig = config.get("credential");
    GcsCredential credentialType = GcsCredential.valueOf(credentialConfig.get("credential_type").asText().toUpperCase());

    if (credentialType == GcsCredential.HMAC) {
      return new GcsHmacKeyCredentialConfig(credentialConfig);
    }
    throw new RuntimeException("Unexpected credential: " + Jsons.serialize(credentialConfig));
  }

}
