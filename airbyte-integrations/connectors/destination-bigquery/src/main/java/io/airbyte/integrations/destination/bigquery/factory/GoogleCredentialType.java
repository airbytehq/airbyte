package io.airbyte.integrations.destination.bigquery.factory;

import static com.google.common.base.Charsets.UTF_8;
import static io.airbyte.integrations.destination.bigquery.BigQueryConsts.CREDENTIALS;
import static io.airbyte.integrations.destination.bigquery.BigQueryConsts.OAuthConsts.ACCESS_TOKEN;
import static io.airbyte.integrations.destination.bigquery.BigQueryConsts.OAuthConsts.CLIENT_ID;
import static io.airbyte.integrations.destination.bigquery.BigQueryConsts.OAuthConsts.CLIENT_SECRET;
import static io.airbyte.integrations.destination.bigquery.BigQueryConsts.OAuthConsts.REFRESH_TOKEN;
import static io.airbyte.integrations.destination.bigquery.factory.BigQueryCredentialsFactory.createCredentialsClient;
import static java.util.Objects.isNull;
import static java.util.concurrent.TimeUnit.SECONDS;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.auth.Credentials;
import com.google.auth.oauth2.AccessToken;
import com.google.auth.oauth2.GoogleCredentials;
import com.google.auth.oauth2.ServiceAccountCredentials;
import com.google.auth.oauth2.UserCredentials;
import com.google.cloud.bigquery.BigQueryOptions;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.bigquery.BigQueryConsts;
import io.airbyte.integrations.destination.bigquery.BigQueryUtils;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.util.Date;
import java.util.function.Function;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public enum GoogleCredentialType {
  OAUTH2(config -> {
    AccessToken accessToken = new AccessToken(config.get(CREDENTIALS).get(ACCESS_TOKEN).asText(), calculateTokenExpirationDate(config));
    GoogleCredentials credentials =
        UserCredentials.newBuilder()
            .setClientId(config.get(CREDENTIALS).get(CLIENT_ID).asText())
            .setClientSecret(config.get(CREDENTIALS).get(CLIENT_SECRET).asText())
            .setAccessToken(accessToken)
            .setRefreshToken(config.get(CREDENTIALS).get(REFRESH_TOKEN).asText())
            .build();
    try {
      credentials.refreshIfExpired();
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
    return credentials;
  }),

  SERVICE_ACCOUNT(config -> {
    ServiceAccountCredentials credentials = null;
    if (BigQueryUtils.isUsingJsonCredentials(config)) {
      // handle the credentials json being passed as a json object or a json object already serialized as
      // a string.
      final String credentialsString =
          config.get(BigQueryConsts.CONFIG_CREDS).isObject() ?
              Jsons.serialize(config.get(BigQueryConsts.CONFIG_CREDS))
              : config.get(BigQueryConsts.CONFIG_CREDS).asText();
      try {
        credentials = ServiceAccountCredentials
            .fromStream(new ByteArrayInputStream(credentialsString.getBytes(UTF_8)));
      } catch (IOException e) {
        throw new RuntimeException(e);
      }
    }
    return credentials;
  }),

  BIGQUERY_WITH_CREDENTIALS(config -> {
    Credentials credentials = createCredentialsClient(config);
    try {
      return BigQueryOptions.newBuilder()
          .setProjectId(config.get(BigQueryConsts.CONFIG_PROJECT_ID).asText())
          .setCredentials(!isNull(credentials) ? credentials : GoogleCredentials.getApplicationDefault())
          .build()
          .getService();
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  });

  private static final Logger LOGGER = LoggerFactory.getLogger(GoogleCredentialType.class);

  private final Function<JsonNode, ?> credentialFunction;

  GoogleCredentialType(Function<JsonNode, ?> credentialFunction) {
    this.credentialFunction = credentialFunction;
  }

  public Function<JsonNode, ?> getCredentialFunction() {
    LOGGER.info("Creating credentials for {}", this.name());
    return credentialFunction;
  }

  // GCP sends "expires_in" in seconds, we convert it to milliseconds and sum current time with it.
  private static Date calculateTokenExpirationDate(JsonNode config) {
    return new Date(System.currentTimeMillis() +
        SECONDS.toMillis(config.get(CREDENTIALS).get("expires_in").asLong()));
  }
}
