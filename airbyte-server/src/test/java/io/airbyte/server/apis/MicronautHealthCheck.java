package io.airbyte.server.apis;

import io.micronaut.http.HttpRequest;
import io.micronaut.http.HttpStatus;
import io.micronaut.test.extensions.junit5.annotation.MicronautTest;
import org.junit.jupiter.api.Test;

@MicronautTest
public class MicronautHealthCheck extends BaseControllerTest {

 @Test
 void testHealth() {
  testEndpointStatus(
          HttpRequest.GET("/api/v1/health"), HttpStatus.OK
  );
 }
}
