/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis;

import io.airbyte.commons.server.handlers.HealthCheckHandler;
import io.micronaut.context.annotation.Requires;
import io.micronaut.context.env.Environment;
import io.micronaut.core.util.StringUtils;
import io.micronaut.http.HttpRequest;
import io.micronaut.http.HttpStatus;
import io.micronaut.http.client.HttpClient;
import io.micronaut.http.client.annotation.Client;
import io.micronaut.test.extensions.junit5.annotation.MicronautTest;
import jakarta.inject.Inject;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

@MicronautTest
@Requires(property = "mockito.test.enabled",
        defaultValue = StringUtils.TRUE,
        value = StringUtils.TRUE)
@Requires(env = {Environment.TEST})
public class MicronautHealthCheck extends BaseControllerTest {

  @Inject
  @Client("/")
  HttpClient client;

  @Test
  void testHealth() {
    testEndpointStatus(
        HttpRequest.GET("/api/v1/health"), HttpStatus.OK);
  }

  void testEndpointStatus(HttpRequest request, HttpStatus expectedStatus) {
    assertEquals(expectedStatus, client.toBlocking().exchange(request).getStatus());
  }

}
