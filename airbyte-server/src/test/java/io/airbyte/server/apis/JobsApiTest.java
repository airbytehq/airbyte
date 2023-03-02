/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis;

import io.airbyte.api.model.generated.*;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.validation.json.JsonValidationException;
import io.micronaut.context.annotation.Requires;
import io.micronaut.context.env.Environment;
import io.micronaut.core.util.StringUtils;
import io.micronaut.http.HttpRequest;
import io.micronaut.http.HttpStatus;
import io.micronaut.test.extensions.junit5.annotation.MicronautTest;
import java.io.IOException;
import javax.ws.rs.NotFoundException;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

@MicronautTest
@Requires(property = "mockito.test.enabled",
          defaultValue = StringUtils.TRUE,
          value = StringUtils.TRUE)
@Requires(env = {Environment.TEST})
@SuppressWarnings("PMD.JUnitTestsShouldIncludeAssert")
class JobsApiTest extends BaseControllerTest {

  @Test
  void testCancelJob() throws IOException {
    Mockito.when(schedulerHandler.cancelJob(Mockito.any()))
        .thenReturn(new JobInfoRead())
        .thenThrow(new NotFoundException());
    final String path = "/api/v1/jobs/cancel";
    testEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new JobIdRequestBody())),
        HttpStatus.OK);
    testErrorEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new JobIdRequestBody())),
        HttpStatus.NOT_FOUND);
  }

  @Test
  void testGetAttemptNormalizationStatusesForJob() throws IOException {
    Mockito.when(jobHistoryHandler.getAttemptNormalizationStatuses(Mockito.any()))
        .thenReturn(new AttemptNormalizationStatusReadList());
    final String path = "/api/v1/jobs/get_normalization_status";
    testEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new JobIdRequestBody())),
        HttpStatus.OK);
  }

  @Test
  void testGetJobDebugInfo() throws IOException, JsonValidationException, ConfigNotFoundException {
    Mockito.when(jobHistoryHandler.getJobDebugInfo(Mockito.any()))
        .thenReturn(new JobDebugInfoRead())
        .thenThrow(new ConfigNotFoundException("", ""));
    final String path = "/api/v1/jobs/get_debug_info";
    testEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new JobIdRequestBody())),
        HttpStatus.OK);
    testErrorEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new JobIdRequestBody())),
        HttpStatus.NOT_FOUND);
  }

}
