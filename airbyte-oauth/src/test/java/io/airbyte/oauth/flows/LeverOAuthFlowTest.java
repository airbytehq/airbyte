/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.oauth.flows;

import io.airbyte.config.persistence.ConfigRepository;
import java.net.http.HttpClient;
import java.util.UUID;

public class LeverOAuthFlowTest {

  private UUID workspaceId;
  private UUID definitionId;
  private ConfigRepository configRepository;
  private LeverOAuthFlow flow;
  private HttpClient httpClient;

  private static final String REDIRECT_URL = "https://airbyte.io";

}
