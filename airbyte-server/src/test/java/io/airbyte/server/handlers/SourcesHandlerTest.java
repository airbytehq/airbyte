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
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.google.common.collect.Lists;
import io.airbyte.api.model.SourceCreate;
import io.airbyte.api.model.SourceIdRequestBody;
import io.airbyte.api.model.SourceRead;
import io.airbyte.api.model.SourceReadList;
import io.airbyte.api.model.SourceUpdate;
import io.airbyte.config.StandardSource;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.server.validators.DockerImageValidator;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.net.URI;
import java.net.URISyntaxException;
import java.util.UUID;
import java.util.function.Supplier;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class SourcesHandlerTest {

  private ConfigRepository configRepository;
  private DockerImageValidator dockerImageValidator;
  private StandardSource source;
  private SourcesHandler sourceHandler;
  private Supplier<UUID> uuidSupplier;

  @SuppressWarnings("unchecked")
  @BeforeEach
  void setUp() {
    configRepository = mock(ConfigRepository.class);
    uuidSupplier = mock(Supplier.class);
    dockerImageValidator = mock(DockerImageValidator.class);

    source = generateSource();
    sourceHandler = new SourcesHandler(configRepository, dockerImageValidator, uuidSupplier);
  }

  private StandardSource generateSource() {
    final UUID sourceId = UUID.randomUUID();

    return new StandardSource()
        .withSourceId(sourceId)
        .withName("presto")
        .withDocumentationUrl("https://netflix.com")
        .withDockerRepository("dockerstuff")
        .withDockerImageTag("12.3");
  }

  @Test
  void testListSources() throws JsonValidationException, IOException, ConfigNotFoundException, URISyntaxException {
    final StandardSource source2 = generateSource();

    when(configRepository.listStandardSources()).thenReturn(Lists.newArrayList(source, source2));

    SourceRead expectedSourceRead1 = new SourceRead()
        .sourceId(source.getSourceId())
        .name(source.getName())
        .dockerRepository(source.getDockerRepository())
        .dockerImageTag(source.getDockerImageTag())
        .documentationUrl(new URI(source.getDocumentationUrl()));

    SourceRead expectedSourceRead2 = new SourceRead()
        .sourceId(source2.getSourceId())
        .name(source2.getName())
        .dockerRepository(source.getDockerRepository())
        .dockerImageTag(source.getDockerImageTag())
        .documentationUrl(new URI(source.getDocumentationUrl()));

    final SourceReadList actualSourceReadList = sourceHandler.listSources();

    assertEquals(Lists.newArrayList(expectedSourceRead1, expectedSourceRead2), actualSourceReadList.getSources());
  }

  @Test
  void testGetSource() throws JsonValidationException, ConfigNotFoundException, IOException, URISyntaxException {
    when(configRepository.getStandardSource(source.getSourceId()))
        .thenReturn(source);

    SourceRead expectedSourceRead = new SourceRead()
        .sourceId(source.getSourceId())
        .name(source.getName())
        .dockerRepository(source.getDockerRepository())
        .dockerImageTag(source.getDockerImageTag())
        .documentationUrl(new URI(source.getDocumentationUrl()));

    final SourceIdRequestBody sourceIdRequestBody = new SourceIdRequestBody().sourceId(source.getSourceId());

    final SourceRead actualSourceRead = sourceHandler.getSource(sourceIdRequestBody);

    assertEquals(expectedSourceRead, actualSourceRead);
  }

  @Test
  void testCreateSource() throws URISyntaxException, ConfigNotFoundException, IOException, JsonValidationException {
    final StandardSource source = generateSource();
    when(uuidSupplier.get()).thenReturn(source.getSourceId());
    final SourceCreate create = new SourceCreate()
        .name(source.getName())
        .dockerRepository(source.getDockerRepository())
        .dockerImageTag(source.getDockerImageTag())
        .documentationUrl(new URI(source.getDocumentationUrl()));

    final SourceRead expectedRead = new SourceRead()
        .name(source.getName())
        .dockerRepository(source.getDockerRepository())
        .dockerImageTag(source.getDockerImageTag())
        .documentationUrl(new URI(source.getDocumentationUrl()))
        .sourceId(source.getSourceId());

    final SourceRead actualRead = sourceHandler.createSource(create);

    assertEquals(expectedRead, actualRead);
    verify(dockerImageValidator).assertValidIntegrationImage(source.getDockerRepository(), source.getDockerImageTag());
  }

  @Test
  void testUpdateSource() throws ConfigNotFoundException, IOException, JsonValidationException {
    when(configRepository.getStandardSource(source.getSourceId())).thenReturn(source);
    final String newDockerImageTag = "averydifferenttag";
    final String currentTag = sourceHandler.getSource(new SourceIdRequestBody().sourceId(source.getSourceId())).getDockerImageTag();
    assertNotEquals(newDockerImageTag, currentTag);

    SourceRead sourceRead = sourceHandler.updateSource(new SourceUpdate().sourceId(source.getSourceId()).dockerImageTag(newDockerImageTag));

    assertEquals(newDockerImageTag, sourceRead.getDockerImageTag());
    verify(dockerImageValidator).assertValidIntegrationImage(source.getDockerRepository(), newDockerImageTag);
  }

}
