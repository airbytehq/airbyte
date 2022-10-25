/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis.factories;

import io.airbyte.analytics.TrackingClient;
import io.airbyte.commons.version.AirbyteVersion;
import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.helpers.LogConfigs;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.SecretsRepositoryReader;
import io.airbyte.config.persistence.SecretsRepositoryWriter;
import io.airbyte.config.persistence.StatePersistence;
import io.airbyte.persistence.job.JobPersistence;
import io.airbyte.server.apis.ConnectionApiController;
import io.airbyte.server.scheduler.EventRunner;
import io.airbyte.server.scheduler.SynchronousSchedulerClient;
import java.util.Map;
import org.glassfish.hk2.api.Factory;
import org.slf4j.MDC;

public class ConnectionApiFactory implements Factory<ConnectionApiController> {

  private static ConfigRepository configRepository;
  private static JobPersistence jobPersistence;
  private static TrackingClient trackingClient;
  private static EventRunner eventRunner;
  private static SecretsRepositoryReader secretsRepositoryReader;
  private static SecretsRepositoryWriter secretsRepositoryWriter;
  private static SynchronousSchedulerClient synchronousSchedulerClient;
  private static WorkerEnvironment workerEnvironment;
  private static LogConfigs logConfigs;
  private static StatePersistence statePersistence;
  private static AirbyteVersion airbyteVersion;
  private static Map<String, String> mdc;

  public static void setValues(final ConfigRepository configRepository,
                               final JobPersistence jobPersistence,
                               final TrackingClient trackingClient,
                               final EventRunner eventRunner,
                               final SecretsRepositoryReader secretsRepositoryReader,
                               final SecretsRepositoryWriter secretsRepositoryWriter,
                               final SynchronousSchedulerClient synchronousSchedulerClient,
                               final WorkerEnvironment workerEnvironment,
                               final LogConfigs logConfigs,
                               final StatePersistence statePersistence,
                               final AirbyteVersion airbyteVersion,
                               final Map<String, String> mdc) {
    ConnectionApiFactory.configRepository = configRepository;
    ConnectionApiFactory.jobPersistence = jobPersistence;
    ConnectionApiFactory.trackingClient = trackingClient;
    ConnectionApiFactory.eventRunner = eventRunner;
    ConnectionApiFactory.secretsRepositoryReader = secretsRepositoryReader;
    ConnectionApiFactory.secretsRepositoryWriter = secretsRepositoryWriter;
    ConnectionApiFactory.synchronousSchedulerClient = synchronousSchedulerClient;
    ConnectionApiFactory.workerEnvironment = workerEnvironment;
    ConnectionApiFactory.logConfigs = logConfigs;
    ConnectionApiFactory.statePersistence = statePersistence;
    ConnectionApiFactory.airbyteVersion = airbyteVersion;
    ConnectionApiFactory.mdc = mdc;
  }

  @Override
  public ConnectionApiController provide() {
    MDC.setContextMap(ConnectionApiFactory.mdc);

    return new ConnectionApiController(configRepository, jobPersistence, trackingClient, eventRunner, secretsRepositoryReader, secretsRepositoryWriter,
        synchronousSchedulerClient, workerEnvironment, logConfigs, statePersistence, airbyteVersion);
  }

  @Override
  public void dispose(final ConnectionApiController instance) {
    /* no op */
  }

}
