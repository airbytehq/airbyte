/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis;

import io.airbyte.commons.server.handlers.HealthCheckHandler;
import io.micronaut.http.HttpRequest;
import io.micronaut.http.HttpStatus;
import io.micronaut.test.extensions.junit5.annotation.MicronautTest;
import jakarta.inject.Inject;
import org.junit.jupiter.api.Test;

@MicronautTest
public class MicronautHealthCheck extends BaseControllerTest {

  @Test
  void testHealth() {
    testEndpointStatus(
        HttpRequest.GET("/api/v1/health"), HttpStatus.OK);
  }

}
