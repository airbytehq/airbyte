/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs.credential;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.auth.Credentials;
import com.google.auth.oauth2.GoogleCredentials;
import io.airbyte.commons.json.Jsons;

public class GcsCredentialConfigs {

  private static final String CREDENTIAL = "credential";
  private static final String CREDENTIAL_TYPE = "credential_type";

  public static GcsCredentialConfig getCredentialConfig(final JsonNode config) {
    final JsonNode credentialConfig = config.get(CREDENTIAL);
    final GcsCredentialType credentialType = GcsCredentialType.valueOf(credentialConfig.get(CREDENTIAL_TYPE).asText().toUpperCase());
    switch (credentialType) {
      case HMAC_KEY -> {
        return new GcsHmacKeyCredentialConfig(credentialConfig);
      }
      default -> throw new RuntimeException("Unexpected credential: " + Jsons.serialize(credentialConfig));
    }
  }

  public static GcsCredentialConfig getCredentialConfig(final JsonNode config, final Credentials credentials) {
    final JsonNode credentialConfig = config.get(CREDENTIAL);
    final GcsCredentialType credentialType = GcsCredentialType.valueOf(credentialConfig.get(CREDENTIAL_TYPE).asText().toUpperCase());
    switch (credentialType) {
      case HMAC_KEY -> {
        return new GcsHmacKeyCredentialConfig(credentialConfig);
      }
      case OAUTH2 -> {
        return new GCPOauth2Adapter((GoogleCredentials) credentials);
      }
      default -> throw new RuntimeException("Unexpected credential: " + Jsons.serialize(credentialConfig));
    }
  }
}
