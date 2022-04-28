package io.airbyte.integrations.destination.bigquery.factory;

import static com.google.common.base.Charsets.UTF_8;
import static io.airbyte.integrations.destination.bigquery.BigQueryConsts.CREDENTIALS;
import static io.airbyte.integrations.destination.bigquery.BigQueryConsts.OAuthConsts.ACCESS_TOKEN;
import static io.airbyte.integrations.destination.bigquery.BigQueryConsts.OAuthConsts.CLIENT_ID;
import static io.airbyte.integrations.destination.bigquery.BigQueryConsts.OAuthConsts.CLIENT_SECRET;
import static io.airbyte.integrations.destination.bigquery.BigQueryConsts.OAuthConsts.REFRESH_TOKEN;
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
import java.util.Objects;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Factory to create Google Credentials
 */
public class BigQueryCredentialsFactory {

  private static final String AUTH_TYPE = "auth_type";
  private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryCredentialsFactory.class);

  private BigQueryCredentialsFactory() {}

  public static BigQuery createBigQueryClientWithCredentials(JsonNode config) throws IOException {
    LOGGER.info("Creating BigQuery client with Google credentials...");
    final String projectId = config.get(BigQueryConsts.CONFIG_PROJECT_ID).asText();
    Credentials credentials = createCredentialsClient(config);
    return BigQueryOptions.newBuilder()
        .setProjectId(projectId)
        .setCredentials(!isNull(credentials) ? credentials : GoogleCredentials.getApplicationDefault())
        .build()
        .getService();
  }

  public static Credentials createCredentialsClient(JsonNode config) {
    LOGGER.info("Determining Google credentials type from the config...");
    return isOauth(config) ? getOAuthClientCredentials(config) : getServiceAccountCredentials(config);
  }

  protected static Credentials getOAuthClientCredentials(JsonNode config) {
    LOGGER.info("Creating OAuth client credentials...");
    AccessToken accessToken = new AccessToken(config.get(CREDENTIALS).get(ACCESS_TOKEN).asText(), calculateTokenExpirationDate(config));
    String refreshToken = config.get(CREDENTIALS).get(REFRESH_TOKEN).asText();
    GoogleCredentials credentials =
        UserCredentials.newBuilder()
            .setClientId(config.get(CREDENTIALS).get(CLIENT_ID).asText())
            .setClientSecret(config.get(CREDENTIALS).get(CLIENT_SECRET).asText())
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

  protected static Credentials getServiceAccountCredentials(JsonNode config) {
    LOGGER.info("Creating Service Account credentials...");
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
        LOGGER.error("Error appears, when creating the Service Account credentials...", e);
        throw new RuntimeException(e);
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
    if (Objects.isNull(config)) {
      throw new IllegalArgumentException("Config cannot be null");
    }
    return config.has(CREDENTIALS)
        && config.get(CREDENTIALS).has(AUTH_TYPE)
        && "oauth2.0".contains(config.get(CREDENTIALS).get(AUTH_TYPE).asText());
  }
}
