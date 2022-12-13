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
import io.airbyte.db.Database;
import io.airbyte.persistence.job.JobPersistence;
import io.airbyte.server.handlers.AttemptHandler;
import io.airbyte.server.handlers.ConnectionsHandler;
import io.airbyte.server.handlers.DestinationDefinitionsHandler;
import io.airbyte.server.handlers.DestinationHandler;
import io.airbyte.server.handlers.HealthCheckHandler;
import io.airbyte.server.handlers.JobHistoryHandler;
import io.airbyte.server.handlers.LogsHandler;
import io.airbyte.server.handlers.OAuthHandler;
import io.airbyte.server.handlers.OperationsHandler;
import io.airbyte.server.handlers.SchedulerHandler;
import io.airbyte.server.handlers.SourceDefinitionsHandler;
import io.airbyte.server.handlers.SourceHandler;
import io.airbyte.server.handlers.WebBackendCheckUpdatesHandler;
import io.airbyte.server.handlers.WebBackendConnectionsHandler;
import io.airbyte.server.handlers.WebBackendGeographiesHandler;
import io.airbyte.server.handlers.WorkspacesHandler;
import io.airbyte.server.scheduler.EventRunner;
import io.airbyte.server.scheduler.SynchronousSchedulerClient;
import java.net.http.HttpClient;
import java.nio.file.Path;
import java.util.HashSet;
import org.flywaydb.core.Flyway;

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
                        final DestinationDefinitionsHandler destinationDefinitionsHandler,
                        final DestinationHandler destinationApiHandler,
                        final HealthCheckHandler healthCheckHandler,
                        final JobHistoryHandler jobHistoryHandler,
                        final LogsHandler logsHandler,
                        final OAuthHandler oAuthHandler,
                        final OperationsHandler operationsHandler,
                        final SchedulerHandler schedulerHandler,
                        final SourceHandler sourceHandler,
                        final SourceDefinitionsHandler sourceDefinitionsHandler,
                        final WorkspacesHandler workspacesHandler,
                        final WebBackendConnectionsHandler webBackendConnectionsHandler,
                        final WebBackendGeographiesHandler webBackendGeographiesHandler,
                        final WebBackendCheckUpdatesHandler webBackendCheckUpdatesHandler);

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
                                 final DestinationDefinitionsHandler destinationDefinitionsHandler,
                                 final DestinationHandler destinationApiHandler,
                                 final HealthCheckHandler healthCheckHandler,
                                 final JobHistoryHandler jobHistoryHandler,
                                 final LogsHandler logsHandler,
                                 final OAuthHandler oAuthHandler,
                                 final OperationsHandler operationsHandler,
                                 final SchedulerHandler schedulerHandler,
                                 final SourceHandler sourceHandler,
                                 final SourceDefinitionsHandler sourceDefinitionsHandler,
                                 final WorkspacesHandler workspacesHandler,
                                 final WebBackendConnectionsHandler webBackendConnectionsHandler,
                                 final WebBackendGeographiesHandler webBackendGeographiesHandler,
                                 final WebBackendCheckUpdatesHandler webBackendCheckUpdatesHandler) {

      // construct server
      return new ServerApp(airbyteVersion, new HashSet<>(), new HashSet<>());
    }

  }

}
