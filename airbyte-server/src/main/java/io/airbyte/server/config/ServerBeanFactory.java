/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.config;

import io.airbyte.analytics.Deployment;
import io.airbyte.analytics.TrackingClient;
import io.airbyte.analytics.TrackingClientSingleton;
import io.airbyte.commons.temporal.ConnectionManagerUtils;
import io.airbyte.commons.temporal.StreamResetRecordsHelper;
import io.airbyte.commons.temporal.TemporalClient;
import io.airbyte.commons.temporal.TemporalUtils;
import io.airbyte.commons.temporal.TemporalWorkflowUtils;
import io.airbyte.commons.temporal.config.WorkerMode;
import io.airbyte.config.Configs;
import io.airbyte.config.helpers.LogClientSingleton;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.SecretsRepositoryReader;
import io.airbyte.config.persistence.SecretsRepositoryWriter;
import io.airbyte.config.persistence.StatePersistence;
import io.airbyte.config.persistence.StreamResetPersistence;
import io.airbyte.config.persistence.split_secrets.SecretPersistence;
import io.airbyte.config.persistence.split_secrets.SecretsHydrator;
import io.airbyte.db.Database;
import io.airbyte.db.check.DatabaseCheckException;
import io.airbyte.persistence.job.DefaultJobPersistence;
import io.airbyte.persistence.job.JobPersistence;
import io.airbyte.persistence.job.WebUrlHelper;
import io.airbyte.persistence.job.WorkspaceHelper;
import io.airbyte.persistence.job.errorreporter.JobErrorReporter;
import io.airbyte.persistence.job.errorreporter.JobErrorReportingClient;
import io.airbyte.persistence.job.errorreporter.JobErrorReportingClientFactory;
import io.airbyte.persistence.job.factory.OAuthConfigSupplier;
import io.airbyte.persistence.job.tracker.JobTracker;
import io.airbyte.server.CorsFilter;
import io.airbyte.server.ServerApp;
import io.airbyte.server.ServerRunnable;
import io.airbyte.server.apis.AttemptApiController;
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
import io.airbyte.server.apis.SourceDefinitionSpecificationApiController;
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
import io.airbyte.server.apis.binders.SourceDefinitionSpecificationApiBinder;
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
import io.airbyte.server.apis.factories.SourceDefinitionSpecificationApiFactory;
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
import io.airbyte.server.scheduler.DefaultSynchronousSchedulerClient;
import io.airbyte.server.scheduler.EventRunner;
import io.airbyte.server.scheduler.TemporalEventRunner;
import io.airbyte.validation.json.JsonSchemaValidator;
import io.airbyte.workers.normalization.NormalizationRunnerFactory;
import io.micronaut.context.annotation.Factory;
import io.micronaut.context.annotation.Requires;
import io.temporal.serviceclient.WorkflowServiceStubs;
import jakarta.inject.Named;
import jakarta.inject.Singleton;
import java.io.IOException;
import java.net.http.HttpClient;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import org.flywaydb.core.Flyway;
import org.jooq.DSLContext;
import org.slf4j.MDC;

@Factory
public class ServerBeanFactory {

  @Singleton
  @Requires(env = WorkerMode.CONTROL_PLANE)
  @Named("componentClasses")
  public Set<Class<?>> componentClasses() {
    return Set.of(
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
        SourceDefinitionSpecificationApiController.class,
        SourceOauthApiController.class,
        StateApiController.class,
        WebBackendApiController.class,
        WorkspaceApiController.class);
  }

  @Singleton
  @Requires(env = WorkerMode.CONTROL_PLANE)
  @Named("components")
  public Set<Object> components() {
    return Set.of(
        new CorsFilter(),
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
        new SourceDefinitionSpecificationApiBinder(),
        new SourceOauthApiBinder(),
        new StateApiBinder(),
        new WebBackendApiBinder(),
        new WorkspaceApiBinder());
  }

  @Singleton
  @Requires(env = WorkerMode.CONTROL_PLANE)
  @Named("serverRunnable")
  public ServerRunnable serverRunnable(
                                       @Named("componentClasses") final Set<Class<?>> componentClasses,
                                       @Named("components") final Set<Object> components,
                                       final Configs configs,
                                       @Named("config") final DSLContext configsDslContext,
                                       @Named("configFlyway") final Flyway configsFlyway,
                                       @Named("jobs") final DSLContext jobsDslContext,
                                       @Named("jobsFlyway") final Flyway jobsFlyway)
      throws DatabaseCheckException, IOException {
    LogClientSingleton.getInstance().setWorkspaceMdc(
        configs.getWorkerEnvironment(),
        configs.getLogConfigs(),
        LogClientSingleton.getInstance().getServerLogsRoot(configs.getWorkspaceRoot()));

    ServerApp.assertDatabasesReady(configs, configsDslContext, configsFlyway, jobsDslContext, jobsFlyway);

    final Database configsDatabase = new Database(configsDslContext);
    final SecretsHydrator secretsHydrator = SecretPersistence.getSecretsHydrator(configsDslContext, configs);
    final Optional<SecretPersistence> secretPersistence = SecretPersistence.getLongLived(configsDslContext, configs);
    final Optional<SecretPersistence> ephemeralSecretPersistence = SecretPersistence.getEphemeral(configsDslContext, configs);
    final ConfigRepository configRepository = new ConfigRepository(configsDatabase);
    final SecretsRepositoryReader secretsRepositoryReader = new SecretsRepositoryReader(configRepository, secretsHydrator);
    final SecretsRepositoryWriter secretsRepositoryWriter =
        new SecretsRepositoryWriter(configRepository, secretPersistence, ephemeralSecretPersistence);

    final Database jobsDatabase = new Database(jobsDslContext);
    final JobPersistence jobPersistence = new DefaultJobPersistence(jobsDatabase);

    TrackingClientSingleton.initialize(
        configs.getTrackingStrategy(),
        new Deployment(configs.getDeploymentMode(), jobPersistence.getDeployment().orElseThrow(), configs.getWorkerEnvironment()),
        configs.getAirbyteRole(),
        configs.getAirbyteVersion(),
        configRepository);

    final TrackingClient trackingClient = TrackingClientSingleton.get();
    final JobTracker jobTracker = new JobTracker(configRepository, jobPersistence, trackingClient);

    final WebUrlHelper webUrlHelper = new WebUrlHelper(configs.getWebappUrl());
    final JobErrorReportingClient jobErrorReportingClient = JobErrorReportingClientFactory.getClient(configs.getJobErrorReportingStrategy(), configs);
    final JobErrorReporter jobErrorReporter =
        new JobErrorReporter(
            configRepository,
            configs.getDeploymentMode(),
            configs.getAirbyteVersionOrWarning(),
            NormalizationRunnerFactory.BASE_NORMALIZATION_IMAGE_NAME,
            NormalizationRunnerFactory.NORMALIZATION_VERSION,
            webUrlHelper,
            jobErrorReportingClient);

    final TemporalUtils temporalUtils = new TemporalUtils(
        configs.getTemporalCloudClientCert(),
        configs.getTemporalCloudClientKey(),
        configs.temporalCloudEnabled(),
        configs.getTemporalCloudHost(),
        configs.getTemporalCloudNamespace(),
        configs.getTemporalHost(),
        configs.getTemporalRetentionInDays());

    final StreamResetPersistence streamResetPersistence = new StreamResetPersistence(configsDatabase);
    final WorkflowServiceStubs temporalService = temporalUtils.createTemporalService();
    final ConnectionManagerUtils connectionManagerUtils = new ConnectionManagerUtils();
    final StreamResetRecordsHelper streamResetRecordsHelper = new StreamResetRecordsHelper(jobPersistence, streamResetPersistence);

    final TemporalClient temporalClient = new TemporalClient(
        configs.getWorkspaceRoot(),
        TemporalWorkflowUtils.createWorkflowClient(temporalService, temporalUtils.getNamespace()),
        temporalService,
        streamResetPersistence,
        connectionManagerUtils,
        streamResetRecordsHelper);

    final OAuthConfigSupplier oAuthConfigSupplier = new OAuthConfigSupplier(configRepository, trackingClient);
    final DefaultSynchronousSchedulerClient syncSchedulerClient =
        new DefaultSynchronousSchedulerClient(temporalClient, jobTracker, jobErrorReporter, oAuthConfigSupplier);
    final HttpClient httpClient = HttpClient.newBuilder().version(HttpClient.Version.HTTP_1_1).build();
    final EventRunner eventRunner = new TemporalEventRunner(temporalClient);

    final WorkspaceHelper workspaceHelper = new WorkspaceHelper(configRepository, jobPersistence);

    final JsonSchemaValidator schemaValidator = new JsonSchemaValidator();

    final AttemptHandler attemptHandler = new AttemptHandler(jobPersistence);

    final ConnectionsHandler connectionsHandler = new ConnectionsHandler(
        configRepository,
        workspaceHelper,
        trackingClient,
        eventRunner);

    final DestinationHandler destinationHandler = new DestinationHandler(
        configRepository,
        secretsRepositoryReader,
        secretsRepositoryWriter,
        schemaValidator,
        connectionsHandler);

    final OperationsHandler operationsHandler = new OperationsHandler(configRepository);

    final SchedulerHandler schedulerHandler = new SchedulerHandler(
        configRepository,
        secretsRepositoryReader,
        secretsRepositoryWriter,
        syncSchedulerClient,
        jobPersistence,
        configs.getWorkerEnvironment(),
        configs.getLogConfigs(),
        eventRunner,
        connectionsHandler);

    final DbMigrationHandler dbMigrationHandler = new DbMigrationHandler(configsDatabase, configsFlyway, jobsDatabase, jobsFlyway);

    final DestinationDefinitionsHandler destinationDefinitionsHandler = new DestinationDefinitionsHandler(configRepository, syncSchedulerClient,
        destinationHandler);

    final HealthCheckHandler healthCheckHandler = new HealthCheckHandler(configRepository);

    final OAuthHandler oAuthHandler = new OAuthHandler(configRepository, httpClient, trackingClient);

    final SourceHandler sourceHandler = new SourceHandler(
        configRepository,
        secretsRepositoryReader,
        secretsRepositoryWriter,
        schemaValidator,
        connectionsHandler);

    final SourceDefinitionsHandler sourceDefinitionsHandler = new SourceDefinitionsHandler(configRepository, syncSchedulerClient, sourceHandler);

    final JobHistoryHandler jobHistoryHandler = new JobHistoryHandler(
        jobPersistence,
        configs.getWorkerEnvironment(),
        configs.getLogConfigs(),
        connectionsHandler,
        sourceHandler,
        sourceDefinitionsHandler,
        destinationHandler,
        destinationDefinitionsHandler,
        configs.getAirbyteVersion());

    final LogsHandler logsHandler = new LogsHandler(configs);

    final WorkspacesHandler workspacesHandler = new WorkspacesHandler(
        configRepository,
        secretsRepositoryWriter,
        connectionsHandler,
        destinationHandler,
        sourceHandler);

    final OpenApiConfigHandler openApiConfigHandler = new OpenApiConfigHandler();

    final StatePersistence statePersistence = new StatePersistence(configsDatabase);

    final StateHandler stateHandler = new StateHandler(statePersistence);

    final WebBackendConnectionsHandler webBackendConnectionsHandler = new WebBackendConnectionsHandler(
        connectionsHandler,
        stateHandler,
        sourceHandler,
        destinationHandler,
        jobHistoryHandler,
        schedulerHandler,
        operationsHandler,
        eventRunner,
        configRepository);

    final WebBackendGeographiesHandler webBackendGeographiesHandler = new WebBackendGeographiesHandler();

    final Map<String, String> mdc = MDC.getCopyOfContextMap();

    AttemptApiFactory.setValues(attemptHandler, mdc);

    ConnectionApiFactory.setValues(
        connectionsHandler,
        operationsHandler,
        schedulerHandler,
        mdc);

    DbMigrationApiFactory.setValues(dbMigrationHandler, mdc);

    DestinationApiFactory.setValues(destinationHandler, schedulerHandler, mdc);

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

    SourceDefinitionSpecificationApiFactory.setValues(schedulerHandler);

    StateApiFactory.setValues(stateHandler);

    WebBackendApiFactory.setValues(webBackendConnectionsHandler, webBackendGeographiesHandler);

    WorkspaceApiFactory.setValues(workspacesHandler);

    // construct server
    return new ServerApp(configs.getAirbyteVersion(), componentClasses, components);
  }

}
