/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.container_orchestrator;

import static org.junit.jupiter.api.Assertions.assertEquals;

import io.micronaut.http.HttpRequest;
import io.micronaut.http.client.HttpClient;
import io.micronaut.http.client.annotation.Client;
import io.micronaut.runtime.server.EmbeddedServer;
import io.micronaut.test.extensions.junit5.annotation.MicronautTest;
import jakarta.inject.Inject;
import org.junit.jupiter.api.Test;

@MicronautTest
class HeartbeatControllerTest {

  @Inject
  EmbeddedServer server;

  @Inject
  @Client("/")
  HttpClient client;

  @Test
  void testHeartbeat() {
    final var response = client.toBlocking().retrieve(HttpRequest.GET("/"));
    assertEquals("{\"up\":true}", response);
  }

}
