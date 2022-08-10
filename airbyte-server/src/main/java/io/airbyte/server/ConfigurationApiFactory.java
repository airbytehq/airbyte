/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server;

import io.airbyte.analytics.TrackingClient;
import io.airbyte.commons.io.FileTtlManager;
import io.airbyte.commons.version.AirbyteVersion;
import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.helpers.LogConfigs;
import io.airbyte.config.persistence.ConfigPersistence;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.SecretsRepositoryReader;
import io.airbyte.config.persistence.SecretsRepositoryWriter;
import io.airbyte.config.persistence.StatePersistence;
import io.airbyte.db.Database;
import io.airbyte.scheduler.client.EventRunner;
import io.airbyte.scheduler.client.SynchronousSchedulerClient;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.server.apis.ConfigurationApi;
import java.net.http.HttpClient;
import java.nio.file.Path;
import java.util.Map;
import org.flywaydb.core.Flyway;
import org.glassfish.hk2.api.Factory;
import org.slf4j.MDC;

public class ConfigurationApiFactory implements Factory<ConfigurationApi> {

  private static ConfigRepository configRepository;
  private static JobPersistence jobPersistence;
  private static ConfigPersistence seed;
  private static SecretsRepositoryReader secretsRepositoryReader;
  private static SecretsRepositoryWriter secretsRepositoryWriter;
  private static SynchronousSchedulerClient synchronousSchedulerClient;
  private static FileTtlManager archiveTtlManager;
  private static StatePersistence statePersistence;
  private static Map<String, String> mdc;
  private static Database configsDatabase;
  private static Database jobsDatabase;
  private static TrackingClient trackingClient;
  private static WorkerEnvironment workerEnvironment;
  private static LogConfigs logConfigs;
  private static Path workspaceRoot;
  private static AirbyteVersion airbyteVersion;
  private static HttpClient httpClient;
  private static EventRunner eventRunner;
  private static Flyway configsFlyway;
  private static Flyway jobsFlyway;

  public static void setValues(
                               final ConfigRepository configRepository,
                               final SecretsRepositoryReader secretsRepositoryReader,
                               final SecretsRepositoryWriter secretsRepositoryWriter,
                               final JobPersistence jobPersistence,
                               final ConfigPersistence seed,
                               final SynchronousSchedulerClient synchronousSchedulerClient,
                               final FileTtlManager archiveTtlManager,
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
    ConfigurationApiFactory.seed = seed;
    ConfigurationApiFactory.secretsRepositoryReader = secretsRepositoryReader;
    ConfigurationApiFactory.secretsRepositoryWriter = secretsRepositoryWriter;
    ConfigurationApiFactory.synchronousSchedulerClient = synchronousSchedulerClient;
    ConfigurationApiFactory.archiveTtlManager = archiveTtlManager;
    ConfigurationApiFactory.mdc = mdc;
    ConfigurationApiFactory.configsDatabase = configsDatabase;
    ConfigurationApiFactory.jobsDatabase = jobsDatabase;
    ConfigurationApiFactory.trackingClient = trackingClient;
    ConfigurationApiFactory.workerEnvironment = workerEnvironment;
    ConfigurationApiFactory.logConfigs = logConfigs;
    ConfigurationApiFactory.workspaceRoot = workspaceRoot;
    ConfigurationApiFactory.airbyteVersion = airbyteVersion;
    ConfigurationApiFactory.httpClient = httpClient;
    ConfigurationApiFactory.eventRunner = eventRunner;
    ConfigurationApiFactory.configsFlyway = configsFlyway;
    ConfigurationApiFactory.jobsFlyway = jobsFlyway;
    ConfigurationApiFactory.statePersistence = statePersistence;
  }

  @Override
  public ConfigurationApi provide() {
    MDC.setContextMap(ConfigurationApiFactory.mdc);

    return new ConfigurationApi(
        ConfigurationApiFactory.configRepository,
        ConfigurationApiFactory.jobPersistence,
        ConfigurationApiFactory.seed,
        ConfigurationApiFactory.secretsRepositoryReader,
        ConfigurationApiFactory.secretsRepositoryWriter,
        ConfigurationApiFactory.synchronousSchedulerClient,
        ConfigurationApiFactory.archiveTtlManager,
        ConfigurationApiFactory.configsDatabase,
        ConfigurationApiFactory.jobsDatabase,
        ConfigurationApiFactory.statePersistence,
        ConfigurationApiFactory.trackingClient,
        ConfigurationApiFactory.workerEnvironment,
        ConfigurationApiFactory.logConfigs,
        ConfigurationApiFactory.airbyteVersion,
        ConfigurationApiFactory.workspaceRoot,
        ConfigurationApiFactory.httpClient,
        ConfigurationApiFactory.eventRunner,
        ConfigurationApiFactory.configsFlyway,
        ConfigurationApiFactory.jobsFlyway);
  }

  @Override
  public void dispose(final ConfigurationApi service) {
    /* noop */
  }

}
