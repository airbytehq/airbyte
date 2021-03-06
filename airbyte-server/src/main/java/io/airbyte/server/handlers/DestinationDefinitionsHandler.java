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
import com.google.common.annotations.VisibleForTesting;
import com.google.common.base.Preconditions;
import io.airbyte.api.model.DestinationDefinitionCreate;
import io.airbyte.api.model.DestinationDefinitionIdRequestBody;
import io.airbyte.api.model.DestinationDefinitionRead;
import io.airbyte.api.model.DestinationDefinitionReadList;
import io.airbyte.api.model.DestinationDefinitionUpdate;
import io.airbyte.commons.yaml.Yamls;
import io.airbyte.config.StandardDestinationDefinition;
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

public class DestinationDefinitionsHandler {

  private static final String DEFAULT_DESTINATION_DEFINITION_ID_NAME = "destinationDefinitionId";
  private static final String DEFAULT_LATEST_LIST_BASE_URL = "https://raw.githubusercontent.com";
  private static final String DESTINATION_DEFINITION_LIST_LOCATION_PATH =
      "/airbytehq/airbyte/master/airbyte-config/init/src/main/resources/seed/destination_definitions.yaml";

  private static final ObjectMapper mapper = new ObjectMapper();
  private static final HttpClient httpClient = HttpClient.newHttpClient();

  private final DockerImageValidator imageValidator;
  private final ConfigRepository configRepository;
  private final Supplier<UUID> uuidSupplier;
  private final CachingSchedulerJobClient schedulerJobClient;
  private final String latestListBaseUrl;

  public DestinationDefinitionsHandler(final ConfigRepository configRepository,
                                       final DockerImageValidator imageValidator,
                                       final CachingSchedulerJobClient schedulerJobClient) {
    this(configRepository, imageValidator, UUID::randomUUID, schedulerJobClient, DEFAULT_LATEST_LIST_BASE_URL);
  }

  @VisibleForTesting
  public DestinationDefinitionsHandler(final ConfigRepository configRepository,
                                       final DockerImageValidator imageValidator,
                                       final Supplier<UUID> uuidSupplier,
                                       final CachingSchedulerJobClient schedulerJobClient,
                                       final String latestListBaseUrl) {
    this.configRepository = configRepository;
    this.imageValidator = imageValidator;
    this.uuidSupplier = uuidSupplier;
    this.schedulerJobClient = schedulerJobClient;
    this.latestListBaseUrl = latestListBaseUrl;
  }

  private static DestinationDefinitionRead buildDestinationDefinitionRead(StandardDestinationDefinition standardDestinationDefinition) {
    try {
      return new DestinationDefinitionRead()
          .destinationDefinitionId(standardDestinationDefinition.getDestinationDefinitionId())
          .name(standardDestinationDefinition.getName())
          .dockerRepository(standardDestinationDefinition.getDockerRepository())
          .dockerImageTag(standardDestinationDefinition.getDockerImageTag())
          .documentationUrl(new URI(standardDestinationDefinition.getDocumentationUrl()));
    } catch (URISyntaxException | NullPointerException e) {
      throw new KnownException(500, "Unable to process retrieved latest destination definition list", e);
    }
  }

  private static List<StandardDestinationDefinition> toStandardDestinationDefinitions(Iterator<JsonNode> iter) {
    Iterable<JsonNode> iterable = () -> iter;
    var destDefList = new ArrayList<StandardDestinationDefinition>();
    for (JsonNode n : iterable) {
      try {
        var def = mapper.treeToValue(n, StandardDestinationDefinition.class);
        System.out.println(def);
        destDefList.add(def);
      } catch (JsonProcessingException e) {
        throw new KnownException(500, "Unable to process retrieved latest destination definition list", e);
      }
    }
    return destDefList;
  }

  public DestinationDefinitionReadList listDestinationDefinitions() throws ConfigNotFoundException, IOException, JsonValidationException {
    final List<DestinationDefinitionRead> reads = configRepository
        .listStandardDestinationDefinitions()
        .stream()
        .map(DestinationDefinitionsHandler::buildDestinationDefinitionRead)
        .collect(Collectors.toList());

    return new DestinationDefinitionReadList().destinationDefinitions(reads);
  }

  public DestinationDefinitionReadList listLatestDestinationDefinitions() throws ConfigNotFoundException, IOException, JsonValidationException {
    final JsonNode deserialize;
    try {
      deserialize = Yamls.deserialize(getLatestDestinationsList());
      checkYamlIsPresentWithNoDuplicates(deserialize);
    } catch (RuntimeException e) {
      throw new KnownException(500, "Error retrieving latest destination definition", e);
    }

    final var destDefs = toStandardDestinationDefinitions(deserialize.elements());
    final var reads = destDefs.stream()
        .map(DestinationDefinitionsHandler::buildDestinationDefinitionRead).collect(Collectors.toList());
    return new DestinationDefinitionReadList().destinationDefinitions(reads);
  }

  private String getLatestDestinationsList() {
    final var request = HttpRequest
        .newBuilder(URI.create(latestListBaseUrl + DESTINATION_DEFINITION_LIST_LOCATION_PATH))
        .header("accept", "application/json")
        .build();
    final var future = httpClient.sendAsync(request, BodyHandlers.ofString());
    try {
      final var resp = future.get(1, TimeUnit.SECONDS);
      return resp.body();
    } catch (TimeoutException | InterruptedException | ExecutionException e) {
      throw new KnownException(500, "Request to retrieve latest destination definition failed", e);
    }
  }

  private void checkYamlIsPresentWithNoDuplicates(JsonNode deserialize) {
    final var presentDestList = !deserialize.elements().equals(ClassUtil.emptyIterator());
    Preconditions.checkState(presentDestList, "Destination definition list is empty");
    SeedRepository.checkNoDuplicateNames(deserialize.elements());
    SeedRepository.checkNoDuplicateIds(deserialize.elements(), DEFAULT_DESTINATION_DEFINITION_ID_NAME);
  }

  public DestinationDefinitionRead getDestinationDefinition(DestinationDefinitionIdRequestBody destinationDefinitionIdRequestBody)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    return buildDestinationDefinitionRead(
        configRepository.getStandardDestinationDefinition(
            destinationDefinitionIdRequestBody.getDestinationDefinitionId()));
  }

  public DestinationDefinitionRead createDestinationDefinition(DestinationDefinitionCreate destinationDefinitionCreate)
      throws JsonValidationException, IOException {
    imageValidator.assertValidIntegrationImage(destinationDefinitionCreate.getDockerRepository(),
        destinationDefinitionCreate.getDockerImageTag());

    final UUID id = uuidSupplier.get();
    final StandardDestinationDefinition destinationDefinition = new StandardDestinationDefinition()
        .withDestinationDefinitionId(id)
        .withDockerRepository(destinationDefinitionCreate.getDockerRepository())
        .withDockerImageTag(destinationDefinitionCreate.getDockerImageTag())
        .withDocumentationUrl(destinationDefinitionCreate.getDocumentationUrl().toString())
        .withName(destinationDefinitionCreate.getName());

    configRepository.writeStandardDestinationDefinition(destinationDefinition);

    return buildDestinationDefinitionRead(destinationDefinition);
  }

  public DestinationDefinitionRead updateDestinationDefinition(DestinationDefinitionUpdate destinationDefinitionUpdate)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final StandardDestinationDefinition currentDestination = configRepository
        .getStandardDestinationDefinition(destinationDefinitionUpdate.getDestinationDefinitionId());
    imageValidator.assertValidIntegrationImage(currentDestination.getDockerRepository(),
        destinationDefinitionUpdate.getDockerImageTag());

    final StandardDestinationDefinition newDestination = new StandardDestinationDefinition()
        .withDestinationDefinitionId(currentDestination.getDestinationDefinitionId())
        .withDockerImageTag(destinationDefinitionUpdate.getDockerImageTag())
        .withDockerRepository(currentDestination.getDockerRepository())
        .withName(currentDestination.getName())
        .withDocumentationUrl(currentDestination.getDocumentationUrl());

    configRepository.writeStandardDestinationDefinition(newDestination);
    // we want to re-fetch the spec for updated definitions.
    schedulerJobClient.resetCache();
    return buildDestinationDefinitionRead(newDestination);
  }

}
