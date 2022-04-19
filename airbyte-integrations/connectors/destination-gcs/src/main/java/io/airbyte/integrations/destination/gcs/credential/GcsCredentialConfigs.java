/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs.credential;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.auth.oauth2.AccessToken;
import com.google.auth.oauth2.GoogleCredentials;
import com.google.auth.oauth2.UserCredentials;
import io.airbyte.commons.json.Jsons;
import java.io.IOException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class GcsCredentialConfigs {

  private static final Logger LOGGER = LoggerFactory.getLogger(GcsCredentialConfigs.class);

  private static final String CREDENTIALS = "credentials";

  public static GcsCredentialConfig getCredentialConfig(final JsonNode config) {
    final JsonNode credentialConfig = config.get("credential");
    final GcsCredentialType credentialType = GcsCredentialType.valueOf(credentialConfig.get("credential_type").asText().toUpperCase());
    switch (credentialType) {
      case HMAC_KEY -> {
        return new GcsHmacKeyCredentialConfig(credentialConfig);
      }
      case OAUTH2 -> {
        return new GCPSessionCredentials(getOAuthClientCredentials(config));
      }
      default -> throw new RuntimeException("Unexpected credential: " + Jsons.serialize(credentialConfig));
    }
  }

  private static GoogleCredentials getOAuthClientCredentials(JsonNode config) {
    AccessToken accessToken = new AccessToken(config.get(CREDENTIALS).get("access_token").asText(), null);
    String refreshToken = config.get(CREDENTIALS).get("refresh_token").asText();
    GoogleCredentials credentials =
        UserCredentials.newBuilder()
            .setClientId(config.get(CREDENTIALS).get("client_id").asText())
            .setClientSecret(config.get(CREDENTIALS).get("client_secret").asText())
            .setAccessToken(accessToken)
            .setRefreshToken(refreshToken)
            .build();
    try {
      credentials.refreshIfExpired();
    } catch (IOException e) {
      LOGGER.error("Error appears when refresh the token...", e);
      throw new RuntimeException(e);
    }
    return credentials;
  }

}
