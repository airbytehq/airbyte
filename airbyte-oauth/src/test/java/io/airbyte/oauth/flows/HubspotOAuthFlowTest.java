/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.oauth.flows;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.SourceOAuthParameter;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.net.http.HttpClient;
import java.net.http.HttpResponse;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

public class HubspotOAuthFlowTest {

  private UUID workspaceId;
  private UUID definitionId;
  private ConfigRepository configRepository;
  private HubspotOAuthFlow flow;
  private HttpClient httpClient;

  private static final String REDIRECT_URL = "https://airbyte.io";

  private static String getConstantState() {
    return "state";
  }

  @BeforeEach
  public void setup() throws IOException, JsonValidationException {
    workspaceId = UUID.randomUUID();
    definitionId = UUID.randomUUID();
    configRepository = mock(ConfigRepository.class);
    httpClient = mock(HttpClient.class);
    when(configRepository.listSourceOAuthParam()).thenReturn(List.of(new SourceOAuthParameter()
        .withOauthParameterId(UUID.randomUUID())
        .withSourceDefinitionId(definitionId)
        .withWorkspaceId(workspaceId)
        .withConfiguration(Jsons.jsonNode(Map.of("credentials", ImmutableMap.builder()
            .put("client_id", "test_client_id")
            .put("client_secret", "test_client_secret")
            .build())))));
    flow = new HubspotOAuthFlow(configRepository, httpClient, HubspotOAuthFlowTest::getConstantState);

  }

  @Test
  public void testGetSourceConcentUrl() throws IOException, ConfigNotFoundException {
    final String concentUrl =
        flow.getSourceConsentUrl(workspaceId, definitionId, REDIRECT_URL);
    assertEquals(concentUrl,
        "https://app.hubspot.com/oauth/authorize?client_id=test_client_id&redirect_uri=https%3A%2F%2Fairbyte.io&state=state&scopes=content+crm.schemas.deals.read+crm.objects.owners.read+forms+tickets+e-commerce+crm.objects.companies.read+crm.lists.read+crm.objects.deals.read+crm.schemas.contacts.read+crm.objects.contacts.read+crm.schemas.companies.read+files+forms-uploaded-files+files.ui_hidden.read");
  }

  @Test
  public void testCompleteSourceOAuth() throws IOException, InterruptedException, ConfigNotFoundException {
    final var response = mock(HttpResponse.class);
    var returnedCredentials = "{\"refresh_token\":\"refresh_token_response\"}";
    when(response.body()).thenReturn(returnedCredentials);
    when(httpClient.send(any(), any())).thenReturn(response);
    final Map<String, Object> queryParams = Map.of("code", "test_code");
    final Map<String, Object> actualQueryParams =
        flow.completeSourceOAuth(workspaceId, definitionId, queryParams, REDIRECT_URL);
    assertEquals(Jsons.serialize(Map.of("credentials", Jsons.deserialize(returnedCredentials))), Jsons.serialize(actualQueryParams));
  }

}
