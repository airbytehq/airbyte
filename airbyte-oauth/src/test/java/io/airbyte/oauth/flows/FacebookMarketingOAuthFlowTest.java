/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.oauth.flows;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

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
import java.util.List;
import java.util.Map;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

public class FacebookMarketingOAuthFlowTest {

  private static final String REDIRECT_URL = "https://airbyte.io";

  private HttpClient httpClient;
  private ConfigRepository configRepository;
  private FacebookMarketingOAuthFlow facebookMarketingOAuthFlow;

  private UUID workspaceId;
  private UUID definitionId;

  @BeforeEach
  public void setup() {
    httpClient = mock(HttpClient.class);
    configRepository = mock(ConfigRepository.class);
    facebookMarketingOAuthFlow = new FacebookMarketingOAuthFlow(configRepository, httpClient, FacebookMarketingOAuthFlowTest::getConstantState);

    workspaceId = UUID.randomUUID();
    definitionId = UUID.randomUUID();
  }

  private static String getConstantState() {
    return "state";
  }

  @Test
  public void testCompleteSourceOAuth() throws IOException, JsonValidationException, InterruptedException, ConfigNotFoundException {
    when(configRepository.listSourceOAuthParam()).thenReturn(List.of(new SourceOAuthParameter()
        .withOauthParameterId(UUID.randomUUID())
        .withSourceDefinitionId(definitionId)
        .withWorkspaceId(workspaceId)
        .withConfiguration(Jsons.jsonNode(ImmutableMap.builder()
            .put("client_id", "test_client_id")
            .put("client_secret", "test_client_secret")
            .build()))));

    Map<String, String> returnedCredentials = Map.of("access_token", "access_token_response");
    final HttpResponse response = mock(HttpResponse.class);
    when(response.body()).thenReturn(Jsons.serialize(returnedCredentials));
    when(httpClient.send(any(), any())).thenReturn(response);
    final Map<String, Object> queryParams = Map.of("code", "test_code");
    final Map<String, Object> actualQueryParams =
        facebookMarketingOAuthFlow.completeSourceOAuth(workspaceId, definitionId, queryParams, REDIRECT_URL);

    assertEquals(Jsons.serialize(returnedCredentials), Jsons.serialize(actualQueryParams));
  }

  @Test
  public void testCompleteDestinationOAuth() throws IOException, ConfigNotFoundException, JsonValidationException, InterruptedException {
    when(configRepository.listDestinationOAuthParam()).thenReturn(List.of(new DestinationOAuthParameter()
        .withOauthParameterId(UUID.randomUUID())
        .withDestinationDefinitionId(definitionId)
        .withWorkspaceId(workspaceId)
        .withConfiguration(Jsons.jsonNode(ImmutableMap.builder()
            .put("client_id", "test_client_id")
            .put("client_secret", "test_client_secret")
            .build()))));

    Map<String, String> returnedCredentials = Map.of("access_token", "access_token_response");
    final HttpResponse response = mock(HttpResponse.class);
    when(response.body()).thenReturn(Jsons.serialize(returnedCredentials));
    when(httpClient.send(any(), any())).thenReturn(response);
    final Map<String, Object> queryParams = Map.of("code", "test_code");
    final Map<String, Object> actualQueryParams =
        facebookMarketingOAuthFlow.completeDestinationOAuth(workspaceId, definitionId, queryParams, REDIRECT_URL);

    assertEquals(Jsons.serialize(returnedCredentials), Jsons.serialize(actualQueryParams));
  }

}
