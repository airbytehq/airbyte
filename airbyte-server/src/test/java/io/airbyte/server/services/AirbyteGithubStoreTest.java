/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.services;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.io.IOException;
import java.net.http.HttpTimeoutException;
import java.time.Duration;
import java.util.Collections;
import java.util.concurrent.TimeUnit;
import okhttp3.mockwebserver.MockResponse;
import okhttp3.mockwebserver.MockWebServer;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;

public class AirbyteGithubStoreTest {

  private static final Duration TIMEOUT = Duration.ofSeconds(1);

  private static MockWebServer webServer;
  private static AirbyteGithubStore githubStore;

  @BeforeEach
  public void setUp() {
    webServer = new MockWebServer();
    githubStore = AirbyteGithubStore.test(webServer.url("/").toString(), TIMEOUT);
  }

  @Nested
  @DisplayName("when there is no internet")
  class NoInternet {

    @Test
    void testGetLatestDestinations() throws InterruptedException, IOException {
      webServer.shutdown();
      assertEquals(Collections.emptyList(), githubStore.getLatestDestinations());
    }

    @Test
    void testGetLatestSources() throws InterruptedException, IOException {
      webServer.shutdown();
      assertEquals(Collections.emptyList(), githubStore.getLatestSources());
    }

  }

  @Nested
  @DisplayName("when a bad file is specified")
  class BadFile {

    @Test
    void testGetLatestDestinations() throws InterruptedException {
      final var timeoutResp = new MockResponse().setResponseCode(404);
      webServer.enqueue(timeoutResp);

      assertEquals(Collections.emptyList(), githubStore.getLatestDestinations());
    }

    @Test
    void testGetLatestSources() throws InterruptedException {
      final var timeoutResp = new MockResponse().setResponseCode(404);
      webServer.enqueue(timeoutResp);

      assertEquals(Collections.emptyList(), githubStore.getLatestSources());
    }

  }

  @Nested
  @DisplayName("getFile")
  class GetFile {

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
          .setHeadersDelay(TIMEOUT.toSeconds() * 2, TimeUnit.SECONDS)
          .setBodyDelay(TIMEOUT.toSeconds() * 2, TimeUnit.SECONDS);
      webServer.enqueue(timeoutResp);

      assertThrows(HttpTimeoutException.class, () -> githubStore.getFile("test-file"));
    }

  }

}
