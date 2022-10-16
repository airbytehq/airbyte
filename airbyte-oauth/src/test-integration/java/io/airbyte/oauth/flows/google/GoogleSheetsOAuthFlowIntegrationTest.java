/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.oauth.flows.google;

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
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.net.http.HttpClient;
import java.nio.charset.StandardCharsets;
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

public class GoogleSheetsOAuthFlowIntegrationTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(GoogleSheetsOAuthFlowIntegrationTest.class);
  private static final String REDIRECT_URL = "http://localhost/code";
  private static final Path CREDENTIALS_PATH = Path.of("secrets/google_sheets.json");

  private ConfigRepository configRepository;
  private GoogleSheetsOAuthFlow googleSheetsOAuthFlow;
  private HttpServer server;
  private ServerHandler serverHandler;
  private HttpClient httpClient;

  @BeforeEach
  public void setup() throws IOException {
    if (!Files.exists(CREDENTIALS_PATH)) {
      throw new IllegalStateException(
          "Must provide path to a oauth credentials file.");
    }
    configRepository = mock(ConfigRepository.class);
    httpClient = HttpClient.newBuilder().version(HttpClient.Version.HTTP_1_1).build();
    googleSheetsOAuthFlow = new GoogleSheetsOAuthFlow(configRepository, httpClient);

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
    final String fullConfigAsString = Files.readString(CREDENTIALS_PATH);
    final JsonNode credentialsJson = Jsons.deserialize(fullConfigAsString);
    when(configRepository.listSourceOAuthParam()).thenReturn(List.of(new SourceOAuthParameter()
        .withOauthParameterId(UUID.randomUUID())
        .withSourceDefinitionId(definitionId)
        .withWorkspaceId(workspaceId)
        .withConfiguration(Jsons.jsonNode(Map.of("credentials", ImmutableMap.builder()
            .put("client_id", credentialsJson.get("credentials").get("client_id").asText())
            .put("client_secret", credentialsJson.get("credentials").get("client_secret").asText())
            .build())))));
    final String url = googleSheetsOAuthFlow.getSourceConsentUrl(workspaceId, definitionId, REDIRECT_URL, Jsons.emptyObject(), null);
    LOGGER.info("Waiting for user consent at: {}", url);
    // TODO: To automate, start a selenium job to navigate to the Consent URL and click on allowing
    // access...
    while (!serverHandler.isSucceeded() && limit > 0) {
      Thread.sleep(1000);
      limit -= 1;
    }
    assertTrue(serverHandler.isSucceeded(), "Failed to get User consent on time");
    final Map<String, Object> params = googleSheetsOAuthFlow.completeSourceOAuth(workspaceId, definitionId,
        Map.of("code", serverHandler.getParamValue()), REDIRECT_URL);
    LOGGER.info("Response from completing OAuth Flow is: {}", params.toString());
    assertTrue(params.containsKey("credentials"));
    final Map<String, Object> credentials = (Map<String, Object>) params.get("credentials");
    assertTrue(credentials.containsKey("refresh_token"));
    assertTrue(credentials.get("refresh_token").toString().length() > 0);
    assertTrue(credentials.containsKey("access_token"));
    assertTrue(credentials.get("access_token").toString().length() > 0);
  }

  static class ServerHandler implements HttpHandler {

    final private String expectedParam;
    private String paramValue;
    private boolean succeeded;

    public ServerHandler(final String expectedParam) {
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
    public void handle(final HttpExchange t) {
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
        os.write(response.getBytes(StandardCharsets.UTF_8));
        os.close();
      } catch (final RuntimeException | IOException e) {
        LOGGER.error("Failed to parse from body {}", query, e);
      }
    }

    private static Map<String, String> deserialize(final String query) {
      if (query == null) {
        return null;
      }
      final Map<String, String> result = new HashMap<>();
      for (final String param : query.split("&")) {
        final String[] entry = param.split("=");
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
