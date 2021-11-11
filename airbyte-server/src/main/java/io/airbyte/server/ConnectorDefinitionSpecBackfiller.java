/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server;

import com.google.api.client.util.Lists;
import com.google.common.annotations.VisibleForTesting;
import com.google.common.collect.ImmutableMap;
import io.airbyte.analytics.TrackingClient;
import io.airbyte.api.model.LogRead;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.Configs;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSync;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigPersistence;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.scheduler.client.SynchronousResponse;
import io.airbyte.scheduler.client.SynchronousSchedulerClient;
import io.airbyte.server.converters.JobConverter;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.List;
import java.util.Set;
import java.util.UUID;
import java.util.function.Function;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

// todo (lmossman) - delete this class after the faux major version bump, along with making the spec
// field required on the definition structs
public class ConnectorDefinitionSpecBackfiller {

  private static final Logger LOGGER = LoggerFactory.getLogger(ConnectorDefinitionSpecBackfiller.class);

  /**
   * Check that each spec in the database has a spec. If it doesn't, add it. If it can't be added,
   * delete the connector definition or fail according to the VERSION_0_31_0_FORCE_UPGRADE env var.
   * The goal is to try to end up in a state where all definitions in the db contain specs, or fail
   * otherwise.
   *
   * @param configRepository - access to the db
   * @param database - access to the db at a lower level (for deleting connections and syncs)
   * @param schedulerClient - scheduler client so that specs can be fetched as needed
   * @param trackingClient - tracking client for reporting failures to Segment
   * @param configs - for retrieving various configs (env vars, worker environment, logs)
   */
  @VisibleForTesting
  static void migrateAllDefinitionsToContainSpec(final ConfigRepository configRepository,
                                                 final ConfigPersistence database,
                                                 final ConfigPersistence seed,
                                                 final SynchronousSchedulerClient schedulerClient,
                                                 final TrackingClient trackingClient,
                                                 final Configs configs)
      throws IOException, JsonValidationException, ConfigNotFoundException {
    final List<String> failedBackfillImages = Lists.newArrayList();

    final JobConverter jobConverter = new JobConverter(configs.getWorkerEnvironment(), configs.getLogConfigs());

    final Set<String> connectorReposInUse = database.getConnectorReposInUse();

    final List<String> seedSourceRepos = seed.listConfigs(ConfigSchema.STANDARD_SOURCE_DEFINITION, StandardSourceDefinition.class)
        .stream()
        .map(StandardSourceDefinition::getDockerRepository)
        .collect(Collectors.toList());
    for (final StandardSourceDefinition sourceDef : configRepository.listStandardSourceDefinitions()) {
      final String imageName = sourceDef.getDockerRepository() + ":" + sourceDef.getDockerImageTag();
      try {
        if (sourceDef.getSpec() == null) {
          // if a source definition is not being used and is not in the seed, don't bother to attempt to fetch
          // a spec for it; just delete.
          if (!seedSourceRepos.contains(sourceDef.getDockerRepository()) && !connectorReposInUse.contains(sourceDef.getDockerRepository())) {
            LOGGER.info(
                "migrateAllDefinitionsToContainSpec - Source Definition {} does not have a spec, is not in the seed, and is not currently used in a connection. Deleting...",
                sourceDef.getName());
            deleteSourceDefinition(database, sourceDef.getSourceDefinitionId());
            continue;
          }

          LOGGER.info(
              "migrateAllDefinitionsToContainSpec - Source Definition {} does not have a spec. Attempting to retrieve spec...",
              sourceDef.getName());
          final SynchronousResponse<ConnectorSpecification> getSpecJob = schedulerClient
              .createGetSpecJob(imageName);
          if (getSpecJob.isSuccess()) {
            LOGGER.info(
                "migrateAllDefinitionsToContainSpec - Spec for Source Definition {} was successfully retrieved. Writing to the db...",
                sourceDef.getName());
            final StandardSourceDefinition updatedDef = Jsons.clone(sourceDef).withSpec(getSpecJob.getOutput());
            configRepository.writeStandardSourceDefinition(updatedDef);
            LOGGER.info(
                "migrateAllDefinitionsToContainSpec - Spec for Source Definition {} was successfully written to the db record.",
                sourceDef.getName());
          } else {
            final LogRead logRead = jobConverter.getLogRead(getSpecJob.getMetadata().getLogPath());
            LOGGER.info(
                "migrateAllDefinitionsToContainSpec - Failed to retrieve spec for Source Definition {}. Logs: {}",
                sourceDef.getName(),
                logRead.toString());
            throw new RuntimeException(String.format(
                "Failed to retrieve spec for Source Definition %s. Logs: %s",
                sourceDef.getName(),
                logRead.toString()));
          }
        }
      } catch (final Exception e) {
        trackSpecBackfillFailure(trackingClient, configRepository, sourceDef.getDockerRepository(), sourceDef.getDockerImageTag(), e);
        LOGGER.info("migrateAllDefinitionsToContainSpec - Failed to backfill spec into Source Definition {}. Error: {}", sourceDef.getName(), e);
        if (configs.getVersion31ForceUpgrade()) {
          LOGGER.info(
              "migrateAllDefinitionsToContainSpec - Force upgrade set to true. Deleting Source Definition {} and any associated connections/syncs...",
              sourceDef.getName());
          deleteSourceDefinition(database, sourceDef.getSourceDefinitionId());
        } else {
          failedBackfillImages.add(imageName);
        }
      }
    }

    final List<String> seedDestRepos = seed.listConfigs(ConfigSchema.STANDARD_DESTINATION_DEFINITION, StandardDestinationDefinition.class)
        .stream()
        .map(StandardDestinationDefinition::getDockerRepository)
        .collect(Collectors.toList());
    for (final StandardDestinationDefinition destDef : configRepository.listStandardDestinationDefinitions()) {
      final String imageName = destDef.getDockerRepository() + ":" + destDef.getDockerImageTag();
      try {
        if (destDef.getSpec() == null) {
          // if a source definition is not being used and is not in the seed, don't bother to attempt to fetch
          // a spec for it; just delete.
          if (!connectorReposInUse.contains(destDef.getDockerRepository()) && !seedDestRepos.contains(destDef.getDockerRepository())) {
            LOGGER.info(
                "migrateAllDefinitionsToContainSpec - Destination Definition {} does not have a spec, is not in the seed, and is not currently used in a connection. Deleting...",
                destDef.getName());
            deleteDestinationDefinition(database, destDef.getDestinationDefinitionId());
            continue;
          }

          LOGGER.info(
              "migrateAllDefinitionsToContainSpec - Destination Definition {} does not have a spec. Attempting to retrieve spec...",
              destDef.getName());
          final SynchronousResponse<ConnectorSpecification> getSpecJob = schedulerClient
              .createGetSpecJob(imageName);
          if (getSpecJob.isSuccess()) {
            LOGGER.info(
                "migrateAllDefinitionsToContainSpec - Spec for Destination Definition {} was successfully retrieved. Writing to the db...",
                destDef.getName());
            final StandardDestinationDefinition updatedDef = Jsons.clone(destDef).withSpec(getSpecJob.getOutput());
            configRepository.writeStandardDestinationDefinition(updatedDef);
            LOGGER.info(
                "migrateAllDefinitionsToContainSpec - Spec for Destination Definition {} was successfully written to the db record.",
                destDef.getName());
          } else {
            final LogRead logRead = jobConverter.getLogRead(getSpecJob.getMetadata().getLogPath());
            LOGGER.info(
                "migrateAllDefinitionsToContainSpec - Failed to retrieve spec for Destination Definition {}. Logs: {}",
                destDef.getName(),
                logRead.toString());
            throw new RuntimeException(String.format(
                "Failed to retrieve spec for Destination Definition %s. Logs: %s",
                destDef.getName(),
                logRead.toString()));
          }
        }
      } catch (final Exception e) {
        trackSpecBackfillFailure(trackingClient, configRepository, destDef.getDockerRepository(), destDef.getDockerImageTag(), e);
        LOGGER.info("migrateAllDefinitionsToContainSpec - Failed to backfill spec into Destination Definition {}. Error: {}", destDef.getName(), e);
        if (configs.getVersion31ForceUpgrade()) {
          LOGGER.info(
              "migrateAllDefinitionsToContainSpec - Force upgrade set to true. Deleting Destination Definition {} and any associated connections/syncs...",
              destDef.getName());
          deleteDestinationDefinition(database, destDef.getDestinationDefinitionId());
        } else {
          failedBackfillImages.add(imageName);
        }
      }
    }

    if (failedBackfillImages.size() > 0 && !configs.getVersion31ForceUpgrade()) {
      throw new RuntimeException(String.format(
          "migrateAllDefinitionsToContainSpec - Specs could not be retrieved for the following connector images: %s. Upgrading to version 0.31.0 "
              + "requires specs to be retrieved for all connector definitions, so you must either fix the images or restart the deployment with "
              + "the VERSION_0_31_0_FORCE_UPGRADE environment variable set to true, which will cause any connector definitions for which specs "
              + "cannot be retrieved to be deleted, as well as their associated connections/syncs.",
          failedBackfillImages.toString()));
    }
  }

  public static void deleteSourceDefinition(final ConfigPersistence configPersistence, final UUID sourceDefinitionId)
      throws JsonValidationException, ConfigNotFoundException, IOException {
    deleteConnectorDefinition(
        configPersistence,
        ConfigSchema.STANDARD_SOURCE_DEFINITION,
        ConfigSchema.SOURCE_CONNECTION,
        SourceConnection.class,
        SourceConnection::getSourceId,
        SourceConnection::getSourceDefinitionId,
        sourceDefinitionId);
  }

  public static void deleteDestinationDefinition(final ConfigPersistence configPersistence, final UUID destinationDefinitionId)
      throws JsonValidationException, ConfigNotFoundException, IOException {
    deleteConnectorDefinition(
        configPersistence,
        ConfigSchema.STANDARD_DESTINATION_DEFINITION,
        ConfigSchema.DESTINATION_CONNECTION,
        DestinationConnection.class,
        DestinationConnection::getDestinationId,
        DestinationConnection::getDestinationDefinitionId,
        destinationDefinitionId);
  }

  private static <T> void deleteConnectorDefinition(
                                                    final ConfigPersistence configPersistence,
                                                    final ConfigSchema definitionType,
                                                    final ConfigSchema connectorType,
                                                    final Class<T> connectorClass,
                                                    final Function<T, UUID> connectorIdGetter,
                                                    final Function<T, UUID> connectorDefinitionIdGetter,
                                                    final UUID definitionId)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    final Set<T> connectors = configPersistence.listConfigs(connectorType, connectorClass)
        .stream()
        .filter(connector -> connectorDefinitionIdGetter.apply(connector).equals(definitionId))
        .collect(Collectors.toSet());
    for (final T connector : connectors) {
      final Set<StandardSync> syncs = configPersistence.listConfigs(ConfigSchema.STANDARD_SYNC, StandardSync.class)
          .stream()
          .filter(sync -> sync.getSourceId().equals(connectorIdGetter.apply(connector))
              || sync.getDestinationId().equals(connectorIdGetter.apply(connector)))
          .collect(Collectors.toSet());

      for (final StandardSync sync : syncs) {
        configPersistence.deleteConfig(ConfigSchema.STANDARD_SYNC, sync.getConnectionId().toString());
      }
      configPersistence.deleteConfig(connectorType, connectorIdGetter.apply(connector).toString());
    }
    configPersistence.deleteConfig(definitionType, definitionId.toString());
  }

  private static void trackSpecBackfillFailure(final TrackingClient trackingClient,
                                               final ConfigRepository configRepository,
                                               final String dockerRepo,
                                               final String dockerImageTag,
                                               final Exception exception)
      throws JsonValidationException, IOException {
    // There is guaranteed to be at least one workspace, because the getServer() function enforces that
    final UUID workspaceId = configRepository.listStandardWorkspaces(true).get(0).getWorkspaceId();

    final ImmutableMap<String, Object> metadata = ImmutableMap.of(
        "docker_image_name", dockerRepo,
        "docker_image_tag", dockerImageTag,
        "exception", exception);
    trackingClient.track(workspaceId, "failed_spec_backfill", metadata);
  }

}
