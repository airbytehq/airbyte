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

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.google.common.net.HttpHeaders;
import java.net.HttpURLConnection;
import java.net.ServerSocket;
import java.net.URI;
import java.net.URL;
import org.eclipse.jetty.http.HttpStatus;
import org.eclipse.jetty.server.Server;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;

public class VersionMismatchServerTest {

  private static final String VERSION1 = "v1";
  private static final String VERSION2 = "v2";

  private static URI rootUri;
  private static Server server;

  @BeforeAll
  public static void startServer() throws Exception {
    // get any available local port
    final ServerSocket socket = new ServerSocket(0);
    final int port = socket.getLocalPort();
    socket.close();

    server = new VersionMismatchServer(VERSION1, VERSION2, port).getServer();
    rootUri = new URI("http://localhost:" + port + "/");

    server.start();
  }

  @AfterAll
  public static void stopServer() throws Exception {
    server.stop();
  }

  @ParameterizedTest
  @ValueSource(strings = {
    "/",
    "/api/v1/health",
    "/random_path"
  })
  public void testIt(String relativePath) throws Exception {
    final URL url = rootUri.resolve(relativePath).toURL();
    final HttpURLConnection http = (HttpURLConnection) url.openConnection();

    http.connect();

    assertEquals(HttpStatus.INTERNAL_SERVER_ERROR_500, http.getResponseCode());

    assertEquals(http.getHeaderField(HttpHeaders.ACCESS_CONTROL_ALLOW_ORIGIN), "*");
    assertEquals(http.getHeaderField(HttpHeaders.ACCESS_CONTROL_ALLOW_HEADERS), "Origin, Content-Type, Accept, Content-Encoding, Authorization");
    assertEquals(http.getHeaderField(HttpHeaders.ACCESS_CONTROL_ALLOW_METHODS), "GET, POST, PUT, DELETE, OPTIONS, HEAD");
  }

}
