/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.validators;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import io.airbyte.commons.docker.DockerUtils;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.scheduler.client.SynchronousResponse;
import io.airbyte.scheduler.client.SynchronousSchedulerClient;
import io.airbyte.server.errors.KnownException;
import java.io.IOException;
import java.net.URI;
import java.net.URISyntaxException;
import java.util.HashMap;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class DockerImageValidatorTest {

  private SynchronousSchedulerClient schedulerJobClient;
  private DockerImageValidator validator;

  @BeforeEach
  public void init() {
    schedulerJobClient = mock(SynchronousSchedulerClient.class);
    validator = new DockerImageValidator(schedulerJobClient);
  }

  @SuppressWarnings("unchecked")
  @Test
  public void testAssertImageIsValid() throws URISyntaxException, IOException {
    final String repo = "repo";
    final String tag = "tag";
    final String imageName = DockerUtils.getTaggedImageName(repo, tag);

    final SynchronousResponse<ConnectorSpecification> specResponse = mock(SynchronousResponse.class);
    final ConnectorSpecification connectorSpecification = new ConnectorSpecification()
        .withDocumentationUrl(new URI("https://google.com"))
        .withChangelogUrl(new URI("https://google.com"))
        .withConnectionSpecification(Jsons.jsonNode(new HashMap<>()));
    when(schedulerJobClient.createGetSpecJob(imageName)).thenReturn(specResponse);
    when(specResponse.getOutput()).thenReturn(connectorSpecification);
    when(specResponse.isSuccess()).thenReturn(true);

    assertDoesNotThrow(() -> validator.assertValidIntegrationImage(repo, tag));
  }

  @SuppressWarnings("unchecked")
  @Test
  public void testThrowsOnInvalidImage() throws IOException {
    final String repo = "repo";
    final String tag = "tag";
    final String imageName = DockerUtils.getTaggedImageName(repo, tag);
    final SynchronousResponse<ConnectorSpecification> specResponse = mock(SynchronousResponse.class);
    when(specResponse.isSuccess()).thenReturn(false);
    when(schedulerJobClient.createGetSpecJob(imageName)).thenReturn(specResponse);

    assertThrows(KnownException.class, () -> validator.assertValidIntegrationImage(repo, tag));
  }

}
