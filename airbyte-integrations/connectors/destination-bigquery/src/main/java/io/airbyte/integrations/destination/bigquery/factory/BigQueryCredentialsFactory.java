package io.airbyte.integrations.destination.bigquery.factory;

import static com.google.common.base.Charsets.UTF_8;
import static io.airbyte.integrations.destination.bigquery.BigQueryConsts.CREDENTIALS;
import static java.util.Objects.isNull;
import static java.util.concurrent.TimeUnit.SECONDS;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.auth.Credentials;
import com.google.auth.oauth2.AccessToken;
import com.google.auth.oauth2.GoogleCredentials;
import com.google.auth.oauth2.ServiceAccountCredentials;
import com.google.auth.oauth2.UserCredentials;
import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.BigQueryOptions;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.bigquery.BigQueryConsts;
import io.airbyte.integrations.destination.bigquery.BigQueryUtils;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.util.Date;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class BigQueryCredentialsFactory {

  private static final String AUTH_TYPE = "auth_type";
  private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryCredentialsFactory.class);


  private BigQueryCredentialsFactory() {
  }

  public static Credentials createCredentialsClient(JsonNode config) {
    return isOauth(config) ? getOAuthClientCredentials(config) : getServiceAccountCredentials(config);
  }

  public static BigQuery createBigQueryClientWithCredentials(JsonNode config) throws IOException {
    final String projectId = config.get(BigQueryConsts.CONFIG_PROJECT_ID).asText();
    Credentials credentials = isOauth(config) ? getOAuthClientCredentials(config) : getServiceAccountCredentials(config);
    return BigQueryOptions.newBuilder()
        .setProjectId(projectId)
        .setCredentials(!isNull(credentials) ? credentials : GoogleCredentials.getApplicationDefault())
        .build()
        .getService();
  }

  private static Credentials getOAuthClientCredentials(JsonNode config) {
    AccessToken accessToken = new AccessToken(config.get(CREDENTIALS).get("access_token").asText(), calculateTokenExpirationDate(config));
    String refreshToken = config.get(CREDENTIALS).get("refresh_token").asText();
    GoogleCredentials credentials =
        UserCredentials.newBuilder()
            .setClientId(config.get(CREDENTIALS).get("client_id").asText())
            .setClientSecret(config.get(CREDENTIALS).get("client_secret").asText())
            .setAccessToken(accessToken)
            .setRefreshToken(refreshToken)
            .build();
    try {
      credentials.refreshAccessToken();
    } catch (IOException e) {
      LOGGER.error("Error appears when refresh the token...", e);
      throw new RuntimeException(e);
    }
    return credentials;
  }

  private static Credentials getServiceAccountCredentials(JsonNode config) {
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
        e.printStackTrace();
      }
    }
    return credentials;
  }

  // GCP sends "expires_in" in seconds, we convert it to milliseconds and sum current time with it.
  private static Date calculateTokenExpirationDate(JsonNode config) {
    return new Date(System.currentTimeMillis() +
        SECONDS.toMillis(config.get(CREDENTIALS).get("expires_in").asLong()));
  }

  public static boolean isOauth(JsonNode config) {
    return config.has(CREDENTIALS)
        && config.get(CREDENTIALS).has(AUTH_TYPE)
        && "oauth2.0".contains(config.get(CREDENTIALS).get(AUTH_TYPE).asText());
  }
}
