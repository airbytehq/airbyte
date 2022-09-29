/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.container_orchestrator;

import com.google.common.collect.ImmutableMap;
import com.google.common.net.HttpHeaders;
import io.airbyte.commons.json.Jsons;
import java.io.IOException;
import java.util.Map;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import org.eclipse.jetty.server.Server;
import org.eclipse.jetty.servlet.ServletContextHandler;

/**
 * Creates a server on a single port that returns a 200 JSON response on any path requested. This is
 * intended to stay up as long as the Kube worker exists so pods spun up can check if the spawning
 * Kube worker still exists.
 */
public class WorkerHeartbeatServer {

  private final int port;
  private Server server;

  public WorkerHeartbeatServer(final int port) {
    this.port = port;
  }

  public void start() throws Exception {
    server = getServer();
    server.start();
    server.join();
  }

  public void startBackground() throws Exception {
    server = getServer();
    server.start();
  }

  public void stop() throws Exception {
    server.stop();
  }

  protected Server getServer() {
    final Server server = new Server(port);
    final ServletContextHandler handler = new ServletContextHandler();
    handler.addServlet(WorkerHeartbeatServlet.class, "/*");
    server.setHandler(handler);

    return server;
  }

  public static class WorkerHeartbeatServlet extends HttpServlet {

    @Override
    public void doPost(final HttpServletRequest request, final HttpServletResponse response) throws IOException {
      this.serveDefaultRequest(response);
    }

    @Override
    public void doGet(final HttpServletRequest request, final HttpServletResponse response) throws IOException {
      this.serveDefaultRequest(response);
    }

    @Override
    public void doOptions(final HttpServletRequest request, final HttpServletResponse response) throws IOException {
      this.addCorsHeaders(response);
    }

    private void serveDefaultRequest(final HttpServletResponse response) throws IOException {
      final var outputMap = ImmutableMap.of("up", true);

      this.addCorsHeaders(response);

      response.setContentType("application/json");
      response.setStatus(HttpServletResponse.SC_OK);
      response.getWriter().println(Jsons.serialize(outputMap));
    }

    private void addCorsHeaders(final HttpServletResponse response) {
      for (final Map.Entry<String, String> entry : CORS_FILTER_MAP.entrySet()) {
        response.setHeader(entry.getKey(), entry.getValue());
      }
    }

  }

  private static final ImmutableMap<String, String> CORS_FILTER_MAP = ImmutableMap.of(
      HttpHeaders.ACCESS_CONTROL_ALLOW_ORIGIN, "*",
      HttpHeaders.ACCESS_CONTROL_ALLOW_HEADERS, "Origin, Content-Type, Accept, Content-Encoding",
      HttpHeaders.ACCESS_CONTROL_ALLOW_METHODS, "GET, POST, PUT, DELETE, OPTIONS, HEAD");

}
