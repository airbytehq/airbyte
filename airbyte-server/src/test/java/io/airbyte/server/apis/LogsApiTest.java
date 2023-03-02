/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis;

import io.airbyte.api.model.generated.LogsRequestBody;
import io.airbyte.commons.json.Jsons;
import io.micronaut.context.annotation.Requires;
import io.micronaut.context.env.Environment;
import io.micronaut.core.util.StringUtils;
import io.micronaut.http.HttpRequest;
import io.micronaut.http.HttpStatus;
import io.micronaut.test.extensions.junit5.annotation.MicronautTest;
import java.io.File;
import java.io.IOException;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

@MicronautTest
@Requires(property = "mockito.test.enabled",
          defaultValue = StringUtils.TRUE,
          value = StringUtils.TRUE)
@Requires(env = {Environment.TEST})
@SuppressWarnings("PMD.JUnitTestsShouldIncludeAssert")
class LogsApiTest extends BaseControllerTest {

  @Test
  void testGetLogs() throws IOException {
    Mockito.when(logsHandler.getLogs(Mockito.any()))
        .thenReturn(File.createTempFile("abc", "def"));
    final String path = "/api/v1/logs/get";
    testEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new LogsRequestBody())),
        HttpStatus.OK);
  }

}
