/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.oauth.flows;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.SourceOAuthParameter;
import io.airbyte.config.DestinationOAuthParameter;
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

public class ZuoraOAuthFlowTest {

  private UUID workspaceId;
  private UUID definitionId;
  private ZuoraOAuthFlow zuoraoAuthFlow;

  @BeforeEach
  public void setup() throws IOException, JsonValidationException {
    workspaceId = UUID.randomUUID();
    definitionId = UUID.randomUUID();
    zuoraoAuthFlow = new ZuoraOAuthFlow();

  }

  @Test
  public void testGetConcentUrl() throws IOException, InterruptedException, ConfigNotFoundException {
    String concentUrl =
        zuoraoAuthFlow.getSourceConsentUrl(workspaceId, definitionId, "");
    assertEquals(concentUrl, "");
    concentUrl =
        zuoraoAuthFlow.getDestinationConsentUrl(workspaceId, definitionId, "");
    assertEquals(concentUrl, "");
  }


  @Test
  public void testCompleteOAuth() throws IOException, JsonValidationException, InterruptedException, ConfigNotFoundException {

    final Map<String, Object> queryParams = Map.of("code", "test_code");
    Map<String, Object> actualQueryParams =
        zuoraoAuthFlow.completeSourceOAuth(workspaceId, definitionId, queryParams, "");
    assertTrue(actualQueryParams.equals(Map.of()));

    actualQueryParams =
        zuoraoAuthFlow.completeDestinationOAuth(workspaceId, definitionId, queryParams, "");
    assertTrue(actualQueryParams.equals(Map.of()));
  }

}
