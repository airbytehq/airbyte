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

import io.airbyte.api.model.SourceDefinitionCreate;
import io.airbyte.api.model.SourceDefinitionIdRequestBody;
import io.airbyte.api.model.SourceDefinitionRead;
import io.airbyte.api.model.SourceDefinitionReadList;
import io.airbyte.api.model.SourceDefinitionUpdate;
import io.airbyte.config.StandardSource;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.server.validators.DockerImageValidator;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.net.URI;
import java.net.URISyntaxException;
import java.util.List;
import java.util.UUID;
import java.util.function.Supplier;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SourceDefinitionsHandler {

  private static final Logger LOGGER = LoggerFactory.getLogger(SourceDefinitionsHandler.class);

  private final DockerImageValidator imageValidator;
  private final ConfigRepository configRepository;
  private final Supplier<UUID> uuidSupplier;

  public SourceDefinitionsHandler(final ConfigRepository configRepository, DockerImageValidator imageValidator) {
    this(configRepository, imageValidator, UUID::randomUUID);
  }

  public SourceDefinitionsHandler(final ConfigRepository configRepository, DockerImageValidator imageValidator, Supplier<UUID> uuidSupplier) {
    this.configRepository = configRepository;
    this.uuidSupplier = uuidSupplier;
    this.imageValidator = imageValidator;
  }

  public SourceDefinitionReadList listSourceDefinitions() throws ConfigNotFoundException, IOException, JsonValidationException {
    final List<SourceDefinitionRead> reads = configRepository.listStandardSources()
        .stream()
        .map(SourceDefinitionsHandler::buildSourceDefinitionRead)
        .collect(Collectors.toList());
    return new SourceDefinitionReadList().sourceDefinitions(reads);
  }

  public SourceDefinitionRead getSourceDefinition(SourceDefinitionIdRequestBody sourceDefinitionIdRequestBody)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    return buildSourceDefinitionRead(configRepository.getStandardSource(sourceDefinitionIdRequestBody.getSourceDefinitionId()));
  }

  public SourceDefinitionRead createSourceDefinition(SourceDefinitionCreate sourceDefinitionCreate) throws JsonValidationException, IOException {
    imageValidator.assertValidIntegrationImage(sourceDefinitionCreate.getDockerRepository(), sourceDefinitionCreate.getDockerImageTag());

    UUID id = uuidSupplier.get();
    StandardSource sourceDefinition = new StandardSource()
        .withSourceId(id)
        .withDockerRepository(sourceDefinitionCreate.getDockerRepository())
        .withDockerImageTag(sourceDefinitionCreate.getDockerImageTag())
        .withDocumentationUrl(sourceDefinitionCreate.getDocumentationUrl().toString())
        .withName(sourceDefinitionCreate.getName());

    configRepository.writeStandardSource(sourceDefinition);

    return buildSourceDefinitionRead(sourceDefinition);
  }

  public SourceDefinitionRead updateSourceDefinition(SourceDefinitionUpdate sourceDefinitionUpdate)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    StandardSource currentSourceDefinition = configRepository.getStandardSource(sourceDefinitionUpdate.getSourceDefinitionId());
    imageValidator.assertValidIntegrationImage(currentSourceDefinition.getDockerRepository(), sourceDefinitionUpdate.getDockerImageTag());

    StandardSource newSource = new StandardSource()
        .withSourceId(currentSourceDefinition.getSourceId())
        .withDockerImageTag(sourceDefinitionUpdate.getDockerImageTag())
        .withDockerRepository(currentSourceDefinition.getDockerRepository())
        .withDocumentationUrl(currentSourceDefinition.getDocumentationUrl())
        .withName(currentSourceDefinition.getName());

    configRepository.writeStandardSource(newSource);
    return buildSourceDefinitionRead(newSource);
  }

  private static SourceDefinitionRead buildSourceDefinitionRead(StandardSource standardSource) {
    try {
      return new SourceDefinitionRead()
          .sourceDefinitionId(standardSource.getSourceId())
          .name(standardSource.getName())
          .dockerRepository(standardSource.getDockerRepository())
          .dockerImageTag(standardSource.getDockerImageTag())
          .documentationUrl(new URI(standardSource.getDocumentationUrl()));
    } catch (URISyntaxException e) {
      throw new RuntimeException(e);
    }
  }

}
