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

package io.airbyte.workers.process;

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

  public WorkerHeartbeatServer(int port) {
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
    Server server = new Server(port);
    ServletContextHandler handler = new ServletContextHandler();
    handler.addServlet(WorkerHeartbeatServlet.class, "/*");
    server.setHandler(handler);

    return server;
  }

  public static class WorkerHeartbeatServlet extends HttpServlet {

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
      var outputMap = ImmutableMap.of("up", true);

      this.addCorsHeaders(response);

      response.setContentType("application/json");
      response.setStatus(HttpServletResponse.SC_OK);
      response.getWriter().println(Jsons.serialize(outputMap));
    }

    private void addCorsHeaders(HttpServletResponse response) {
      for (Map.Entry<String, String> entry : CORS_FILTER_MAP.entrySet()) {
        response.setHeader(entry.getKey(), entry.getValue());
      }
    }

  }

  private static final ImmutableMap<String, String> CORS_FILTER_MAP = ImmutableMap.of(
      HttpHeaders.ACCESS_CONTROL_ALLOW_ORIGIN, "*",
      HttpHeaders.ACCESS_CONTROL_ALLOW_HEADERS, "Origin, Content-Type, Accept, Content-Encoding",
      HttpHeaders.ACCESS_CONTROL_ALLOW_METHODS, "GET, POST, PUT, DELETE, OPTIONS, HEAD");

}
