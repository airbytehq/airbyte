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

package io.airbyte.server.version_mismatch;

import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.version.AirbyteVersion;
import io.airbyte.server.CorsFilter;
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
public class VersionMismatchServer {

  private static final Logger LOGGER = LoggerFactory.getLogger(VersionMismatchServer.class);
  private final String version1;
  private final String version2;
  private final int port;

  public VersionMismatchServer(String version1, String version2, int port) {
    this.version1 = version1;
    this.version2 = version2;
    this.port = port;
  }

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
