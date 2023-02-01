/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server;

import io.airbyte.analytics.TrackingClient;
import io.airbyte.commons.server.handlers.*;
import io.airbyte.commons.server.scheduler.EventRunner;
import io.airbyte.commons.server.scheduler.SynchronousSchedulerClient;
import io.airbyte.commons.version.AirbyteVersion;
import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.helpers.LogConfigs;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.SecretsRepositoryReader;
import io.airbyte.config.persistence.SecretsRepositoryWriter;
import io.airbyte.db.Database;
import io.airbyte.persistence.job.JobPersistence;
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
                        final DestinationHandler destinationHandler,
                        final HealthCheckHandler healthCheckHandler,
                        final JobHistoryHandler jobHistoryHandler,
                        final LogsHandler logsHandler,
                        final OAuthHandler ooAuthHandler,
                        final OpenApiConfigHandler openApiConfigHandler,
                        final OperationsHandler operationsHandler,
                        final SchedulerHandler schedulerHandler,
                        final SourceHandler sourceHandler,
                        final SourceDefinitionsHandler sourceDefinitionsHandler,
                        final StateHandler stateHandler,
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
                                 final DestinationHandler destinationHandler,
                                 final HealthCheckHandler healthCheckHandler,
                                 final JobHistoryHandler jobHistoryHandler,
                                 final LogsHandler logsHandler,
                                 final OAuthHandler ooAuthHandler,
                                 final OpenApiConfigHandler openApiConfigHandler,
                                 final OperationsHandler operationsHandler,
                                 final SchedulerHandler schedulerHandler,
                                 final SourceHandler sourceHandler,
                                 final SourceDefinitionsHandler sourceDefinitionsHandler,
                                 final StateHandler stateHandler,
                                 final WorkspacesHandler workspacesHandler,
                                 final WebBackendConnectionsHandler webBackendConnectionsHandler,
                                 final WebBackendGeographiesHandler webBackendGeographiesHandler,
                                 final WebBackendCheckUpdatesHandler webBackendCheckUpdatesHandler) {

      // construct server
      return new ServerApp(airbyteVersion, new HashSet<>(), new HashSet<>());
    }

  }

}
