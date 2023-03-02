/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis;

import io.airbyte.api.model.generated.ConnectionState;
import io.airbyte.api.model.generated.SourceIdRequestBody;
import io.airbyte.commons.json.Jsons;
import io.micronaut.context.annotation.Requires;
import io.micronaut.context.env.Environment;
import io.micronaut.core.util.StringUtils;
import io.micronaut.http.HttpRequest;
import io.micronaut.http.HttpStatus;
import io.micronaut.test.extensions.junit5.annotation.MicronautTest;
import java.io.IOException;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

@MicronautTest
@Requires(property = "mockito.test.enabled",
          defaultValue = StringUtils.TRUE,
          value = StringUtils.TRUE)
@Requires(env = {Environment.TEST})
@SuppressWarnings("PMD.JUnitTestsShouldIncludeAssert")
class StateApiTest extends BaseControllerTest {

  @Test
  void testCreateOrUpdateState() throws IOException {
    Mockito.when(stateHandler.createOrUpdateState(Mockito.any()))
        .thenReturn(new ConnectionState());
    final String path = "/api/v1/state/create_or_update";
    testEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new SourceIdRequestBody())),
        HttpStatus.OK);
  }

  @Test
  void testGetState() throws IOException {
    Mockito.when(stateHandler.getState(Mockito.any()))
        .thenReturn(new ConnectionState());
    final String path = "/api/v1/state/get";
    testEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new SourceIdRequestBody())),
        HttpStatus.OK);
  }

}
