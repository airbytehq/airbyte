package io.airbyte.integrations.destination.gcs.credential;

import com.fasterxml.jackson.databind.JsonNode;

public class GcsHmacKeyCredentialConfig implements GcsCredentialConfig {

  private final String hmacKeyAccessId;
  private final String hmacKeySecret;

  public GcsHmacKeyCredentialConfig(JsonNode credentialConfig) {
    this.hmacKeyAccessId = credentialConfig.get("hmac_key_access_id").asText();
    this.hmacKeySecret = credentialConfig.get("hmac_key_secret").asText();
  }

  public String getHmacKeyAccessId() {
    return hmacKeyAccessId;
  }

  public String getHmacKeySecret() {
    return hmacKeySecret;
  }

  @Override
  public GcsCredential getCredentialType() {
    return GcsCredential.HMAC;
  }

}
