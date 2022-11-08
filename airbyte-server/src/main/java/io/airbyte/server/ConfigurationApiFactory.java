/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server;

import io.airbyte.analytics.TrackingClient;
import io.airbyte.commons.version.AirbyteVersion;
import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.helpers.LogConfigs;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.SecretsRepositoryReader;
import io.airbyte.config.persistence.SecretsRepositoryWriter;
import io.airbyte.config.persistence.StatePersistence;
import io.airbyte.db.Database;
import io.airbyte.persistence.job.JobPersistence;
import io.airbyte.server.apis.ConfigurationApi;
import io.airbyte.server.scheduler.EventRunner;
import io.airbyte.server.scheduler.SynchronousSchedulerClient;
import java.net.http.HttpClient;
import java.nio.file.Path;
import java.util.Map;
import org.flywaydb.core.Flyway;
import org.glassfish.hk2.api.Factory;
import org.slf4j.MDC;

public class ConfigurationApiFactory implements Factory<ConfigurationApi> {

  private static ConfigRepository configRepository;
  private static JobPersistence jobPersistence;
  private static SecretsRepositoryReader secretsRepositoryReader;
  private static SecretsRepositoryWriter secretsRepositoryWriter;
  private static SynchronousSchedulerClient synchronousSchedulerClient;
  private static Map<String, String> mdc;
  private static TrackingClient trackingClient;
  private static WorkerEnvironment workerEnvironment;
  private static LogConfigs logConfigs;
  private static AirbyteVersion airbyteVersion;
  private static EventRunner eventRunner;

  public static void setValues(
                               final ConfigRepository configRepository,
                               final SecretsRepositoryReader secretsRepositoryReader,
                               final SecretsRepositoryWriter secretsRepositoryWriter,
                               final JobPersistence jobPersistence,
                               final SynchronousSchedulerClient synchronousSchedulerClient,
                               final StatePersistence statePersistence,
                               final Map<String, String> mdc,
                               final Database configsDatabase,
                               final Database jobsDatabase,
                               final TrackingClient trackingClient,
                               final WorkerEnvironment workerEnvironment,
                               final LogConfigs logConfigs,
                               final AirbyteVersion airbyteVersion,
                               final Path workspaceRoot,
                               final HttpClient httpClient,
                               final EventRunner eventRunner,
                               final Flyway configsFlyway,
                               final Flyway jobsFlyway) {
    ConfigurationApiFactory.configRepository = configRepository;
    ConfigurationApiFactory.jobPersistence = jobPersistence;
    ConfigurationApiFactory.secretsRepositoryReader = secretsRepositoryReader;
    ConfigurationApiFactory.secretsRepositoryWriter = secretsRepositoryWriter;
    ConfigurationApiFactory.synchronousSchedulerClient = synchronousSchedulerClient;
    ConfigurationApiFactory.mdc = mdc;
    ConfigurationApiFactory.trackingClient = trackingClient;
    ConfigurationApiFactory.workerEnvironment = workerEnvironment;
    ConfigurationApiFactory.logConfigs = logConfigs;
    ConfigurationApiFactory.airbyteVersion = airbyteVersion;
    ConfigurationApiFactory.eventRunner = eventRunner;
  }

  @Override
  public ConfigurationApi provide() {
    MDC.setContextMap(ConfigurationApiFactory.mdc);

    return new ConfigurationApi(
        ConfigurationApiFactory.configRepository,
        ConfigurationApiFactory.jobPersistence,
        ConfigurationApiFactory.secretsRepositoryReader,
        ConfigurationApiFactory.secretsRepositoryWriter,
        ConfigurationApiFactory.synchronousSchedulerClient,
        ConfigurationApiFactory.trackingClient,
        ConfigurationApiFactory.workerEnvironment,
        ConfigurationApiFactory.logConfigs,
        ConfigurationApiFactory.airbyteVersion,
        ConfigurationApiFactory.eventRunner);
  }

  @Override
  public void dispose(final ConfigurationApi service) {
    /* noop */
  }

}
