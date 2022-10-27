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
import io.airbyte.server.apis.AttemptApiController;
import io.airbyte.server.apis.ConfigurationApi;
import io.airbyte.server.apis.ConnectionApiController;
import io.airbyte.server.apis.DestinationApiController;
import io.airbyte.server.apis.binders.AttemptApiBinder;
import io.airbyte.server.apis.binders.ConnectionApiBinder;
import io.airbyte.server.apis.binders.DestinationApiBinder;
import io.airbyte.server.apis.factories.AttemptApiFactory;
import io.airbyte.server.apis.factories.ConnectionApiFactory;
import io.airbyte.server.apis.factories.DestinationApiFactory;
import io.airbyte.server.handlers.AttemptHandler;
import io.airbyte.server.handlers.ConnectionsHandler;
import io.airbyte.server.handlers.DestinationHandler;
import io.airbyte.server.handlers.OperationsHandler;
import io.airbyte.server.handlers.SchedulerHandler;
import io.airbyte.server.scheduler.EventRunner;
import io.airbyte.server.scheduler.SynchronousSchedulerClient;
import java.net.http.HttpClient;
import java.nio.file.Path;
import java.util.Map;
import java.util.Set;
import org.flywaydb.core.Flyway;
import org.slf4j.MDC;

public interface ServerFactory {

  ServerRunnable create(final SynchronousSchedulerClient synchronousSchedulerClient,
                        final ConfigRepository configRepository,
                        final SecretsRepositoryReader secretsRepositoryReader,
                        final SecretsRepositoryWriter secretsRepositoryWriter,
                        final JobPersistence jobPersistence,
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
                        final Flyway jobsFlyway,
                        final AttemptHandler attemptHandler,
                        final ConnectionsHandler connectionsHandler,
                        final DestinationHandler destinationApiHandler,
                        final OperationsHandler operationsHandler,
                        final SchedulerHandler schedulerHandler);

  class Api implements ServerFactory {

    @Override
    public ServerRunnable create(final SynchronousSchedulerClient synchronousSchedulerClient,
                                 final ConfigRepository configRepository,
                                 final SecretsRepositoryReader secretsRepositoryReader,
                                 final SecretsRepositoryWriter secretsRepositoryWriter,
                                 final JobPersistence jobPersistence,
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
                                 final Flyway jobsFlyway,
                                 final AttemptHandler attemptHandler,
                                 final ConnectionsHandler connectionsHandler,
                                 final DestinationHandler destinationApiHandler,
                                 final OperationsHandler operationsHandler,
                                 final SchedulerHandler schedulerHandler) {
      final Map<String, String> mdc = MDC.getCopyOfContextMap();

      // set static values for factory
      ConfigurationApiFactory.setValues(
          configRepository,
          secretsRepositoryReader,
          secretsRepositoryWriter,
          jobPersistence,
          synchronousSchedulerClient,
          new StatePersistence(configsDatabase),
          mdc,
          configsDatabase,
          jobsDatabase,
          trackingClient,
          workerEnvironment,
          logConfigs,
          airbyteVersion,
          workspaceRoot,
          httpClient,
          eventRunner,
          configsFlyway,
          jobsFlyway);

      AttemptApiFactory.setValues(attemptHandler, mdc);

      ConnectionApiFactory.setValues(
          connectionsHandler,
          operationsHandler,
          schedulerHandler,
          mdc);

      DestinationApiFactory.setValues(destinationApiHandler, schedulerHandler, mdc);

      // server configurations
      final Set<Class<?>> componentClasses = Set.of(ConfigurationApi.class, AttemptApiController.class, ConnectionApiController.class,
          DestinationApiController.class);
      final Set<Object> components = Set.of(new CorsFilter(), new ConfigurationApiBinder(), new AttemptApiBinder(), new ConnectionApiBinder(),
          new DestinationApiBinder());

      // construct server
      return new ServerApp(airbyteVersion, componentClasses, components);
    }

  }

}
