/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server;

import io.airbyte.analytics.TrackingClient;
import io.airbyte.commons.io.FileTtlManager;
import io.airbyte.config.Configs;
import io.airbyte.config.persistence.ConfigPersistence;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.db.Database;
import io.airbyte.scheduler.client.CachingSynchronousSchedulerClient;
import io.airbyte.scheduler.client.SchedulerJobClient;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.server.apis.ConfigurationApi;
import io.temporal.serviceclient.WorkflowServiceStubs;
import java.util.Map;
import org.glassfish.hk2.api.Factory;
import org.slf4j.MDC;

public class ConfigurationApiFactory implements Factory<ConfigurationApi> {

  private static WorkflowServiceStubs temporalService;
  private static ConfigRepository configRepository;
  private static JobPersistence jobPersistence;
  private static ConfigPersistence seed;
  private static SchedulerJobClient schedulerJobClient;
  private static CachingSynchronousSchedulerClient synchronousSchedulerClient;
  private static Configs configs;
  private static FileTtlManager archiveTtlManager;
  private static Map<String, String> mdc;
  private static Database configsDatabase;
  private static Database jobsDatabase;
  private static TrackingClient trackingClient;

  public static void setValues(
                               final WorkflowServiceStubs temporalService,
                               final ConfigRepository configRepository,
                               final JobPersistence jobPersistence,
                               final ConfigPersistence seed,
                               final SchedulerJobClient schedulerJobClient,
                               final CachingSynchronousSchedulerClient synchronousSchedulerClient,
                               final Configs configs,
                               final FileTtlManager archiveTtlManager,
                               final Map<String, String> mdc,
                               final Database configsDatabase,
                               final Database jobsDatabase,
                               final TrackingClient trackingClient) {
    ConfigurationApiFactory.configRepository = configRepository;
    ConfigurationApiFactory.jobPersistence = jobPersistence;
    ConfigurationApiFactory.seed = seed;
    ConfigurationApiFactory.schedulerJobClient = schedulerJobClient;
    ConfigurationApiFactory.synchronousSchedulerClient = synchronousSchedulerClient;
    ConfigurationApiFactory.configs = configs;
    ConfigurationApiFactory.archiveTtlManager = archiveTtlManager;
    ConfigurationApiFactory.mdc = mdc;
    ConfigurationApiFactory.temporalService = temporalService;
    ConfigurationApiFactory.configsDatabase = configsDatabase;
    ConfigurationApiFactory.jobsDatabase = jobsDatabase;
    ConfigurationApiFactory.trackingClient = trackingClient;
  }

  @Override
  public ConfigurationApi provide() {
    MDC.setContextMap(ConfigurationApiFactory.mdc);

    return new ConfigurationApi(
        ConfigurationApiFactory.configRepository,
        ConfigurationApiFactory.jobPersistence,
        ConfigurationApiFactory.seed,
        ConfigurationApiFactory.schedulerJobClient,
        ConfigurationApiFactory.synchronousSchedulerClient,
        ConfigurationApiFactory.configs,
        ConfigurationApiFactory.archiveTtlManager,
        ConfigurationApiFactory.temporalService,
        ConfigurationApiFactory.configsDatabase,
        ConfigurationApiFactory.jobsDatabase,
        ConfigurationApiFactory.trackingClient);
  }

  @Override
  public void dispose(final ConfigurationApi service) {
    /* noop */
  }

}
