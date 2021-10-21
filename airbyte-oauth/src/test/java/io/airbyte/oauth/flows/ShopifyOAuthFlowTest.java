/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.oauth.flows;

import static java.util.Collections.emptyMap;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.DestinationOAuthParameter;
import io.airbyte.config.SourceOAuthParameter;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.net.http.HttpClient;
import java.net.http.HttpResponse;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ShopifyOAuthFlowTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(ShopifyOAuthFlowTest.class);
  private static final Path CREDENTIALS_PATH = Path.of("secrets/credentials.json");
  private static final String REDIRECT_URL = "https://airbyte.io";
  private static final String EXPECTED_REDIRECT_URL = "https%3A%2F%2Fairbyte.io";
  private static final String EXPECTED_OPTIONS =
      "grant_options%5B%5D=value&scope=read_themes%2Cread_orders%2Cread_all_orders%2Cread_assigned_fulfillment_orders%2Cread_checkouts%2Cread_content%2Cread_customers%2Cread_discounts%2Cread_draft_orders%2Cread_fulfillments%2Cread_locales%2Cread_locations%2Cread_price_rules%2Cread_products%2Cread_product_listings%2Cread_shopify_payments_payouts";

  private HttpClient httpClient;
  private ConfigRepository configRepository;
  private ShopifyOAuthFlow shopifyOAuthFlow;

  private UUID workspaceId;
  private UUID definitionId;

  @BeforeEach
  public void setup() {
    httpClient = mock(HttpClient.class);
    configRepository = mock(ConfigRepository.class);
    shopifyOAuthFlow = new ShopifyOAuthFlow(configRepository, httpClient,
        ShopifyOAuthFlowTest::getConstantState);

    workspaceId = UUID.randomUUID();
    definitionId = UUID.randomUUID();
  }

  @Test
  public void testGetSourceConsentUrl()
      throws IOException, ConfigNotFoundException, JsonValidationException {
    when(configRepository.listSourceOAuthParam()).thenReturn(List.of(new SourceOAuthParameter()
        .withOauthParameterId(UUID.randomUUID())
        .withSourceDefinitionId(definitionId)
        .withWorkspaceId(workspaceId)
        .withConfiguration(Jsons.jsonNode(Map.of("credentials", ImmutableMap.builder()
            .put("client_id", getClientId())
            .put("client_secret", "test_client_secret")
            .build())))));
    final String actualSourceUrl = shopifyOAuthFlow.getSourceConsentUrl(workspaceId, definitionId,
        REDIRECT_URL, emptyMap());
    final String expectedSourceUrl = String.format(
        "https://airbyte-integration-test.myshopify.com/admin/oauth/authorize?client_id=%s&redirect_uri=%s&state=%s&%s",
        getClientId(),
        EXPECTED_REDIRECT_URL,
        getConstantState(),
        EXPECTED_OPTIONS);
    LOGGER.info(expectedSourceUrl);
    assertEquals(expectedSourceUrl, actualSourceUrl);
  }

  @Test
  public void testCompleteDestinationOAuth()
      throws IOException, ConfigNotFoundException, JsonValidationException, InterruptedException {
    when(configRepository.listDestinationOAuthParam()).thenReturn(
        List.of(new DestinationOAuthParameter()
            .withOauthParameterId(UUID.randomUUID())
            .withDestinationDefinitionId(definitionId)
            .withWorkspaceId(workspaceId)
            .withConfiguration(Jsons.jsonNode(Map.of("credentials", ImmutableMap.builder()
                .put("client_id", "test_client_id")
                .put("client_secret", "test_client_secret")
                .build())))));

    final Map<String, String> returnedCredentials = Map.of("access_token",
        "refresh_token_response");
    final HttpResponse response = mock(HttpResponse.class);
    when(response.body()).thenReturn(Jsons.serialize(returnedCredentials));
    when(httpClient.send(any(), any())).thenReturn(response);
    final Map<String, Object> queryParams = Map.of("code", "test_code");
    final Map<String, Object> actualQueryParams = shopifyOAuthFlow.completeDestinationOAuth(
        workspaceId, definitionId, queryParams, REDIRECT_URL);

    assertEquals(Jsons.serialize(Map.of("credentials", returnedCredentials)),
        Jsons.serialize(actualQueryParams));
  }

  @Test
  public void testGetClientIdUnsafe() {
    final String clientId = "123";
    final Map<String, String> clientIdMap = Map.of("client_id", clientId);
    final Map<String, Map<String, String>> nestedConfig = Map.of("credentials", clientIdMap);

    assertThrows(IllegalArgumentException.class,
        () -> shopifyOAuthFlow.getClientIdUnsafe(Jsons.jsonNode(clientIdMap)));
    assertEquals(clientId, shopifyOAuthFlow.getClientIdUnsafe(Jsons.jsonNode(nestedConfig)));
  }

  @Test
  public void testGetClientSecretUnsafe() {
    final String clientSecret = "secret";
    final Map<String, String> clientIdMap = Map.of("client_secret", clientSecret);
    final Map<String, Map<String, String>> nestedConfig = Map.of("credentials", clientIdMap);

    assertThrows(IllegalArgumentException.class,
        () -> shopifyOAuthFlow.getClientSecretUnsafe(Jsons.jsonNode(clientIdMap)));
    assertEquals(clientSecret,
        shopifyOAuthFlow.getClientSecretUnsafe(Jsons.jsonNode(nestedConfig)));
  }

  private static String getConstantState() {
    return "state";
  }

  private String getClientId() throws IOException {
    if (!Files.exists(CREDENTIALS_PATH)) {
      return "test_client_id";
    } else {
      final String fullConfigAsString = new String(Files.readAllBytes(CREDENTIALS_PATH));
      final JsonNode credentialsJson = Jsons.deserialize(fullConfigAsString);
      return credentialsJson.get("credentials").get("client_id").asText();
    }
  }

}
