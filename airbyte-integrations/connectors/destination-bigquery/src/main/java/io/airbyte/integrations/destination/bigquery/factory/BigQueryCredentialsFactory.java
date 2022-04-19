package io.airbyte.integrations.destination.bigquery.factory;

import static com.google.common.base.Charsets.UTF_8;
import static io.airbyte.integrations.destination.bigquery.BigQueryConsts.CREDENTIALS;
import static java.util.Objects.isNull;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.api.services.iam.v1.model.ServiceAccount;
import com.google.api.services.iam.v1.model.ServiceAccountKey;
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
import io.airbyte.integrations.destination.bigquery.oauth.BigQueryServiceAccountKeysManager;
import io.airbyte.integrations.destination.bigquery.oauth.BigQueryServiceAccountManager;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStream;
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

  private static BigQuery createServiceAccountAndServiceKeyFromOAuth(JsonNode config) {
    final BigQueryOptions.Builder bigQueryBuilder = BigQueryOptions.newBuilder();
    final String projectId = config.get(BigQueryConsts.CONFIG_PROJECT_ID).asText();
    final String accessToken = config.get(CREDENTIALS).get("access_token").asText();
    final String expiresIn = config.get(CREDENTIALS).get("expires_in").asText();
    Date date = calculateTokenExpirationDate(expiresIn);
    ServiceAccount serviceAccount = BigQueryServiceAccountManager.createServiceAccount(projectId, "testbigquery-otsukanov", accessToken, date);
    ServiceAccountKey key = BigQueryServiceAccountKeysManager.createKey(projectId, serviceAccount.getEmail(), accessToken);
    InputStream stream = new ByteArrayInputStream(key.decodePrivateKeyData());
    try {
      GoogleCredentials credentials = GoogleCredentials.fromStream(stream);
      return bigQueryBuilder
          .setProjectId(projectId)
          .setCredentials(!isNull(credentials) ? credentials : ServiceAccountCredentials.getApplicationDefault())
          .build()
          .getService();
    } catch (final IOException e) {
      throw new RuntimeException(e);
    }
  }

  private static Date calculateTokenExpirationDate(String expiresIn) {
    Date currentTime = new Date();
    long time = currentTime.getTime();
    return new Date(time + Long.parseLong(expiresIn));
  }

  public static boolean isOauth(JsonNode config) {
    return config.has(CREDENTIALS)
        && config.get(CREDENTIALS).has(AUTH_TYPE)
        && "Client".contains(config.get(CREDENTIALS).get(AUTH_TYPE).asText());
  }
}
