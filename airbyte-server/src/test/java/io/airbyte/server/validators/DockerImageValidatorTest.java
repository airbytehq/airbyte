package io.airbyte.server.validators;

import io.airbyte.commons.docker.DockerUtils;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.ConnectorSpecification;
import io.airbyte.server.errors.KnownException;
import io.airbyte.server.handlers.SchedulerHandler;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.io.IOException;
import java.net.URI;
import java.net.URISyntaxException;
import java.util.HashMap;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

class DockerImageValidatorTest {
  private SchedulerHandler schedulerHandler;
  private DockerImageValidator validator;

  @BeforeEach
  public void init(){
    schedulerHandler = mock(SchedulerHandler.class);
    validator = new DockerImageValidator(schedulerHandler);
  }

  @Test
  public void testAssertImageIsValid() throws URISyntaxException, IOException {
    final String repo = "repo";
    final String tag = "tag";
    final String imageName = DockerUtils.getTaggedImageName(repo, tag);
    when(schedulerHandler.getConnectorSpecification(imageName)).thenReturn(new ConnectorSpecification()
        .withDocumentationUrl(new URI("https://google.com"))
        .withChangelogUrl(new URI("https://google.com"))
        .withConnectionSpecification(Jsons.jsonNode(new HashMap<>())));

    assertDoesNotThrow(() -> validator.assertValidIntegrationImage(repo, tag));
  }

  @Test
  public void testThrowsOnInvalidImage() throws IOException {
    final String repo = "repo";
    final String tag = "tag";
    final String imageName = DockerUtils.getTaggedImageName(repo, tag);
    when(schedulerHandler.getConnectorSpecification(imageName)).thenThrow(new IllegalArgumentException());

    assertThrows(KnownException.class, () -> validator.assertValidIntegrationImage(repo, tag));
  }
}
