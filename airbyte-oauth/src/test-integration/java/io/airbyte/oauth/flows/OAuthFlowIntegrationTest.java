/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
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
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.Map;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public abstract class OAuthFlowIntegrationTest {

  /**
   * Convenience base class for OAuthFlow tests. Those tests right now are meant to be run manually,
   * due to the consent flow in the browser
   */
  protected static final Logger LOGGER = LoggerFactory.getLogger(OAuthFlowIntegrationTest.class);
  protected static final String REDIRECT_URL = "http://localhost/code";

  protected ConfigRepository configRepository;
  protected OAuthFlowImplementation flow;
  protected HttpServer server;
  protected ServerHandler serverHandler;

  protected abstract Path get_credentials_path();

  protected abstract OAuthFlowImplementation getFlowObject(ConfigRepository configRepository);

  @BeforeEach
  public void setup() throws IOException {
    if (!Files.exists(get_credentials_path())) {
      throw new IllegalStateException(
          "Must provide path to a oauth credentials file.");
    }
    configRepository = mock(ConfigRepository.class);

    flow = this.getFlowObject(configRepository);

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
