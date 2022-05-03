package io.airbyte.integrations.destination.bigquery.factory;

import static io.airbyte.integrations.destination.bigquery.BigQueryConsts.CREDENTIALS;
import static io.airbyte.integrations.destination.bigquery.factory.GoogleCredentialType.OAUTH2;
import static io.airbyte.integrations.destination.bigquery.factory.GoogleCredentialType.SERVICE_ACCOUNT;

import com.fasterxml.jackson.databind.JsonNode;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.function.Function;

/**
 * Factory to create Google Credentials
 */
public class BigQueryCredentialsFactory {

  private static final String AUTH_TYPE = "auth_type";

  private BigQueryCredentialsFactory() {
  }

  private static Map<GoogleCredentialType, Object> GOOGLE_INITIALIZED_CREDENTIALS_MAP = new ConcurrentHashMap<>();

  public static <T> T createCredentialsClient(JsonNode config) {
    GoogleCredentialType googleCredentialType = determineAuthMethod(config).apply(config);
    return (T) GOOGLE_INITIALIZED_CREDENTIALS_MAP
        .computeIfAbsent(googleCredentialType,
            value -> googleCredentialType.getCredentialFunction().apply(config));
  }

  public static <T> T createCredentialsClient(JsonNode config, GoogleCredentialType googleCredentialType) {
    return (T) GOOGLE_INITIALIZED_CREDENTIALS_MAP
        .computeIfAbsent(googleCredentialType,
            value -> googleCredentialType.getCredentialFunction().apply(config));
  }

  private static Function<JsonNode, GoogleCredentialType> determineAuthMethod(JsonNode config) {
    return innerConfig -> {
      if (isOAuth2(config)) {
        return OAUTH2;
      }
      return SERVICE_ACCOUNT;
    };
  }

  private static boolean isOAuth2(JsonNode config) {
    return config.has(CREDENTIALS)
        && config.get(CREDENTIALS).has(AUTH_TYPE)
        && "oauth2.0".contains(config.get(CREDENTIALS).get(AUTH_TYPE).asText());
  }
}
