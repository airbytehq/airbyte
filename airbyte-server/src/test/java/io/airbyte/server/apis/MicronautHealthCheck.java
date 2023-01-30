/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis;

import io.airbyte.api.model.generated.HealthCheckRead;
import io.micronaut.context.annotation.Requires;
import io.micronaut.context.env.Environment;
import io.micronaut.core.util.StringUtils;
import io.micronaut.http.HttpRequest;
import io.micronaut.http.HttpStatus;
import io.micronaut.test.extensions.junit5.annotation.MicronautTest;
import java.io.IOException;
import lombok.extern.slf4j.Slf4j;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

@MicronautTest
@Requires(property = "mockito.test.enabled",
          defaultValue = StringUtils.TRUE,
          value = StringUtils.TRUE)
@Requires(env = {Environment.TEST})
@Slf4j
public class MicronautHealthCheck extends BaseControllerTest {

  @Test
  void testHealth() throws IOException {
    Mockito.when(healthApiController.getHealthCheck())
        .thenReturn(new HealthCheckRead());
    testEndpointStatus(
        HttpRequest.GET("/api/v1/health"), HttpStatus.OK);
  }

}
