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
import io.airbyte.server.apis.DbMigrationApiController;
import io.airbyte.server.apis.DestinationApiController;
import io.airbyte.server.apis.DestinationDefinitionApiController;
import io.airbyte.server.apis.DestinationDefinitionSpecificationApiController;
import io.airbyte.server.apis.DestinationOauthApiController;
import io.airbyte.server.apis.HealthApiController;
import io.airbyte.server.apis.JobsApiController;
import io.airbyte.server.apis.LogsApiController;
import io.airbyte.server.apis.NotificationsApiController;
import io.airbyte.server.apis.OpenapiApiController;
import io.airbyte.server.apis.OperationApiController;
import io.airbyte.server.apis.SchedulerApiController;
import io.airbyte.server.apis.SourceApiController;
import io.airbyte.server.apis.SourceDefinitionApiController;
import io.airbyte.server.apis.SourceOauthApiController;
import io.airbyte.server.apis.StateApiController;
import io.airbyte.server.apis.WebBackendApiController;
import io.airbyte.server.apis.WorkspaceApiController;
import io.airbyte.server.apis.binders.AttemptApiBinder;
import io.airbyte.server.apis.binders.ConnectionApiBinder;
import io.airbyte.server.apis.binders.DbMigrationBinder;
import io.airbyte.server.apis.binders.DestinationApiBinder;
import io.airbyte.server.apis.binders.DestinationDefinitionApiBinder;
import io.airbyte.server.apis.binders.DestinationDefinitionSpecificationApiBinder;
import io.airbyte.server.apis.binders.DestinationOauthApiBinder;
import io.airbyte.server.apis.binders.HealthApiBinder;
import io.airbyte.server.apis.binders.JobsApiBinder;
import io.airbyte.server.apis.binders.LogsApiBinder;
import io.airbyte.server.apis.binders.NotificationApiBinder;
import io.airbyte.server.apis.binders.OpenapiApiBinder;
import io.airbyte.server.apis.binders.OperationApiBinder;
import io.airbyte.server.apis.binders.SchedulerApiBinder;
import io.airbyte.server.apis.binders.SourceApiBinder;
import io.airbyte.server.apis.binders.SourceDefinitionApiBinder;
import io.airbyte.server.apis.binders.SourceOauthApiBinder;
import io.airbyte.server.apis.binders.StateApiBinder;
import io.airbyte.server.apis.binders.WebBackendApiBinder;
import io.airbyte.server.apis.binders.WorkspaceApiBinder;
import io.airbyte.server.apis.factories.AttemptApiFactory;
import io.airbyte.server.apis.factories.ConnectionApiFactory;
import io.airbyte.server.apis.factories.DbMigrationApiFactory;
import io.airbyte.server.apis.factories.DestinationApiFactory;
import io.airbyte.server.apis.factories.DestinationDefinitionApiFactory;
import io.airbyte.server.apis.factories.DestinationDefinitionSpecificationApiFactory;
import io.airbyte.server.apis.factories.DestinationOauthApiFactory;
import io.airbyte.server.apis.factories.HealthApiFactory;
import io.airbyte.server.apis.factories.JobsApiFactory;
import io.airbyte.server.apis.factories.LogsApiFactory;
import io.airbyte.server.apis.factories.NotificationsApiFactory;
import io.airbyte.server.apis.factories.OpenapiApiFactory;
import io.airbyte.server.apis.factories.OperationApiFactory;
import io.airbyte.server.apis.factories.SchedulerApiFactory;
import io.airbyte.server.apis.factories.SourceApiFactory;
import io.airbyte.server.apis.factories.SourceDefinitionApiFactory;
import io.airbyte.server.apis.factories.SourceOauthApiFactory;
import io.airbyte.server.apis.factories.StateApiFactory;
import io.airbyte.server.apis.factories.WebBackendApiFactory;
import io.airbyte.server.apis.factories.WorkspaceApiFactory;
import io.airbyte.server.handlers.AttemptHandler;
import io.airbyte.server.handlers.ConnectionsHandler;
import io.airbyte.server.handlers.DbMigrationHandler;
import io.airbyte.server.handlers.DestinationDefinitionsHandler;
import io.airbyte.server.handlers.DestinationHandler;
import io.airbyte.server.handlers.HealthCheckHandler;
import io.airbyte.server.handlers.JobHistoryHandler;
import io.airbyte.server.handlers.LogsHandler;
import io.airbyte.server.handlers.OAuthHandler;
import io.airbyte.server.handlers.OpenApiConfigHandler;
import io.airbyte.server.handlers.OperationsHandler;
import io.airbyte.server.handlers.SchedulerHandler;
import io.airbyte.server.handlers.SourceDefinitionsHandler;
import io.airbyte.server.handlers.SourceHandler;
import io.airbyte.server.handlers.StateHandler;
import io.airbyte.server.handlers.WebBackendConnectionsHandler;
import io.airbyte.server.handlers.WebBackendGeographiesHandler;
import io.airbyte.server.handlers.WorkspacesHandler;
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
                        final DbMigrationHandler dbMigrationHandler,
                        final DestinationDefinitionsHandler destinationDefinitionsHandler,
                        final DestinationHandler destinationApiHandler,
                        final HealthCheckHandler healthCheckHandler,
                        final JobHistoryHandler jobHistoryHandler,
                        final LogsHandler logsHandler,
                        final OAuthHandler oAuthHandler,
                        final OpenApiConfigHandler openApiConfigHandler,
                        final OperationsHandler operationsHandler,
                        final SchedulerHandler schedulerHandler,
                        final SourceHandler sourceHandler,
                        final SourceDefinitionsHandler sourceDefinitionsHandler,
                        final StateHandler stateHandler,
                        final WorkspacesHandler workspacesHandler,
                        final WebBackendConnectionsHandler webBackendConnectionsHandler,
                        final WebBackendGeographiesHandler webBackendGeographiesHandler);

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
                                 final DbMigrationHandler dbMigrationHandler,
                                 final DestinationDefinitionsHandler destinationDefinitionsHandler,
                                 final DestinationHandler destinationApiHandler,
                                 final HealthCheckHandler healthCheckHandler,
                                 final JobHistoryHandler jobHistoryHandler,
                                 final LogsHandler logsHandler,
                                 final OAuthHandler oAuthHandler,
                                 final OpenApiConfigHandler openApiConfigHandler,
                                 final OperationsHandler operationsHandler,
                                 final SchedulerHandler schedulerHandler,
                                 final SourceHandler sourceHandler,
                                 final SourceDefinitionsHandler sourceDefinitionsHandler,
                                 final StateHandler stateHandler,
                                 final WorkspacesHandler workspacesHandler,
                                 final WebBackendConnectionsHandler webBackendConnectionsHandler,
                                 final WebBackendGeographiesHandler webBackendGeographiesHandler) {
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

      DbMigrationApiFactory.setValues(dbMigrationHandler, mdc);

      DestinationApiFactory.setValues(destinationApiHandler, schedulerHandler, mdc);

      DestinationDefinitionApiFactory.setValues(destinationDefinitionsHandler);

      DestinationDefinitionSpecificationApiFactory.setValues(schedulerHandler);

      HealthApiFactory.setValues(healthCheckHandler);

      DestinationOauthApiFactory.setValues(oAuthHandler);

      SourceOauthApiFactory.setValues(oAuthHandler);

      JobsApiFactory.setValues(jobHistoryHandler, schedulerHandler);

      LogsApiFactory.setValues(logsHandler);

      NotificationsApiFactory.setValues(workspacesHandler);

      OperationApiFactory.setValues(operationsHandler);

      OpenapiApiFactory.setValues(openApiConfigHandler);

      SchedulerApiFactory.setValues(schedulerHandler);

      SourceApiFactory.setValues(schedulerHandler, sourceHandler);

      SourceDefinitionApiFactory.setValues(sourceDefinitionsHandler);

      StateApiFactory.setValues(stateHandler);

      WebBackendApiFactory.setValues(webBackendConnectionsHandler, webBackendGeographiesHandler);

      WorkspaceApiFactory.setValues(workspacesHandler);

      // server configurations
      final Set<Class<?>> componentClasses = Set.of(
          ConfigurationApi.class,
          AttemptApiController.class,
          ConnectionApiController.class,
          DbMigrationApiController.class,
          DestinationApiController.class,
          DestinationDefinitionApiController.class,
          DestinationDefinitionSpecificationApiController.class,
          DestinationOauthApiController.class,
          HealthApiController.class,
          JobsApiController.class,
          LogsApiController.class,
          NotificationsApiController.class,
          OpenapiApiController.class,
          OperationApiController.class,
          SchedulerApiController.class,
          SourceApiController.class,
          SourceDefinitionApiController.class,
          SourceOauthApiController.class,
          StateApiController.class,
          WebBackendApiController.class,
          WorkspaceApiController.class);

      final Set<Object> components = Set.of(
          new CorsFilter(),
          new ConfigurationApiBinder(),
          new AttemptApiBinder(),
          new ConnectionApiBinder(),
          new DbMigrationBinder(),
          new DestinationApiBinder(),
          new DestinationDefinitionApiBinder(),
          new DestinationDefinitionSpecificationApiBinder(),
          new DestinationOauthApiBinder(),
          new HealthApiBinder(),
          new JobsApiBinder(),
          new LogsApiBinder(),
          new NotificationApiBinder(),
          new OpenapiApiBinder(),
          new OperationApiBinder(),
          new SchedulerApiBinder(),
          new SourceApiBinder(),
          new SourceDefinitionApiBinder(),
          new SourceOauthApiBinder(),
          new StateApiBinder(),
          new WebBackendApiBinder(),
          new WorkspaceApiBinder());

      // construct server
      return new ServerApp(airbyteVersion, componentClasses, components);
    }

  }

}
