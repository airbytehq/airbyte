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

package io.airbyte.server.services;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.io.IOException;
import java.net.http.HttpTimeoutException;
import java.util.concurrent.TimeUnit;
import okhttp3.mockwebserver.MockResponse;
import okhttp3.mockwebserver.MockWebServer;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;

public class AirbyteGithubStoreTest {

  private static MockWebServer webServer;
  private static AirbyteGithubStore githubStore;

  @BeforeAll
  public static void setUp() {
    webServer = new MockWebServer();
    githubStore = AirbyteGithubStore.test(webServer.url("/").toString());
  }

  @Nested
  @DisplayName("getFile")
  class getFile {

    @Test
    void testReturn() throws IOException, InterruptedException {
      final var goodBody = "great day!";
      final var goodResp = new MockResponse().setResponseCode(200)
          .addHeader("Content-Type", "text/plain; charset=utf-8")
          .addHeader("Cache-Control", "no-cache")
          .setBody(goodBody);
      webServer.enqueue(goodResp);

      var fileStr = githubStore.getFile("test-file");
      assertEquals(goodBody, fileStr);
    }

    @Test
    void testHttpTimeout() {
      final var timeoutResp = new MockResponse().setResponseCode(200)
          .addHeader("Content-Type", "text/plain; charset=utf-8")
          .addHeader("Cache-Control", "no-cache")
          .setBody("")
          .setHeadersDelay(10, TimeUnit.SECONDS)
          .setBodyDelay(10, TimeUnit.SECONDS);
      webServer.enqueue(timeoutResp);

      assertThrows(HttpTimeoutException.class, () -> githubStore.getFile("test-file"));
    }

  }

}
