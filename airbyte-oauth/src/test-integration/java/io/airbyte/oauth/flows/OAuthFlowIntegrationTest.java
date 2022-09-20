/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.oauth.flows;

import static org.mockito.Mockito.mock;

import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;
import com.sun.net.httpserver.HttpServer;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.oauth.OAuthFlowImplementation;
import java.io.IOException;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.net.http.HttpClient;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.Map;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@SuppressWarnings("PMD.AvoidReassigningParameters")
public abstract class OAuthFlowIntegrationTest {

  /**
   * Convenience base class for OAuthFlow tests. Those tests right now are meant to be run manually,
   * due to the consent flow in the browser
   */
  protected static final Logger LOGGER = LoggerFactory.getLogger(OAuthFlowIntegrationTest.class);
  protected static final String REDIRECT_URL = "http://localhost/auth_flow";
  protected static final int SERVER_LISTENING_PORT = 80;

  protected HttpClient httpClient;
  protected ConfigRepository configRepository;
  protected OAuthFlowImplementation flow;
  protected HttpServer server;
  protected ServerHandler serverHandler;

  protected Path getCredentialsPath() {
    return Path.of("secrets/config.json");
  };

  protected String getRedirectUrl() {
    return REDIRECT_URL;
  }

  protected abstract OAuthFlowImplementation getFlowImplementation(ConfigRepository configRepository, HttpClient httpClient);

  @BeforeEach
  public void setup() throws IOException {
    if (!Files.exists(getCredentialsPath())) {
      throw new IllegalStateException(
          "Must provide path to a oauth credentials file.");
    }
    configRepository = mock(ConfigRepository.class);
    httpClient = HttpClient.newBuilder().version(HttpClient.Version.HTTP_1_1).build();
    flow = this.getFlowImplementation(configRepository, httpClient);

    server = HttpServer.create(new InetSocketAddress(getServerListeningPort()), 0);
    server.setExecutor(null); // creates a default executor
    server.start();
    serverHandler = new ServerHandler("code");
    // Same endpoint as we use for airbyte instance
    server.createContext(getCallBackServerPath(), serverHandler);

  }

  protected String getCallBackServerPath() {
    return "/auth_flow";
  }

  protected int getServerListeningPort() {
    return SERVER_LISTENING_PORT;
  }

  @AfterEach
  void tearDown() {
    server.stop(1);
  }

  protected void waitForResponse(int limit) throws InterruptedException {
    // TODO: To automate, start a selenium job to navigate to the Consent URL and click on allowing
    // access...
    while (!serverHandler.isSucceeded() && limit > 0) {
      Thread.sleep(1000);
      limit -= 1;
    }
  }

  public static class ServerHandler implements HttpHandler {

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
        final String[] entry = param.split("=", 2);
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
