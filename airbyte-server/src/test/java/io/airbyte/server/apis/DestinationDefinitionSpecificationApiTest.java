/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis;

import io.airbyte.api.model.generated.DestinationDefinitionIdWithWorkspaceId;
import io.airbyte.api.model.generated.DestinationDefinitionSpecificationRead;
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
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

@MicronautTest
@Requires(property = "mockito.test.enabled",
          defaultValue = StringUtils.TRUE,
          value = StringUtils.TRUE)
@Requires(env = {Environment.TEST})
@SuppressWarnings("PMD.JUnitTestsShouldIncludeAssert")
class DestinationDefinitionSpecificationApiTest extends BaseControllerTest {

  @Test
  void testCheckConnectionToDestination() throws JsonValidationException, ConfigNotFoundException, IOException {
    Mockito.when(schedulerHandler.getDestinationSpecification(Mockito.any()))
        .thenReturn(new DestinationDefinitionSpecificationRead())
        .thenThrow(new ConfigNotFoundException("", ""));
    final String path = "/api/v1/destination_definition_specifications/get";
    testEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new DestinationDefinitionIdWithWorkspaceId())),
        HttpStatus.OK);
    testErrorEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new DestinationDefinitionIdWithWorkspaceId())),
        HttpStatus.NOT_FOUND);
  }

}
