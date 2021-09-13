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

package io.airbyte.oauth;

import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;
import com.sun.net.httpserver.HttpServer;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.SourceOAuthParameter;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.oauth.google.GoogleAnalyticsOauthFlow;
import io.airbyte.oauth.google.GoogleOAuthFlow;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class GoogleOAuthFlowIntegrationTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(GoogleOAuthFlowIntegrationTest.class);
  private static final String REDIRECT_URL = "http://localhost/code";
  private static final Path CREDENTIALS_PATH = Path.of("secrets/credentials.json");

  private ConfigRepository configRepository;
  private GoogleOAuthFlow googleOAuthFlow;
  private HttpServer server;
  private ServerHandler serverHandler;

  @BeforeEach
  public void setup() throws IOException {
    if (!Files.exists(CREDENTIALS_PATH)) {
      throw new IllegalStateException(
          "Must provide path to a oauth credentials file.");
    }
    configRepository = mock(ConfigRepository.class);
    googleOAuthFlow = new GoogleAnalyticsOauthFlow(configRepository);

    server = HttpServer.create(new InetSocketAddress(80), 0);
    server.setExecutor(null); // creates a default executor
    server.start();
    serverHandler = new ServerHandler("code");
    server.createContext("/code", serverHandler);
  }

  @AfterEach
  void tearDown() {
    server.stop(1);
  }

  @Test
  public void testFullGoogleOAuthFlow() throws InterruptedException, ConfigNotFoundException, IOException, JsonValidationException {
    int limit = 20;
    final UUID workspaceId = UUID.randomUUID();
    final UUID definitionId = UUID.randomUUID();
    final String fullConfigAsString = new String(Files.readAllBytes(CREDENTIALS_PATH));
    final JsonNode credentialsJson = Jsons.deserialize(fullConfigAsString);
    when(configRepository.listSourceOAuthParam()).thenReturn(List.of(new SourceOAuthParameter()
        .withOauthParameterId(UUID.randomUUID())
        .withSourceDefinitionId(definitionId)
        .withWorkspaceId(workspaceId)
        .withConfiguration(Jsons.jsonNode(ImmutableMap.builder()
            .put("client_id", credentialsJson.get("client_id").asText())
            .put("client_secret", credentialsJson.get("client_secret").asText())
            .build()))));
    final String url = googleOAuthFlow.getSourceConsentUrl(workspaceId, definitionId, REDIRECT_URL);
    LOGGER.info("Waiting for user consent at: {}", url);
    // TODO: To automate, start a selenium job to navigate to the Consent URL and click on allowing
    // access...
    while (!serverHandler.isSucceeded() && limit > 0) {
      Thread.sleep(1000);
      limit -= 1;
    }
    assertTrue(serverHandler.isSucceeded(), "Failed to get User consent on time");
    final Map<String, Object> params = googleOAuthFlow.completeSourceOAuth(workspaceId, definitionId,
        Map.of("code", serverHandler.getParamValue()), REDIRECT_URL);
    LOGGER.info("Response from completing OAuth Flow is: {}", params.toString());
    assertTrue(params.containsKey("refresh_token"));
    assertTrue(params.get("refresh_token").toString().length() > 0);
  }

  static class ServerHandler implements HttpHandler {

    final private String expectedParam;
    private String paramValue;
    private boolean succeeded;

    public ServerHandler(String expectedParam) {
      this.expectedParam = expectedParam;
      this.paramValue = "";
      this.succeeded = false;
    }

    public boolean isSucceeded() {
      return succeeded;
    }

    public String getParamValue() {
      return paramValue;
    }

    @Override
    public void handle(HttpExchange t) {
      final String query = t.getRequestURI().getQuery();
      LOGGER.info("Received query: '{}'", query);
      final Map<String, String> data;
      try {
        data = deserialize(query);
        final String response;
        if (data != null && data.containsKey(expectedParam)) {
          paramValue = data.get(expectedParam);
          response = String.format("Successfully extracted %s:\n'%s'\nTest should be continuing the OAuth Flow to retrieve the refresh_token...",
              expectedParam, paramValue);
          LOGGER.info(response);
          t.sendResponseHeaders(200, response.length());
          succeeded = true;
        } else {
          response = String.format("Unable to parse query params from redirected url: %s", query);
          t.sendResponseHeaders(500, response.length());
        }
        final OutputStream os = t.getResponseBody();
        os.write(response.getBytes());
        os.close();
      } catch (RuntimeException | IOException e) {
        LOGGER.error("Failed to parse from body {}", query, e);
      }
    }

    private static Map<String, String> deserialize(String query) {
      if (query == null) {
        return null;
      }
      final Map<String, String> result = new HashMap<>();
      for (String param : query.split("&")) {
        String[] entry = param.split("=");
        if (entry.length > 1) {
          result.put(entry[0], entry[1]);
        } else {
          result.put(entry[0], "");
        }
      }
      return result;
    }

  }

}
