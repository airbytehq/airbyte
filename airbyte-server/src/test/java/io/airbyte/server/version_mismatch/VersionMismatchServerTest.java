/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
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
    assertEquals(http.getHeaderField(HttpHeaders.ACCESS_CONTROL_ALLOW_HEADERS), "Origin, Content-Type, Accept, Content-Encoding");
    assertEquals(http.getHeaderField(HttpHeaders.ACCESS_CONTROL_ALLOW_METHODS), "GET, POST, PUT, DELETE, OPTIONS, HEAD");
  }

}
