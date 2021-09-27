/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.handlers;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.google.common.collect.Lists;
import io.airbyte.api.model.SourceDefinitionCreate;
import io.airbyte.api.model.SourceDefinitionIdRequestBody;
import io.airbyte.api.model.SourceDefinitionRead;
import io.airbyte.api.model.SourceDefinitionReadList;
import io.airbyte.api.model.SourceDefinitionUpdate;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.scheduler.client.CachingSynchronousSchedulerClient;
import io.airbyte.server.services.AirbyteGithubStore;
import io.airbyte.server.validators.DockerImageValidator;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.net.URI;
import java.net.URISyntaxException;
import java.util.Collections;
import java.util.UUID;
import java.util.function.Supplier;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;

class SourceDefinitionsHandlerTest {

  private ConfigRepository configRepository;
  private DockerImageValidator dockerImageValidator;
  private StandardSourceDefinition source;
  private SourceDefinitionsHandler sourceHandler;
  private Supplier<UUID> uuidSupplier;
  private CachingSynchronousSchedulerClient schedulerSynchronousClient;
  private AirbyteGithubStore githubStore;

  @SuppressWarnings("unchecked")
  @BeforeEach
  void setUp() {
    configRepository = mock(ConfigRepository.class);
    uuidSupplier = mock(Supplier.class);
    dockerImageValidator = mock(DockerImageValidator.class);
    schedulerSynchronousClient = spy(CachingSynchronousSchedulerClient.class);
    githubStore = mock(AirbyteGithubStore.class);

    source = generateSource();

    sourceHandler = new SourceDefinitionsHandler(configRepository, dockerImageValidator, uuidSupplier, schedulerSynchronousClient, githubStore);
  }

  private StandardSourceDefinition generateSource() {
    final UUID sourceId = UUID.randomUUID();

    return new StandardSourceDefinition()
        .withSourceDefinitionId(sourceId)
        .withName("presto")
        .withDocumentationUrl("https://netflix.com")
        .withDockerRepository("dockerstuff")
        .withDockerImageTag("12.3")
        .withIcon("http.svg");
  }

  @Test
  @DisplayName("listSourceDefinition should return the right list")
  void testListSourceDefinitions() throws JsonValidationException, IOException, URISyntaxException {
    final StandardSourceDefinition source2 = generateSource();

    when(configRepository.listStandardSources()).thenReturn(Lists.newArrayList(source, source2));

    SourceDefinitionRead expectedSourceDefinitionRead1 = new SourceDefinitionRead()
        .sourceDefinitionId(source.getSourceDefinitionId())
        .name(source.getName())
        .dockerRepository(source.getDockerRepository())
        .dockerImageTag(source.getDockerImageTag())
        .documentationUrl(new URI(source.getDocumentationUrl()))
        .icon(SourceDefinitionsHandler.loadIcon(source.getIcon()));

    SourceDefinitionRead expectedSourceDefinitionRead2 = new SourceDefinitionRead()
        .sourceDefinitionId(source2.getSourceDefinitionId())
        .name(source2.getName())
        .dockerRepository(source.getDockerRepository())
        .dockerImageTag(source.getDockerImageTag())
        .documentationUrl(new URI(source.getDocumentationUrl()))
        .icon(SourceDefinitionsHandler.loadIcon(source.getIcon()));

    final SourceDefinitionReadList actualSourceDefinitionReadList = sourceHandler.listSourceDefinitions();

    assertEquals(Lists.newArrayList(expectedSourceDefinitionRead1, expectedSourceDefinitionRead2),
        actualSourceDefinitionReadList.getSourceDefinitions());
  }

  @Test
  @DisplayName("getSourceDefinition should return the right source")
  void testGetSourceDefinition() throws JsonValidationException, ConfigNotFoundException, IOException, URISyntaxException {
    when(configRepository.getStandardSourceDefinition(source.getSourceDefinitionId()))
        .thenReturn(source);

    SourceDefinitionRead expectedSourceDefinitionRead = new SourceDefinitionRead()
        .sourceDefinitionId(source.getSourceDefinitionId())
        .name(source.getName())
        .dockerRepository(source.getDockerRepository())
        .dockerImageTag(source.getDockerImageTag())
        .documentationUrl(new URI(source.getDocumentationUrl()))
        .icon(SourceDefinitionsHandler.loadIcon(source.getIcon()));

    final SourceDefinitionIdRequestBody sourceDefinitionIdRequestBody =
        new SourceDefinitionIdRequestBody().sourceDefinitionId(source.getSourceDefinitionId());

    final SourceDefinitionRead actualSourceDefinitionRead = sourceHandler.getSourceDefinition(sourceDefinitionIdRequestBody);

    assertEquals(expectedSourceDefinitionRead, actualSourceDefinitionRead);
  }

  @Test
  @DisplayName("createSourceDefinition should correctly create a sourceDefinition")
  void testCreateSourceDefinition() throws URISyntaxException, IOException, JsonValidationException {
    final StandardSourceDefinition source = generateSource();
    when(uuidSupplier.get()).thenReturn(source.getSourceDefinitionId());
    final SourceDefinitionCreate create = new SourceDefinitionCreate()
        .name(source.getName())
        .dockerRepository(source.getDockerRepository())
        .dockerImageTag(source.getDockerImageTag())
        .documentationUrl(new URI(source.getDocumentationUrl()))
        .icon(source.getIcon());

    final SourceDefinitionRead expectedRead = new SourceDefinitionRead()
        .name(source.getName())
        .dockerRepository(source.getDockerRepository())
        .dockerImageTag(source.getDockerImageTag())
        .documentationUrl(new URI(source.getDocumentationUrl()))
        .sourceDefinitionId(source.getSourceDefinitionId())
        .icon(SourceDefinitionsHandler.loadIcon(source.getIcon()));

    final SourceDefinitionRead actualRead = sourceHandler.createSourceDefinition(create);

    assertEquals(expectedRead, actualRead);
    verify(dockerImageValidator).assertValidIntegrationImage(source.getDockerRepository(), source.getDockerImageTag());
  }

  @Test
  @DisplayName("updateSourceDefinition should correctly update a sourceDefinition")
  void testUpdateSourceDefinition() throws ConfigNotFoundException, IOException, JsonValidationException {
    when(configRepository.getStandardSourceDefinition(source.getSourceDefinitionId())).thenReturn(source);
    final String newDockerImageTag = "averydifferenttag";
    final SourceDefinitionRead sourceDefinition = sourceHandler
        .getSourceDefinition(new SourceDefinitionIdRequestBody().sourceDefinitionId(source.getSourceDefinitionId()));
    final String dockerRepository = sourceDefinition.getDockerRepository();
    final String currentTag = sourceDefinition.getDockerImageTag();
    assertNotEquals(newDockerImageTag, currentTag);

    final SourceDefinitionRead sourceDefinitionRead = sourceHandler
        .updateSourceDefinition(new SourceDefinitionUpdate().sourceDefinitionId(source.getSourceDefinitionId()).dockerImageTag(newDockerImageTag));

    assertEquals(newDockerImageTag, sourceDefinitionRead.getDockerImageTag());
    verify(dockerImageValidator).assertValidIntegrationImage(dockerRepository, newDockerImageTag);
    verify(schedulerSynchronousClient).resetCache();
  }

  @Nested
  @DisplayName("listLatest")
  class listLatest {

    @Test
    @DisplayName("should return the latest list")
    void testCorrect() throws IOException, InterruptedException {
      final StandardSourceDefinition sourceDefinition = generateSource();
      when(githubStore.getLatestSources()).thenReturn(Collections.singletonList(sourceDefinition));

      final var sourceDefinitionReadList = sourceHandler.listLatestSourceDefinitions().getSourceDefinitions();
      assertEquals(1, sourceDefinitionReadList.size());

      final var sourceDefinitionRead = sourceDefinitionReadList.get(0);
      assertEquals(SourceDefinitionsHandler.buildSourceDefinitionRead(sourceDefinition), sourceDefinitionRead);
    }

    @Test
    @DisplayName("returns empty collection if cannot find latest definitions")
    void testHttpTimeout() {
      assertEquals(0, sourceHandler.listLatestSourceDefinitions().getSourceDefinitions().size());
    }

    @Test
    @DisplayName("Icon should contain data")
    void testIconHoldsData() {
      final String icon = SourceDefinitionsHandler.loadIcon(source.getIcon());
      assertNotNull(icon);
      assert (icon.length() > 3000);
      assert (icon.length() < 6000);
    }

  }

}
