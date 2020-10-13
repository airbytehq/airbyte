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

import io.airbyte.api.model.SourceCreate;
import io.airbyte.api.model.SourceIdRequestBody;
import io.airbyte.api.model.SourceRead;
import io.airbyte.api.model.SourceReadList;
import io.airbyte.api.model.SourceUpdate;
import io.airbyte.commons.docker.DockerUtils;
import io.airbyte.commons.json.JsonValidationException;
import io.airbyte.config.StandardSource;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.server.errors.KnownException;
import java.io.IOException;
import java.net.URI;
import java.net.URISyntaxException;
import java.util.List;
import java.util.UUID;
import java.util.function.Supplier;
import java.util.stream.Collectors;

import io.airbyte.server.validators.DockerImageValidator;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SourcesHandler {

  private static final Logger LOGGER = LoggerFactory.getLogger(SourcesHandler.class);

  private final DockerImageValidator imageValidator;
  private final ConfigRepository configRepository;
  private final Supplier<UUID> uuidSupplier;

  public SourcesHandler(final ConfigRepository configRepository, DockerImageValidator imageValidator) {
    this(configRepository, imageValidator, UUID::randomUUID);
  }

  public SourcesHandler(final ConfigRepository configRepository, DockerImageValidator imageValidator, Supplier<UUID> uuidSupplier) {
    this.configRepository = configRepository;
    this.uuidSupplier = uuidSupplier;
    this.imageValidator = imageValidator;
  }

  public SourceReadList listSources() throws ConfigNotFoundException, IOException, JsonValidationException {
    final List<SourceRead> reads = configRepository.listStandardSources()
        .stream()
        .map(SourcesHandler::buildSourceRead)
        .collect(Collectors.toList());
    return new SourceReadList().sources(reads);
  }

  public SourceRead getSource(SourceIdRequestBody sourceIdRequestBody) throws ConfigNotFoundException, IOException, JsonValidationException {
    return buildSourceRead(configRepository.getStandardSource(sourceIdRequestBody.getSourceId()));
  }

  public SourceRead createSource(SourceCreate sourceCreate) throws JsonValidationException, IOException {
    imageValidator.assertValidIntegrationImage(sourceCreate.getDockerRepository(), sourceCreate.getDockerImageTag());

    UUID id = uuidSupplier.get();
    StandardSource source = new StandardSource()
        .withSourceId(id)
        .withDockerRepository(sourceCreate.getDockerRepository())
        .withDockerImageTag(sourceCreate.getDockerImageTag())
        .withDocumentationUrl(sourceCreate.getDocumentationUrl().toString())
        .withName(sourceCreate.getName());

    configRepository.writeStandardSource(source);

    return buildSourceRead(source);
  }

  public SourceRead updateSource(SourceUpdate sourceUpdate) throws ConfigNotFoundException, IOException, JsonValidationException {
    StandardSource currentSource = configRepository.getStandardSource(sourceUpdate.getSourceId());
    imageValidator.assertValidIntegrationImage(currentSource.getDockerRepository(), sourceUpdate.getDockerImageTag());

    StandardSource newSource = new StandardSource()
        .withSourceId(currentSource.getSourceId())
        .withDockerImageTag(sourceUpdate.getDockerImageTag())
        .withDockerRepository(currentSource.getDockerRepository())
        .withDocumentationUrl(currentSource.getDocumentationUrl())
        .withName(currentSource.getName());

    configRepository.writeStandardSource(newSource);
    return buildSourceRead(newSource);
  }

  private static SourceRead buildSourceRead(StandardSource standardSource) {
    try {
      return new SourceRead()
          .sourceId(standardSource.getSourceId())
          .name(standardSource.getName())
          .dockerRepository(standardSource.getDockerRepository())
          .dockerImageTag(standardSource.getDockerImageTag())
          .documentationUrl(new URI(standardSource.getDocumentationUrl()));
    } catch (URISyntaxException e) {
      throw new RuntimeException(e);
    }
  }

}
