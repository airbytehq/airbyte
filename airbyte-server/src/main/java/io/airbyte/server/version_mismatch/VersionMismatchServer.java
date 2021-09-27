/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.version_mismatch;

import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.version.AirbyteVersion;
import io.airbyte.server.CorsFilter;
import io.airbyte.server.ServerRunnable;
import java.io.IOException;
import java.util.Map;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import org.eclipse.jetty.server.Server;
import org.eclipse.jetty.servlet.ServletContextHandler;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Serves an error for any call. This is only used if the server has a different version than the
 * stored version in the database, which means that there is a "version mismatch". When a version
 * mismatch occurs, a migration is required to upgrade the database. Until then, we show errors
 * using this server in order to prevent getting into a bad state.
 */
public class VersionMismatchServer implements ServerRunnable {

  private static final Logger LOGGER = LoggerFactory.getLogger(VersionMismatchServer.class);
  private final String version1;
  private final String version2;
  private final int port;

  public VersionMismatchServer(String version1, String version2, int port) {
    this.version1 = version1;
    this.version2 = version2;
    this.port = port;
  }

  @Override
  public void start() throws Exception {
    final Server server = getServer();
    server.start();
    server.join();
  }

  protected Server getServer() {
    final String errorMessage = AirbyteVersion.getErrorMessage(version1, version2);
    LOGGER.error(errorMessage);
    Server server = new Server(port);
    VersionMismatchServlet.ERROR_MESSAGE = errorMessage;
    ServletContextHandler handler = new ServletContextHandler();
    handler.addServlet(VersionMismatchServlet.class, "/*");
    server.setHandler(handler);

    return server;
  }

  public static class VersionMismatchServlet extends HttpServlet {

    // this error message should be overwritten before any requests are served
    public static String ERROR_MESSAGE = "Versions don't match!";

    public void doPost(HttpServletRequest request, HttpServletResponse response) throws IOException {
      this.serveDefaultRequest(response);
    }

    public void doGet(HttpServletRequest request, HttpServletResponse response) throws IOException {
      this.serveDefaultRequest(response);
    }

    public void doOptions(HttpServletRequest request, HttpServletResponse response) throws IOException {
      this.addCorsHeaders(response);
    }

    private void serveDefaultRequest(HttpServletResponse response) throws IOException {
      var outputMap = ImmutableMap.of("error", ERROR_MESSAGE);

      this.addCorsHeaders(response);

      response.setContentType("application/json");
      response.setStatus(HttpServletResponse.SC_INTERNAL_SERVER_ERROR);
      response.getWriter().println(Jsons.serialize(outputMap));
    }

    private void addCorsHeaders(HttpServletResponse response) {
      for (Map.Entry<String, String> entry : CorsFilter.MAP.entrySet()) {
        response.setHeader(entry.getKey(), entry.getValue());
      }
    }

  }

}
