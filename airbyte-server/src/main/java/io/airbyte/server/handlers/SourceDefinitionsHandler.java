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

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.util.ClassUtil;
import com.google.common.base.Preconditions;
import io.airbyte.api.model.SourceDefinitionCreate;
import io.airbyte.api.model.SourceDefinitionIdRequestBody;
import io.airbyte.api.model.SourceDefinitionRead;
import io.airbyte.api.model.SourceDefinitionReadList;
import io.airbyte.api.model.SourceDefinitionUpdate;
import io.airbyte.commons.yaml.Yamls;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.init.SeedRepository;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.scheduler.client.CachingSchedulerJobClient;
import io.airbyte.server.errors.KnownException;
import io.airbyte.server.validators.DockerImageValidator;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.net.URI;
import java.net.URISyntaxException;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse.BodyHandlers;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import java.util.function.Supplier;
import java.util.stream.Collectors;

public class SourceDefinitionsHandler {

  private static final String DEFAULT_SOURCE_DEFINITION_ID_NAME = "sourceDefinitionId";
  private static final String DEFAULT_LATEST_LIST_BASE_URL = "https://raw.githubusercontent.com";
  private static final String SOURCE_DEFINITION_LIST_LOCATION_PATH =
      "/airbytehq/airbyte/master/airbyte-config/init/src/main/resources/seed/source_definitions.yaml";

  private static final ObjectMapper mapper = new ObjectMapper();
  private static final HttpClient httpClient = HttpClient.newHttpClient();

  private final DockerImageValidator imageValidator;
  private final ConfigRepository configRepository;
  private final Supplier<UUID> uuidSupplier;
  private final CachingSchedulerJobClient schedulerJobClient;
  private final String latestListBaseUrl;

  public SourceDefinitionsHandler(
                                  final ConfigRepository configRepository,
                                  final DockerImageValidator imageValidator,
                                  final CachingSchedulerJobClient schedulerJobClient) {
    this(configRepository, imageValidator, UUID::randomUUID, schedulerJobClient, DEFAULT_LATEST_LIST_BASE_URL);
  }

  public SourceDefinitionsHandler(
                                  final ConfigRepository configRepository,
                                  final DockerImageValidator imageValidator,
                                  final Supplier<UUID> uuidSupplier,
                                  final CachingSchedulerJobClient schedulerJobClient,
                                  final String latestListBaseUrl) {
    this.configRepository = configRepository;
    this.uuidSupplier = uuidSupplier;
    this.imageValidator = imageValidator;
    this.schedulerJobClient = schedulerJobClient;
    this.latestListBaseUrl = latestListBaseUrl;
  }

  private static SourceDefinitionRead buildSourceDefinitionRead(StandardSourceDefinition standardSourceDefinition) {
    try {
      return new SourceDefinitionRead()
          .sourceDefinitionId(standardSourceDefinition.getSourceDefinitionId())
          .name(standardSourceDefinition.getName())
          .dockerRepository(standardSourceDefinition.getDockerRepository())
          .dockerImageTag(standardSourceDefinition.getDockerImageTag())
          .documentationUrl(new URI(standardSourceDefinition.getDocumentationUrl()));
    } catch (URISyntaxException | NullPointerException e) {
      throw new KnownException(500, "Unable to process retrieved latest source definitions list", e);
    }
  }

  private static List<StandardSourceDefinition> toStandardSourceDefinitions(
      Iterator<JsonNode> iter) {
    Iterable<JsonNode> iterable = () -> iter;
    var sourceDefList = new ArrayList<StandardSourceDefinition>();
    for (JsonNode n : iterable) {
      try {
        var def = mapper.treeToValue(n, StandardSourceDefinition.class);
        sourceDefList.add(def);
      } catch (JsonProcessingException e) {
        throw new KnownException(500, "Unable to process retrieved latest source definitions list", e);
      }
    }
    return sourceDefList;
  }

  public SourceDefinitionReadList listSourceDefinitions() throws ConfigNotFoundException, IOException, JsonValidationException {
    final List<SourceDefinitionRead> reads = configRepository.listStandardSources()
        .stream()
        .map(SourceDefinitionsHandler::buildSourceDefinitionRead)
        .collect(Collectors.toList());
    return new SourceDefinitionReadList().sourceDefinitions(reads);
  }

  public SourceDefinitionReadList listLatestSourceDefinitions() throws ConfigNotFoundException, IOException, JsonValidationException {
    final JsonNode deserialize;
    try {
      deserialize = Yamls.deserialize(getLatestSources());
      checkYamlIsPresentWithNoDuplicates(deserialize);
    } catch (RuntimeException e) {
      throw new KnownException(500, "Error retrieving latest source definitions", e);
    }

    final var sourceDefs = toStandardSourceDefinitions(deserialize.elements());
    final var reads = sourceDefs.stream()
        .map(SourceDefinitionsHandler::buildSourceDefinitionRead).collect(Collectors.toList());
    return new SourceDefinitionReadList().sourceDefinitions(reads);
  }

  private String getLatestSources() {
    final var request = HttpRequest
        .newBuilder(URI.create(latestListBaseUrl + SOURCE_DEFINITION_LIST_LOCATION_PATH))
        .header("accept", "application/json")
        .build();
    final var future = httpClient.sendAsync(request, BodyHandlers.ofString());
    try {
      final var resp = future.get(1, TimeUnit.SECONDS);
      return resp.body();
    } catch (TimeoutException | InterruptedException | ExecutionException e) {
      throw new KnownException(500, "Request to retrieve latest source definitions failed", e);
    }
  }

  private void checkYamlIsPresentWithNoDuplicates(JsonNode deserialize) {
    final var presentSourceList = !deserialize.elements().equals(ClassUtil.emptyIterator());
    Preconditions.checkState(presentSourceList, "Source definition list is empty");
    SeedRepository.checkNoDuplicateNames(deserialize.elements());
    SeedRepository.checkNoDuplicateIds(deserialize.elements(), DEFAULT_SOURCE_DEFINITION_ID_NAME);
  }

  public SourceDefinitionRead getSourceDefinition(SourceDefinitionIdRequestBody sourceDefinitionIdRequestBody)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    return buildSourceDefinitionRead(configRepository.getStandardSourceDefinition(sourceDefinitionIdRequestBody.getSourceDefinitionId()));
  }

  public SourceDefinitionRead createSourceDefinition(SourceDefinitionCreate sourceDefinitionCreate) throws JsonValidationException, IOException {
    imageValidator.assertValidIntegrationImage(sourceDefinitionCreate.getDockerRepository(), sourceDefinitionCreate.getDockerImageTag());

    final UUID id = uuidSupplier.get();
    final StandardSourceDefinition sourceDefinition = new StandardSourceDefinition()
        .withSourceDefinitionId(id)
        .withDockerRepository(sourceDefinitionCreate.getDockerRepository())
        .withDockerImageTag(sourceDefinitionCreate.getDockerImageTag())
        .withDocumentationUrl(sourceDefinitionCreate.getDocumentationUrl().toString())
        .withName(sourceDefinitionCreate.getName());

    configRepository.writeStandardSource(sourceDefinition);

    return buildSourceDefinitionRead(sourceDefinition);
  }

  public SourceDefinitionRead updateSourceDefinition(SourceDefinitionUpdate sourceDefinitionUpdate)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final StandardSourceDefinition currentSourceDefinition =
        configRepository.getStandardSourceDefinition(sourceDefinitionUpdate.getSourceDefinitionId());
    imageValidator.assertValidIntegrationImage(currentSourceDefinition.getDockerRepository(), sourceDefinitionUpdate.getDockerImageTag());

    final StandardSourceDefinition newSource = new StandardSourceDefinition()
        .withSourceDefinitionId(currentSourceDefinition.getSourceDefinitionId())
        .withDockerImageTag(sourceDefinitionUpdate.getDockerImageTag())
        .withDockerRepository(currentSourceDefinition.getDockerRepository())
        .withDocumentationUrl(currentSourceDefinition.getDocumentationUrl())
        .withName(currentSourceDefinition.getName());

    configRepository.writeStandardSource(newSource);
    // we want to re-fetch the spec for updated definitions.
    schedulerJobClient.resetCache();
    return buildSourceDefinitionRead(newSource);
  }

}
