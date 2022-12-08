/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.config;

import io.airbyte.analytics.TrackingClient;
import io.airbyte.analytics.TrackingClientSingleton;
import io.airbyte.commons.temporal.TemporalClient;
import io.airbyte.config.EnvConfigs;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.SecretsRepositoryReader;
import io.airbyte.config.persistence.SecretsRepositoryWriter;
import io.airbyte.config.persistence.StreamResetPersistence;
import io.airbyte.config.persistence.split_secrets.SecretPersistence;
import io.airbyte.db.Database;
import io.airbyte.persistence.job.JobPersistence;
import io.airbyte.persistence.job.WorkspaceHelper;
import io.airbyte.server.handlers.ConnectionsHandler;
import io.airbyte.server.scheduler.EventRunner;
import io.airbyte.server.scheduler.TemporalEventRunner;
import io.airbyte.validation.json.JsonSchemaValidator;
import io.airbyte.workers.helper.ConnectionHelper;
import io.micronaut.context.annotation.Factory;
import jakarta.inject.Named;
import jakarta.inject.Singleton;
import org.jooq.DSLContext;

@Factory
public class WorkspaceApiFactory {

  @Singleton
  EnvConfigs envConfigs() {
    return new EnvConfigs();
  }

  @Singleton
  SecretsRepositoryWriter secretsRepositoryWriter(final ConfigRepository configRepository,
                                                  @Named("config") final DSLContext dslContext,
                                                  final EnvConfigs envConfigs) {
    return new SecretsRepositoryWriter(configRepository, SecretPersistence.getLongLived(dslContext, envConfigs),
        SecretPersistence.getEphemeral(dslContext, envConfigs));
  }

  @Singleton
  SecretsRepositoryReader secretsRepositoryReader(final ConfigRepository configRepository,
                                                  @Named("config") final DSLContext dslContext,
                                                  final EnvConfigs envConfigs) {
    return new SecretsRepositoryReader(configRepository, SecretPersistence.getSecretsHydrator(dslContext, envConfigs));

  }

  @Singleton
  ConnectionsHandler connectionsHandler(final ConfigRepository configRepository,
                                        final WorkspaceHelper workspaceHelper,
                                        final TrackingClient trackingClient,
                                        final EventRunner eventRunner,
                                        final ConnectionHelper connectionHelper) {
    return new ConnectionsHandler(configRepository, workspaceHelper, trackingClient, eventRunner, connectionHelper);
  }

  @Singleton
  WorkspaceHelper workspaceHelper(final ConfigRepository configRepository, final JobPersistence jobPersistence) {
    return new WorkspaceHelper(configRepository, jobPersistence);
  }

  @Singleton
  TrackingClient trackingClient() {
    return TrackingClientSingleton.get();
  }

  @Singleton
  EventRunner eventRunner(final TemporalClient temporalClient) {
    return new TemporalEventRunner(temporalClient);
  }

  @Singleton
  StreamResetPersistence streamResetPersistence(@Named("configDatabase") final Database configDb) {
    return new StreamResetPersistence(configDb);
  }

  @Singleton
  JsonSchemaValidator jsonSchemaValidator() {
    return new JsonSchemaValidator();
  }

}
