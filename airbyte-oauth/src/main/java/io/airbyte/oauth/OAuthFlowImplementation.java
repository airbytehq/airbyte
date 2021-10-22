/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.oauth;

import io.airbyte.config.persistence.ConfigNotFoundException;
import java.io.IOException;
import java.util.Map;
import java.util.UUID;

public interface OAuthFlowImplementation {

  String getSourceConsentUrl(UUID workspaceId, UUID sourceDefinitionId, String redirectUrl, Map<String, Object> inputParameters)
      throws IOException, ConfigNotFoundException;

  String getDestinationConsentUrl(UUID workspaceId, UUID destinationDefinitionId, String redirectUrl, Map<String, Object> inputParameters)
      throws IOException, ConfigNotFoundException;

  Map<String, Object> completeSourceOAuth(UUID workspaceId,
                                          UUID sourceDefinitionId,
                                          Map<String, Object> queryParams,
                                          String redirectUrl,
                                          Map<String, Object> inputParameters)
      throws IOException, ConfigNotFoundException;

  Map<String, Object> completeDestinationOAuth(UUID workspaceId,
                                               UUID destinationDefinitionId,
                                               Map<String, Object> queryParams,
                                               String redirectUrl,
                                               Map<String, Object> inputParameters)
      throws IOException, ConfigNotFoundException;

}
