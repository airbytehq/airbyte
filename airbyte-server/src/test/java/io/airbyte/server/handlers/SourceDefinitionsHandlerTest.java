/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.server.handlers;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
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
import io.airbyte.scheduler.client.CachingSchedulerJobClient;
import io.airbyte.server.validators.DockerImageValidator;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.net.URI;
import java.net.URISyntaxException;
import java.util.UUID;
import java.util.function.Supplier;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class SourceDefinitionsHandlerTest {

  private ConfigRepository configRepository;
  private DockerImageValidator dockerImageValidator;
  private StandardSourceDefinition source;
  private SourceDefinitionsHandler sourceHandler;
  private Supplier<UUID> uuidSupplier;
  private CachingSchedulerJobClient schedulerJobClient;

  @SuppressWarnings("unchecked")
  @BeforeEach
  void setUp() {
    configRepository = mock(ConfigRepository.class);
    uuidSupplier = mock(Supplier.class);
    dockerImageValidator = mock(DockerImageValidator.class);
    schedulerJobClient = spy(CachingSchedulerJobClient.class);

    source = generateSource();
    sourceHandler = new SourceDefinitionsHandler(configRepository, dockerImageValidator, uuidSupplier, schedulerJobClient);
  }

  private StandardSourceDefinition generateSource() {
    final UUID sourceId = UUID.randomUUID();

    return new StandardSourceDefinition()
        .withSourceDefinitionId(sourceId)
        .withName("presto")
        .withDocumentationUrl("https://netflix.com")
        .withDockerRepository("dockerstuff")
        .withDockerImageTag("12.3");
  }

  @Test
  void testListSourceDefinitions() throws JsonValidationException, IOException, ConfigNotFoundException, URISyntaxException {
    final StandardSourceDefinition source2 = generateSource();

    when(configRepository.listStandardSources()).thenReturn(Lists.newArrayList(source, source2));

    SourceDefinitionRead expectedSourceDefinitionRead1 = new SourceDefinitionRead()
        .sourceDefinitionId(source.getSourceDefinitionId())
        .name(source.getName())
        .dockerRepository(source.getDockerRepository())
        .dockerImageTag(source.getDockerImageTag())
        .documentationUrl(new URI(source.getDocumentationUrl()));

    SourceDefinitionRead expectedSourceDefinitionRead2 = new SourceDefinitionRead()
        .sourceDefinitionId(source2.getSourceDefinitionId())
        .name(source2.getName())
        .dockerRepository(source.getDockerRepository())
        .dockerImageTag(source.getDockerImageTag())
        .documentationUrl(new URI(source.getDocumentationUrl()));

    final SourceDefinitionReadList actualSourceDefinitionReadList = sourceHandler.listSourceDefinitions();

    assertEquals(Lists.newArrayList(expectedSourceDefinitionRead1, expectedSourceDefinitionRead2),
        actualSourceDefinitionReadList.getSourceDefinitions());
  }

  @Test
  void testGetSourceDefinition() throws JsonValidationException, ConfigNotFoundException, IOException, URISyntaxException {
    when(configRepository.getStandardSourceDefinition(source.getSourceDefinitionId()))
        .thenReturn(source);

    SourceDefinitionRead expectedSourceDefinitionRead = new SourceDefinitionRead()
        .sourceDefinitionId(source.getSourceDefinitionId())
        .name(source.getName())
        .dockerRepository(source.getDockerRepository())
        .dockerImageTag(source.getDockerImageTag())
        .documentationUrl(new URI(source.getDocumentationUrl()));

    final SourceDefinitionIdRequestBody sourceDefinitionIdRequestBody =
        new SourceDefinitionIdRequestBody().sourceDefinitionId(source.getSourceDefinitionId());

    final SourceDefinitionRead actualSourceDefinitionRead = sourceHandler.getSourceDefinition(sourceDefinitionIdRequestBody);

    assertEquals(expectedSourceDefinitionRead, actualSourceDefinitionRead);
  }

  @Test
  void testCreateSourceDefinition() throws URISyntaxException, ConfigNotFoundException, IOException, JsonValidationException {
    final StandardSourceDefinition source = generateSource();
    when(uuidSupplier.get()).thenReturn(source.getSourceDefinitionId());
    final SourceDefinitionCreate create = new SourceDefinitionCreate()
        .name(source.getName())
        .dockerRepository(source.getDockerRepository())
        .dockerImageTag(source.getDockerImageTag())
        .documentationUrl(new URI(source.getDocumentationUrl()));

    final SourceDefinitionRead expectedRead = new SourceDefinitionRead()
        .name(source.getName())
        .dockerRepository(source.getDockerRepository())
        .dockerImageTag(source.getDockerImageTag())
        .documentationUrl(new URI(source.getDocumentationUrl()))
        .sourceDefinitionId(source.getSourceDefinitionId());

    final SourceDefinitionRead actualRead = sourceHandler.createSourceDefinition(create);

    assertEquals(expectedRead, actualRead);
    verify(dockerImageValidator).assertValidIntegrationImage(source.getDockerRepository(), source.getDockerImageTag());
  }

  @Test
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
    verify(schedulerJobClient).resetCache();
  }

}
