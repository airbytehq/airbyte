package io.airbyte.integrations.destination.bigquery.factory;

import static io.airbyte.integrations.destination.bigquery.BigQueryConsts.CONFIG_PROJECT_ID;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;

public class BigQueryCredentialsFactoryTest {

  private static final String AUTH_TYPE = "auth_type";
  private static final String ACCESS_TOKEN = "access_token";
  private static final String REFRESH_TOKEN = "refresh_token";
  private static final String CLIENT_ID = "client_id";
  private static final String CLIENT_SECRET = "client_secret";
  private static final String CREDENTIALS = "credentials";
  private static final String EXPIRES_IN = "expires_in";

  @Mock
  private JsonNode config;

  @Mock
  private JsonNode credentials;

  @Mock
  private JsonNode authType;

  @Mock
  private JsonNode accessToken;

  @Mock
  private JsonNode refreshToken;

  @Mock
  private JsonNode clientId;

  @Mock
  private JsonNode clientSecret;

  @Mock
  private JsonNode expiresIn;

  @BeforeEach
  public void setUp() {
    MockitoAnnotations.openMocks(this);
    when(config.get(CREDENTIALS)).thenReturn(credentials);
    when(credentials.get(AUTH_TYPE)).thenReturn(authType);
    when(credentials.get(ACCESS_TOKEN)).thenReturn(accessToken);
    when(credentials.get(REFRESH_TOKEN)).thenReturn(refreshToken);
    when(credentials.get(CLIENT_ID)).thenReturn(clientId);
    when(credentials.get(CLIENT_SECRET)).thenReturn(clientSecret);
    when(credentials.get(EXPIRES_IN)).thenReturn(expiresIn);
    when(config.has(CREDENTIALS)).thenReturn(true);
    when(config.get(CREDENTIALS).has(AUTH_TYPE)).thenReturn(true);
    when(authType.asText()).thenReturn("oauth2.0");
    when(accessToken.asText()).thenReturn("accessToken");
    when(refreshToken.asText()).thenReturn("refreshToken");
    when(clientId.asText()).thenReturn("clientId");
    when(clientSecret.asText()).thenReturn("clientSecret");
    when(expiresIn.asLong()).thenReturn((long) 3600);
    when(config.get(CREDENTIALS).get(AUTH_TYPE).asText()).thenReturn("oauth2.0");
    when(config.get(CONFIG_PROJECT_ID)).thenReturn(config);
    when(config.get(CONFIG_PROJECT_ID).asText()).thenReturn("projectId");
  }

  @Test
  public void testIsOauth() {
    assertTrue(BigQueryCredentialsFactory.isOauth(config));
  }

  @Test
  public void testIsNotOauth() {
    when(config.get(CREDENTIALS).get(AUTH_TYPE).asText()).thenReturn("Service account");
    assertFalse(BigQueryCredentialsFactory.isOauth(config));
  }

  @Test
  public void testIsNotOauthWhenCredentialsAreNotPresent() {
    when(config.has(CREDENTIALS)).thenReturn(false);
    assertFalse(BigQueryCredentialsFactory.isOauth(config));
  }

  @Test
  public void testIsNotOauthWhenCredentialsAreNotObject() {
    when(config.get(CREDENTIALS).isObject()).thenReturn(false);
    assertFalse(BigQueryCredentialsFactory.isOauth(config));
  }

  @Test
  public void testIsNotOauthWhenConfigIsNull() {
    assertThrows(IllegalArgumentException.class, () -> {
      BigQueryCredentialsFactory.isOauth(null);
    });
  }
}