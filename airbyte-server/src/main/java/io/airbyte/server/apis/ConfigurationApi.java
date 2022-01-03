/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis;

import io.airbyte.analytics.TrackingClient;
import io.airbyte.api.model.CheckConnectionRead;
import io.airbyte.api.model.CheckOperationRead;
import io.airbyte.api.model.CompleteDestinationOAuthRequest;
import io.airbyte.api.model.CompleteSourceOauthRequest;
import io.airbyte.api.model.ConnectionCreate;
import io.airbyte.api.model.ConnectionIdRequestBody;
import io.airbyte.api.model.ConnectionRead;
import io.airbyte.api.model.ConnectionReadList;
import io.airbyte.api.model.ConnectionSearch;
import io.airbyte.api.model.ConnectionState;
import io.airbyte.api.model.ConnectionUpdate;
import io.airbyte.api.model.DbMigrationExecutionRead;
import io.airbyte.api.model.DbMigrationReadList;
import io.airbyte.api.model.DbMigrationRequestBody;
import io.airbyte.api.model.DestinationCoreConfig;
import io.airbyte.api.model.DestinationCreate;
import io.airbyte.api.model.DestinationDefinitionCreate;
import io.airbyte.api.model.DestinationDefinitionIdRequestBody;
import io.airbyte.api.model.DestinationDefinitionRead;
import io.airbyte.api.model.DestinationDefinitionReadList;
import io.airbyte.api.model.DestinationDefinitionSpecificationRead;
import io.airbyte.api.model.DestinationDefinitionUpdate;
import io.airbyte.api.model.DestinationIdRequestBody;
import io.airbyte.api.model.DestinationOauthConsentRequest;
import io.airbyte.api.model.DestinationRead;
import io.airbyte.api.model.DestinationReadList;
import io.airbyte.api.model.DestinationSearch;
import io.airbyte.api.model.DestinationUpdate;
import io.airbyte.api.model.HealthCheckRead;
import io.airbyte.api.model.ImportRead;
import io.airbyte.api.model.ImportRequestBody;
import io.airbyte.api.model.JobIdRequestBody;
import io.airbyte.api.model.JobInfoRead;
import io.airbyte.api.model.JobListRequestBody;
import io.airbyte.api.model.JobReadList;
import io.airbyte.api.model.LogsRequestBody;
import io.airbyte.api.model.Notification;
import io.airbyte.api.model.NotificationRead;
import io.airbyte.api.model.OAuthConsentRead;
import io.airbyte.api.model.OperationCreate;
import io.airbyte.api.model.OperationIdRequestBody;
import io.airbyte.api.model.OperationRead;
import io.airbyte.api.model.OperationReadList;
import io.airbyte.api.model.OperationUpdate;
import io.airbyte.api.model.OperatorConfiguration;
import io.airbyte.api.model.SetInstancewideDestinationOauthParamsRequestBody;
import io.airbyte.api.model.SetInstancewideSourceOauthParamsRequestBody;
import io.airbyte.api.model.SlugRequestBody;
import io.airbyte.api.model.SourceCoreConfig;
import io.airbyte.api.model.SourceCreate;
import io.airbyte.api.model.SourceDefinitionCreate;
import io.airbyte.api.model.SourceDefinitionIdRequestBody;
import io.airbyte.api.model.SourceDefinitionRead;
import io.airbyte.api.model.SourceDefinitionReadList;
import io.airbyte.api.model.SourceDefinitionSpecificationRead;
import io.airbyte.api.model.SourceDefinitionUpdate;
import io.airbyte.api.model.SourceDiscoverSchemaRead;
import io.airbyte.api.model.SourceIdRequestBody;
import io.airbyte.api.model.SourceOauthConsentRequest;
import io.airbyte.api.model.SourceRead;
import io.airbyte.api.model.SourceReadList;
import io.airbyte.api.model.SourceSearch;
import io.airbyte.api.model.SourceUpdate;
import io.airbyte.api.model.UploadRead;
import io.airbyte.api.model.WebBackendConnectionCreate;
import io.airbyte.api.model.WebBackendConnectionRead;
import io.airbyte.api.model.WebBackendConnectionReadList;
import io.airbyte.api.model.WebBackendConnectionRequestBody;
import io.airbyte.api.model.WebBackendConnectionSearch;
import io.airbyte.api.model.WebBackendConnectionUpdate;
import io.airbyte.api.model.WorkspaceCreate;
import io.airbyte.api.model.WorkspaceGiveFeedback;
import io.airbyte.api.model.WorkspaceIdRequestBody;
import io.airbyte.api.model.WorkspaceRead;
import io.airbyte.api.model.WorkspaceReadList;
import io.airbyte.api.model.WorkspaceUpdate;
import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.commons.io.FileTtlManager;
import io.airbyte.commons.version.AirbyteVersion;
import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.helpers.LogConfigs;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigPersistence;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.db.Database;
import io.airbyte.scheduler.client.SchedulerJobClient;
import io.airbyte.scheduler.client.SynchronousSchedulerClient;
import io.airbyte.scheduler.persistence.JobNotifier;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.scheduler.persistence.WorkspaceHelper;
import io.airbyte.scheduler.persistence.job_factory.OAuthConfigSupplier;
import io.airbyte.server.errors.BadObjectSchemaKnownException;
import io.airbyte.server.errors.IdNotFoundKnownException;
import io.airbyte.server.handlers.ArchiveHandler;
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
import io.airbyte.server.handlers.WebBackendConnectionsHandler;
import io.airbyte.server.handlers.WorkspacesHandler;
import io.airbyte.validation.json.JsonSchemaValidator;
import io.airbyte.validation.json.JsonValidationException;
import io.airbyte.workers.WorkerConfigs;
import io.airbyte.workers.helper.ConnectionHelper;
import io.airbyte.workers.worker_run.TemporalWorkerRunFactory;
import io.temporal.serviceclient.WorkflowServiceStubs;
import java.io.File;
import java.io.IOException;
import java.net.http.HttpClient;
import java.nio.file.Path;
import java.util.Map;

@javax.ws.rs.Path("/v1")
public class ConfigurationApi implements io.airbyte.api.V1Api {

  private final WorkspacesHandler workspacesHandler;
  private final SourceDefinitionsHandler sourceDefinitionsHandler;
  private final SourceHandler sourceHandler;
  private final DestinationDefinitionsHandler destinationDefinitionsHandler;
  private final DestinationHandler destinationHandler;
  private final ConnectionsHandler connectionsHandler;
  private final OperationsHandler operationsHandler;
  private final SchedulerHandler schedulerHandler;
  private final JobHistoryHandler jobHistoryHandler;
  private final WebBackendConnectionsHandler webBackendConnectionsHandler;
  private final HealthCheckHandler healthCheckHandler;
  private final ArchiveHandler archiveHandler;
  private final LogsHandler logsHandler;
  private final OpenApiConfigHandler openApiConfigHandler;
  private final DbMigrationHandler dbMigrationHandler;
  private final OAuthHandler oAuthHandler;
  private final WorkerEnvironment workerEnvironment;
  private final LogConfigs logConfigs;
  private final Path workspaceRoot;
  private final FeatureFlags featureFlags;

  public ConfigurationApi(final ConfigRepository configRepository,
                          final JobPersistence jobPersistence,
                          final ConfigPersistence seed,
                          final SchedulerJobClient schedulerJobClient,
                          final SynchronousSchedulerClient synchronousSchedulerClient,
                          final FileTtlManager archiveTtlManager,
                          final WorkflowServiceStubs temporalService,
                          final Database configsDatabase,
                          final Database jobsDatabase,
                          final TrackingClient trackingClient,
                          final WorkerEnvironment workerEnvironment,
                          final LogConfigs logConfigs,
                          final WorkerConfigs workerConfigs,
                          final String webappUrl,
                          final AirbyteVersion airbyteVersion,
                          final Path workspaceRoot,
                          final HttpClient httpClient,
                          final FeatureFlags featureFlags,
                          final TemporalWorkerRunFactory temporalWorkerRunFactory) {
    this.workerEnvironment = workerEnvironment;
    this.logConfigs = logConfigs;
    this.workspaceRoot = workspaceRoot;

    final JsonSchemaValidator schemaValidator = new JsonSchemaValidator();
    final JobNotifier jobNotifier = new JobNotifier(
        webappUrl,
        configRepository,
        new WorkspaceHelper(configRepository, jobPersistence),
        trackingClient);

    final WorkspaceHelper workspaceHelper = new WorkspaceHelper(configRepository, jobPersistence);

    schedulerHandler = new SchedulerHandler(
        configRepository,
        schedulerJobClient,
        synchronousSchedulerClient,
        jobPersistence,
        jobNotifier,
        temporalService,
        new OAuthConfigSupplier(configRepository, trackingClient), workerEnvironment, logConfigs, temporalWorkerRunFactory);
    final ConnectionHelper connectionHelper = new ConnectionHelper(configRepository, workspaceHelper, workerConfigs);
    connectionsHandler = new ConnectionsHandler(
        configRepository,
        workspaceHelper,
        trackingClient,
        temporalWorkerRunFactory,
        featureFlags,
        connectionHelper,
        workerConfigs);
    sourceHandler = new SourceHandler(configRepository, schemaValidator, connectionsHandler);
    sourceDefinitionsHandler = new SourceDefinitionsHandler(configRepository, synchronousSchedulerClient, sourceHandler);
    operationsHandler = new OperationsHandler(configRepository);
    destinationHandler = new DestinationHandler(configRepository, schemaValidator, connectionsHandler);
    destinationDefinitionsHandler = new DestinationDefinitionsHandler(configRepository, synchronousSchedulerClient, destinationHandler);
    workspacesHandler = new WorkspacesHandler(configRepository, connectionsHandler, destinationHandler, sourceHandler);
    jobHistoryHandler = new JobHistoryHandler(jobPersistence, workerEnvironment, logConfigs);
    oAuthHandler = new OAuthHandler(configRepository, httpClient, trackingClient);
    webBackendConnectionsHandler = new WebBackendConnectionsHandler(
        connectionsHandler,
        sourceHandler,
        destinationHandler,
        jobHistoryHandler,
        schedulerHandler,
        operationsHandler);
    healthCheckHandler = new HealthCheckHandler(configRepository);
    archiveHandler = new ArchiveHandler(
        airbyteVersion,
        configRepository,
        jobPersistence,
        seed,
        workspaceHelper,
        archiveTtlManager,
        true);
    logsHandler = new LogsHandler();
    openApiConfigHandler = new OpenApiConfigHandler();
    dbMigrationHandler = new DbMigrationHandler(configsDatabase, jobsDatabase);
    this.featureFlags = featureFlags;
  }

  // WORKSPACE

  @Override
  public WorkspaceReadList listWorkspaces() {
    return execute(workspacesHandler::listWorkspaces);
  }

  @Override
  public WorkspaceRead createWorkspace(final WorkspaceCreate workspaceCreate) {
    return execute(() -> workspacesHandler.createWorkspace(workspaceCreate));
  }

  @Override
  public void deleteWorkspace(final WorkspaceIdRequestBody workspaceIdRequestBody) {
    execute(() -> {
      workspacesHandler.deleteWorkspace(workspaceIdRequestBody);
      return null;
    });
  }

  @Override
  public WorkspaceRead getWorkspace(final WorkspaceIdRequestBody workspaceIdRequestBody) {
    return execute(() -> workspacesHandler.getWorkspace(workspaceIdRequestBody));
  }

  @Override
  public WorkspaceRead getWorkspaceBySlug(final SlugRequestBody slugRequestBody) {
    return execute(() -> workspacesHandler.getWorkspaceBySlug(slugRequestBody));
  }

  @Override
  public WorkspaceRead updateWorkspace(final WorkspaceUpdate workspaceUpdate) {
    return execute(() -> workspacesHandler.updateWorkspace(workspaceUpdate));
  }

  @Override
  public void updateWorkspaceFeedback(final WorkspaceGiveFeedback workspaceGiveFeedback) {
    execute(() -> {
      workspacesHandler.setFeedbackDone(workspaceGiveFeedback);
      return null;
    });
  }

  @Override
  public NotificationRead tryNotificationConfig(final Notification notification) {
    return execute(() -> workspacesHandler.tryNotification(notification));
  }

  // SOURCE

  @Override
  public SourceDefinitionReadList listSourceDefinitions() {
    return execute(sourceDefinitionsHandler::listSourceDefinitions);
  }

  @Override
  public SourceDefinitionReadList listLatestSourceDefinitions() {
    return execute(sourceDefinitionsHandler::listLatestSourceDefinitions);
  }

  @Override
  public SourceDefinitionRead getSourceDefinition(final SourceDefinitionIdRequestBody sourceDefinitionIdRequestBody) {
    return execute(() -> sourceDefinitionsHandler.getSourceDefinition(sourceDefinitionIdRequestBody));
  }

  @Override
  public SourceDefinitionRead createSourceDefinition(final SourceDefinitionCreate sourceDefinitionCreate) {
    return execute(() -> sourceDefinitionsHandler.createSourceDefinition(sourceDefinitionCreate));
  }

  @Override
  public SourceDefinitionRead updateSourceDefinition(final SourceDefinitionUpdate sourceDefinitionUpdate) {
    return execute(() -> sourceDefinitionsHandler.updateSourceDefinition(sourceDefinitionUpdate));
  }

  @Override
  public void deleteSourceDefinition(final SourceDefinitionIdRequestBody sourceDefinitionIdRequestBody) {
    execute(() -> {
      sourceDefinitionsHandler.deleteSourceDefinition(sourceDefinitionIdRequestBody);
      return null;
    });
  }

  // SOURCE SPECIFICATION

  @Override
  public SourceDefinitionSpecificationRead getSourceDefinitionSpecification(final SourceDefinitionIdRequestBody sourceDefinitionIdRequestBody) {
    return execute(() -> schedulerHandler.getSourceDefinitionSpecification(sourceDefinitionIdRequestBody));
  }

  // OAUTH

  @Override
  public OAuthConsentRead getSourceOAuthConsent(final SourceOauthConsentRequest sourceOauthConsentRequest) {
    return execute(() -> oAuthHandler.getSourceOAuthConsent(sourceOauthConsentRequest));
  }

  @Override
  public Map<String, Object> completeSourceOAuth(final CompleteSourceOauthRequest completeSourceOauthRequest) {
    return execute(() -> oAuthHandler.completeSourceOAuth(completeSourceOauthRequest));
  }

  @Override
  public OAuthConsentRead getDestinationOAuthConsent(final DestinationOauthConsentRequest destinationOauthConsentRequest) {
    return execute(() -> oAuthHandler.getDestinationOAuthConsent(destinationOauthConsentRequest));
  }

  @Override
  public Map<String, Object> completeDestinationOAuth(final CompleteDestinationOAuthRequest requestBody) {
    return execute(() -> oAuthHandler.completeDestinationOAuth(requestBody));
  }

  @Override
  public void setInstancewideDestinationOauthParams(final SetInstancewideDestinationOauthParamsRequestBody requestBody) {
    execute(() -> {
      oAuthHandler.setDestinationInstancewideOauthParams(requestBody);
      return null;
    });
  }

  @Override
  public void setInstancewideSourceOauthParams(final SetInstancewideSourceOauthParamsRequestBody requestBody) {
    execute(() -> {
      oAuthHandler.setSourceInstancewideOauthParams(requestBody);
      return null;
    });
  }

  // SOURCE IMPLEMENTATION

  @Override
  public SourceRead createSource(final SourceCreate sourceCreate) {
    return execute(() -> sourceHandler.createSource(sourceCreate));
  }

  @Override
  public SourceRead updateSource(final SourceUpdate sourceUpdate) {
    return execute(() -> sourceHandler.updateSource(sourceUpdate));
  }

  @Override
  public SourceReadList listSourcesForWorkspace(final WorkspaceIdRequestBody workspaceIdRequestBody) {
    return execute(() -> sourceHandler.listSourcesForWorkspace(workspaceIdRequestBody));
  }

  @Override
  public SourceReadList searchSources(final SourceSearch sourceSearch) {
    return execute(() -> sourceHandler.searchSources(sourceSearch));
  }

  @Override
  public SourceRead getSource(final SourceIdRequestBody sourceIdRequestBody) {
    return execute(() -> sourceHandler.getSource(sourceIdRequestBody));
  }

  @Override
  public void deleteSource(final SourceIdRequestBody sourceIdRequestBody) {
    execute(() -> {
      sourceHandler.deleteSource(sourceIdRequestBody);
      return null;
    });
  }

  @Override
  public CheckConnectionRead checkConnectionToSource(final SourceIdRequestBody sourceIdRequestBody) {
    return execute(() -> schedulerHandler.checkSourceConnectionFromSourceId(sourceIdRequestBody));
  }

  @Override
  public CheckConnectionRead checkConnectionToSourceForUpdate(final SourceUpdate sourceUpdate) {
    return execute(() -> schedulerHandler.checkSourceConnectionFromSourceIdForUpdate(sourceUpdate));
  }

  @Override
  public SourceDiscoverSchemaRead discoverSchemaForSource(final SourceIdRequestBody sourceIdRequestBody) {
    return execute(() -> schedulerHandler.discoverSchemaForSourceFromSourceId(sourceIdRequestBody));
  }

  // DB MIGRATION

  @Override
  public DbMigrationReadList listMigrations(final DbMigrationRequestBody request) {
    return execute(() -> dbMigrationHandler.list(request));
  }

  @Override
  public DbMigrationExecutionRead executeMigrations(final DbMigrationRequestBody request) {
    return execute(() -> dbMigrationHandler.migrate(request));
  }

  // DESTINATION

  @Override
  public DestinationDefinitionReadList listDestinationDefinitions() {
    return execute(destinationDefinitionsHandler::listDestinationDefinitions);
  }

  @Override
  public DestinationDefinitionReadList listLatestDestinationDefinitions() {
    return execute(destinationDefinitionsHandler::listLatestDestinationDefinitions);
  }

  @Override
  public DestinationDefinitionRead getDestinationDefinition(final DestinationDefinitionIdRequestBody destinationDefinitionIdRequestBody) {
    return execute(() -> destinationDefinitionsHandler.getDestinationDefinition(destinationDefinitionIdRequestBody));
  }

  @Override
  public DestinationDefinitionRead createDestinationDefinition(final DestinationDefinitionCreate destinationDefinitionCreate) {
    return execute(() -> destinationDefinitionsHandler.createDestinationDefinition(destinationDefinitionCreate));
  }

  @Override
  public DestinationDefinitionRead updateDestinationDefinition(final DestinationDefinitionUpdate destinationDefinitionUpdate) {
    return execute(() -> destinationDefinitionsHandler.updateDestinationDefinition(destinationDefinitionUpdate));
  }

  @Override
  public void deleteDestinationDefinition(final DestinationDefinitionIdRequestBody destinationDefinitionIdRequestBody) {
    execute(() -> {
      destinationDefinitionsHandler.deleteDestinationDefinition(destinationDefinitionIdRequestBody);
      return null;
    });
  }

  // DESTINATION SPECIFICATION

  @Override
  public DestinationDefinitionSpecificationRead getDestinationDefinitionSpecification(final DestinationDefinitionIdRequestBody destinationDefinitionIdRequestBody) {
    return execute(() -> schedulerHandler.getDestinationSpecification(destinationDefinitionIdRequestBody));
  }

  // DESTINATION IMPLEMENTATION

  @Override
  public DestinationRead createDestination(final DestinationCreate destinationCreate) {
    return execute(() -> destinationHandler.createDestination(destinationCreate));
  }

  @Override
  public void deleteDestination(final DestinationIdRequestBody destinationIdRequestBody) {
    execute(() -> {
      destinationHandler.deleteDestination(destinationIdRequestBody);
      return null;
    });
  }

  @Override
  public DestinationRead updateDestination(final DestinationUpdate destinationUpdate) {
    return execute(() -> destinationHandler.updateDestination(destinationUpdate));
  }

  @Override
  public DestinationReadList listDestinationsForWorkspace(final WorkspaceIdRequestBody workspaceIdRequestBody) {
    return execute(() -> destinationHandler.listDestinationsForWorkspace(workspaceIdRequestBody));
  }

  @Override
  public DestinationReadList searchDestinations(final DestinationSearch destinationSearch) {
    return execute(() -> destinationHandler.searchDestinations(destinationSearch));
  }

  @Override
  public DestinationRead getDestination(final DestinationIdRequestBody destinationIdRequestBody) {
    return execute(() -> destinationHandler.getDestination(destinationIdRequestBody));
  }

  @Override
  public CheckConnectionRead checkConnectionToDestination(final DestinationIdRequestBody destinationIdRequestBody) {
    return execute(() -> schedulerHandler.checkDestinationConnectionFromDestinationId(destinationIdRequestBody));
  }

  @Override
  public CheckConnectionRead checkConnectionToDestinationForUpdate(final DestinationUpdate destinationUpdate) {
    return execute(() -> schedulerHandler.checkDestinationConnectionFromDestinationIdForUpdate(destinationUpdate));
  }

  // CONNECTION

  @Override
  public ConnectionRead createConnection(final ConnectionCreate connectionCreate) {
    return execute(() -> connectionsHandler.createConnection(connectionCreate));
  }

  @Override
  public ConnectionRead updateConnection(final ConnectionUpdate connectionUpdate) {
    return execute(() -> connectionsHandler.updateConnection(connectionUpdate));
  }

  @Override
  public ConnectionReadList listConnectionsForWorkspace(final WorkspaceIdRequestBody workspaceIdRequestBody) {
    return execute(() -> connectionsHandler.listConnectionsForWorkspace(workspaceIdRequestBody));
  }

  @Override
  public ConnectionReadList listAllConnectionsForWorkspace(final WorkspaceIdRequestBody workspaceIdRequestBody) {
    return execute(() -> connectionsHandler.listAllConnectionsForWorkspace(workspaceIdRequestBody));
  }

  @Override
  public ConnectionReadList searchConnections(final ConnectionSearch connectionSearch) {
    return execute(() -> connectionsHandler.searchConnections(connectionSearch));
  }

  @Override
  public ConnectionRead getConnection(final ConnectionIdRequestBody connectionIdRequestBody) {
    return execute(() -> connectionsHandler.getConnection(connectionIdRequestBody.getConnectionId()));
  }

  @Override
  public void deleteConnection(final ConnectionIdRequestBody connectionIdRequestBody) {
    execute(() -> {
      operationsHandler.deleteOperationsForConnection(connectionIdRequestBody);
      connectionsHandler.deleteConnection(connectionIdRequestBody.getConnectionId());
      return null;
    });
  }

  @Override
  public JobInfoRead syncConnection(final ConnectionIdRequestBody connectionIdRequestBody) {
    if (featureFlags.usesNewScheduler()) {
      return execute(() -> schedulerHandler.createManualRun(connectionIdRequestBody.getConnectionId()));
    }

    return execute(() -> schedulerHandler.syncConnection(connectionIdRequestBody));
  }

  @Override
  public JobInfoRead resetConnection(final ConnectionIdRequestBody connectionIdRequestBody) {
    return execute(() -> schedulerHandler.resetConnection(connectionIdRequestBody));
  }

  // Operations

  @Override
  public CheckOperationRead checkOperation(final OperatorConfiguration operatorConfiguration) {
    return execute(() -> operationsHandler.checkOperation(operatorConfiguration));
  }

  @Override
  public OperationRead createOperation(final OperationCreate operationCreate) {
    return execute(() -> operationsHandler.createOperation(operationCreate));
  }

  @Override
  public void deleteOperation(final OperationIdRequestBody operationIdRequestBody) {
    execute(() -> {
      operationsHandler.deleteOperation(operationIdRequestBody);
      return null;
    });
  }

  @Override
  public OperationReadList listOperationsForConnection(final ConnectionIdRequestBody connectionIdRequestBody) {
    return execute(() -> operationsHandler.listOperationsForConnection(connectionIdRequestBody));
  }

  @Override
  public OperationRead getOperation(final OperationIdRequestBody operationIdRequestBody) {
    return execute(() -> operationsHandler.getOperation(operationIdRequestBody));
  }

  @Override
  public OperationRead updateOperation(final OperationUpdate operationUpdate) {
    return execute(() -> operationsHandler.updateOperation(operationUpdate));
  }

  @Override
  public ConnectionState getState(final ConnectionIdRequestBody connectionIdRequestBody) {
    return execute(() -> schedulerHandler.getState(connectionIdRequestBody));
  }

  // SCHEDULER
  @Override
  public CheckConnectionRead executeSourceCheckConnection(final SourceCoreConfig sourceConfig) {
    return execute(() -> schedulerHandler.checkSourceConnectionFromSourceCreate(sourceConfig));
  }

  @Override
  public CheckConnectionRead executeDestinationCheckConnection(final DestinationCoreConfig destinationConfig) {
    return execute(() -> schedulerHandler.checkDestinationConnectionFromDestinationCreate(destinationConfig));
  }

  @Override
  public SourceDiscoverSchemaRead executeSourceDiscoverSchema(final SourceCoreConfig sourceCreate) {
    return execute(() -> schedulerHandler.discoverSchemaForSourceFromSourceCreate(sourceCreate));
  }

  @Override
  public JobInfoRead cancelJob(final JobIdRequestBody jobIdRequestBody) {
    if (featureFlags.usesNewScheduler()) {
      return execute(() -> schedulerHandler.createNewSchedulerCancellation(jobIdRequestBody.getId()));
    }

    return execute(() -> schedulerHandler.cancelJob(jobIdRequestBody));
  }

  // JOB HISTORY

  @Override
  public JobReadList listJobsFor(final JobListRequestBody jobListRequestBody) {
    return execute(() -> jobHistoryHandler.listJobsFor(jobListRequestBody));
  }

  @Override
  public JobInfoRead getJobInfo(final JobIdRequestBody jobIdRequestBody) {
    return execute(() -> jobHistoryHandler.getJobInfo(jobIdRequestBody));
  }

  @Override
  public File getLogs(final LogsRequestBody logsRequestBody) {
    return execute(() -> logsHandler.getLogs(workspaceRoot, workerEnvironment, logConfigs, logsRequestBody));
  }

  @Override
  public File getOpenApiSpec() {
    return execute(openApiConfigHandler::getFile);
  }

  // HEALTH
  @Override
  public HealthCheckRead getHealthCheck() {
    return healthCheckHandler.health();
  }

  // WEB BACKEND

  @Override
  public WebBackendConnectionReadList webBackendListConnectionsForWorkspace(final WorkspaceIdRequestBody workspaceIdRequestBody) {
    return execute(() -> webBackendConnectionsHandler.webBackendListConnectionsForWorkspace(workspaceIdRequestBody));
  }

  @Override
  public WebBackendConnectionReadList webBackendListAllConnectionsForWorkspace(final WorkspaceIdRequestBody workspaceIdRequestBody) {
    return execute(() -> webBackendConnectionsHandler.webBackendListAllConnectionsForWorkspace(workspaceIdRequestBody));
  }

  @Override
  public WebBackendConnectionReadList webBackendSearchConnections(final WebBackendConnectionSearch webBackendConnectionSearch) {
    return execute(() -> webBackendConnectionsHandler.webBackendSearchConnections(webBackendConnectionSearch));
  }

  @Override
  public WebBackendConnectionRead webBackendGetConnection(final WebBackendConnectionRequestBody webBackendConnectionRequestBody) {
    return execute(() -> webBackendConnectionsHandler.webBackendGetConnection(webBackendConnectionRequestBody));
  }

  @Override
  public WebBackendConnectionRead webBackendCreateConnection(final WebBackendConnectionCreate webBackendConnectionCreate) {
    return execute(() -> webBackendConnectionsHandler.webBackendCreateConnection(webBackendConnectionCreate));
  }

  @Override
  public WebBackendConnectionRead webBackendUpdateConnection(final WebBackendConnectionUpdate webBackendConnectionUpdate) {
    return execute(() -> webBackendConnectionsHandler.webBackendUpdateConnection(webBackendConnectionUpdate));
  }

  // ARCHIVES

  @Override
  public File exportArchive() {
    return execute(archiveHandler::exportData);
  }

  @Override
  public ImportRead importArchive(final File archiveFile) {
    return execute(() -> archiveHandler.importData(archiveFile));
  }

  @Override
  public File exportWorkspace(final WorkspaceIdRequestBody workspaceIdRequestBody) {
    return execute(() -> archiveHandler.exportWorkspace(workspaceIdRequestBody));
  }

  @Override
  public UploadRead uploadArchiveResource(final File archiveFile) {
    return execute(() -> archiveHandler.uploadArchiveResource(archiveFile));
  }

  @Override
  public ImportRead importIntoWorkspace(final ImportRequestBody importRequestBody) {
    return execute(() -> archiveHandler.importIntoWorkspace(importRequestBody));
  }

  public boolean canImportDefinitons() {
    return archiveHandler.canImportDefinitions();
  }

  private <T> T execute(final HandlerCall<T> call) {
    try {
      return call.call();
    } catch (final ConfigNotFoundException e) {
      throw new IdNotFoundKnownException(String.format("Could not find configuration for %s: %s.", e.getType().toString(), e.getConfigId()),
          e.getConfigId(), e);
    } catch (final JsonValidationException e) {
      throw new BadObjectSchemaKnownException(
          String.format("The provided configuration does not fulfill the specification. Errors: %s", e.getMessage()), e);
    } catch (final IOException e) {
      throw new RuntimeException(e);
    }
  }

  private interface HandlerCall<T> {

    T call() throws ConfigNotFoundException, IOException, JsonValidationException;

  }

}
