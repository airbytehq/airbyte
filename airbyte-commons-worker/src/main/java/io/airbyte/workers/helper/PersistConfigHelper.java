/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.helper;

import com.google.common.hash.Hashing;
import io.airbyte.api.client.AirbyteApiClient;
import io.airbyte.api.client.generated.DestinationApi;
import io.airbyte.api.client.generated.JobsApi;
import io.airbyte.api.client.generated.SourceApi;
import io.airbyte.api.client.invoker.generated.ApiClient;
import io.airbyte.api.client.invoker.generated.ApiException;
import io.airbyte.api.client.model.generated.ConnectionIdRequestBody;
import io.airbyte.api.client.model.generated.ConnectionRead;
import io.airbyte.api.client.model.generated.DestinationIdRequestBody;
import io.airbyte.api.client.model.generated.DestinationRead;
import io.airbyte.api.client.model.generated.DestinationUpdate;
import io.airbyte.api.client.model.generated.JobIdRequestBody;
import io.airbyte.api.client.model.generated.JobInfoLightRead;
import io.airbyte.api.client.model.generated.SourceIdRequestBody;
import io.airbyte.api.client.model.generated.SourceRead;
import io.airbyte.api.client.model.generated.SourceUpdate;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.Configs;
import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.EnvConfigs;
import io.airbyte.protocol.models.Config;
import java.nio.charset.StandardCharsets;
import java.util.UUID;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Helper class for workers to persist updates to Source/Destination configs emitted from
 * AirbyteControlMessages.
 */
public class PersistConfigHelper {

  private static final Logger LOGGER = LoggerFactory.getLogger(PersistConfigHelper.class);

  private static final Configs CONFIGS = new EnvConfigs();
  private static final AirbyteApiClient CLIENT = getAirbyteApiClient();

  // TODO inject this with micronaut, possibly making this class a Singleton
  private static AirbyteApiClient getAirbyteApiClient() {
    if (CONFIGS.getWorkerEnvironment() == WorkerEnvironment.DOCKER) {
      return new AirbyteApiClient(
          new ApiClient().setScheme("http")
              .setHost(CONFIGS.getAirbyteApiHost())
              .setPort(CONFIGS.getAirbyteApiPort())
              .setBasePath("/api"));
    }

    return new AirbyteApiClient(
        new ApiClient().setScheme("http")
            .setHost("airbyte-server-svc")
            .setPort(8001)
            .setBasePath("/api"));
  }

  private static UUID getConnectionIdFromJobId(final Long jobId) throws ApiException {
    final JobsApi jobsApi = CLIENT.getJobsApi();
    final JobIdRequestBody body = new JobIdRequestBody().id(jobId);
    final JobInfoLightRead jobInfo = jobsApi.getJobInfoLight(body);
    return UUID.fromString(jobInfo.getJob().getConfigId());
  }

  public static void persistSourceConfig(final Long jobId, final Config config) throws ApiException {
    final UUID connectionId = getConnectionIdFromJobId(jobId);

    final ConnectionRead connection = CLIENT.getConnectionApi().getConnection(new ConnectionIdRequestBody().connectionId(connectionId));
    final UUID sourceId = connection.getSourceId();

    final SourceApi sourceApi = CLIENT.getSourceApi();
    final SourceRead source = sourceApi.getSource(new SourceIdRequestBody().sourceId(sourceId));

    // TODO might need to strip out OAuth params

    final SourceRead updatedSource = sourceApi
        .updateSource(new SourceUpdate()
            .sourceId(sourceId)
            .name(source.getName())
            .connectionConfiguration(Jsons.jsonNode(config.getAdditionalProperties())));

    LOGGER.info("Persisted updated configuration for source {}. New config hash: {}.", sourceId,
        Hashing.sha256().hashString(updatedSource.getConnectionConfiguration().asText(), StandardCharsets.UTF_8));

  }

  public static void persistDestinationConfig(final Long jobId, final Config config) throws ApiException {
    final UUID connectionId = getConnectionIdFromJobId(jobId);

    final ConnectionRead connection = CLIENT.getConnectionApi().getConnection(new ConnectionIdRequestBody().connectionId(connectionId));
    final UUID destinationId = connection.getDestinationId();

    final DestinationApi destinationApi = CLIENT.getDestinationApi();
    final DestinationRead destination = destinationApi.getDestination(new DestinationIdRequestBody().destinationId(destinationId));

    // TODO might need to strip out OAuth params

    final DestinationRead updatedDestination = destinationApi
        .updateDestination(new DestinationUpdate()
            .destinationId(destinationId)
            .name(destination.getName())
            .connectionConfiguration(Jsons.jsonNode(config.getAdditionalProperties())));

    LOGGER.info("Persisted updated configuration for destination {}. New config hash: {}.", destinationId,
        Hashing.sha256().hashString(updatedDestination.getConnectionConfiguration().asText(), StandardCharsets.UTF_8));
  }

}
