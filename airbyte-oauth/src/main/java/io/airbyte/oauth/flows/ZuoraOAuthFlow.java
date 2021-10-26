/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.oauth.flows;

import io.airbyte.oauth.OAuthFlowImplementation;
import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.oauth.BaseOAuthFlow;
import java.io.IOException;
import java.util.Map;
import java.util.UUID;

/**
 * Following docs from
 * https://www.zuora.com/developer/api-reference/#section/Authentication/OAuth-v2.0
 * Zoura oAuth supports only client_credentials grant type therefore no getting
 * code/refresh_token stage needed. Only purpose of Zuora oAuth flow is to
 * store and inject client_id/secret_id parameters so connector could do
 * authentication on its own.
 */
public class ZuoraOAuthFlow implements OAuthFlowImplementation {

  public String getSourceConsentUrl(UUID workspaceId, UUID sourceDefinitionId, String redirectUrl) throws IOException, ConfigNotFoundException {
     return "";
  }

  public String getDestinationConsentUrl(UUID workspaceId, UUID destinationDefinitionId, String redirectUrl) throws IOException, ConfigNotFoundException {
     return "";
  }

  public Map<String, Object> completeSourceOAuth(
                                                 final UUID workspaceId,
                                                 final UUID sourceDefinitionId,
                                                 final Map<String, Object> queryParams,
                                                 final String redirectUrl)
      throws IOException, ConfigNotFoundException {
    return Map.of();
  }

  public Map<String, Object> completeDestinationOAuth(final UUID workspaceId,
                                                      final UUID destinationDefinitionId,
                                                      final Map<String, Object> queryParams,
                                                      final String redirectUrl)
      throws IOException, ConfigNotFoundException {
    return Map.of();
  }

}
