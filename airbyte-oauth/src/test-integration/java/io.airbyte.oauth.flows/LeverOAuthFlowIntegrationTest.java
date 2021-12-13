/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.oauth.flows;

import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.oauth.OAuthFlowImplementation;
import java.io.IOException;
import java.net.http.HttpClient;
import java.nio.file.Path;
import org.junit.jupiter.api.BeforeEach;

public class LeverOAuthFlowIntegrationTest extends OAuthFlowIntegrationTest {

  protected static final Path CREDENTIALS_PATH = Path.of("secrets/lever.json");
  protected static final String REDIRECT_URL = "http://localhost:8000/oauth_flow";
  protected static final int SERVER_LISTENING_PORT = 8000;

  @Override
  protected String getCallBackServerPath() {
    return "/oauth_flow";
  }

  @Override
  protected Path getCredentialsPath() {
    return CREDENTIALS_PATH;
  }

  @Override
  protected OAuthFlowImplementation getFlowImplementation(ConfigRepository configRepository, HttpClient httpClient) {
    return null;
  }

  @Override
  protected int getServerListeningPort() {
    return 8000;
  }

  @BeforeEach
  public void setup() throws IOException {
    super.setup();
  }

}
