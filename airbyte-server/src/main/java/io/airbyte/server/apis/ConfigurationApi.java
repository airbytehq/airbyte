/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis;

import io.airbyte.analytics.TrackingClient;
import io.airbyte.api.model.generated.CheckConnectionRead;
import io.airbyte.api.model.generated.CheckOperationRead;
import io.airbyte.api.model.generated.CompleteDestinationOAuthRequest;
import io.airbyte.api.model.generated.CompleteSourceOauthRequest;
import io.airbyte.api.model.generated.ConnectionCreate;
import io.airbyte.api.model.generated.ConnectionIdRequestBody;
import io.airbyte.api.model.generated.ConnectionRead;
import io.airbyte.api.model.generated.ConnectionReadList;
import io.airbyte.api.model.generated.ConnectionSearch;
import io.airbyte.api.model.generated.ConnectionState;
import io.airbyte.api.model.generated.ConnectionStateCreateOrUpdate;
import io.airbyte.api.model.generated.ConnectionStateType;
import io.airbyte.api.model.generated.ConnectionUpdate;
import io.airbyte.api.model.generated.CustomDestinationDefinitionCreate;
import io.airbyte.api.model.generated.CustomDestinationDefinitionUpdate;
import io.airbyte.api.model.generated.CustomSourceDefinitionCreate;
import io.airbyte.api.model.generated.CustomSourceDefinitionUpdate;
import io.airbyte.api.model.generated.DbMigrationExecutionRead;
import io.airbyte.api.model.generated.DbMigrationReadList;
import io.airbyte.api.model.generated.DbMigrationRequestBody;
import io.airbyte.api.model.generated.DestinationCloneRequestBody;
import io.airbyte.api.model.generated.DestinationCoreConfig;
import io.airbyte.api.model.generated.DestinationCreate;
import io.airbyte.api.model.generated.DestinationDefinitionCreate;
import io.airbyte.api.model.generated.DestinationDefinitionIdRequestBody;
import io.airbyte.api.model.generated.DestinationDefinitionIdWithWorkspaceId;
import io.airbyte.api.model.generated.DestinationDefinitionRead;
import io.airbyte.api.model.generated.DestinationDefinitionReadList;
import io.airbyte.api.model.generated.DestinationDefinitionSpecificationRead;
import io.airbyte.api.model.generated.DestinationDefinitionUpdate;
import io.airbyte.api.model.generated.DestinationIdRequestBody;
import io.airbyte.api.model.generated.DestinationOauthConsentRequest;
import io.airbyte.api.model.generated.DestinationRead;
import io.airbyte.api.model.generated.DestinationReadList;
import io.airbyte.api.model.generated.DestinationSearch;
import io.airbyte.api.model.generated.DestinationUpdate;
import io.airbyte.api.model.generated.HealthCheckRead;
import io.airbyte.api.model.generated.ImportRead;
import io.airbyte.api.model.generated.ImportRequestBody;
import io.airbyte.api.model.generated.InternalOperationResult;
import io.airbyte.api.model.generated.JobDebugInfoRead;
import io.airbyte.api.model.generated.JobIdRequestBody;
import io.airbyte.api.model.generated.JobInfoRead;
import io.airbyte.api.model.generated.JobListRequestBody;
import io.airbyte.api.model.generated.JobReadList;
import io.airbyte.api.model.generated.LogsRequestBody;
import io.airbyte.api.model.generated.Notification;
import io.airbyte.api.model.generated.NotificationRead;
import io.airbyte.api.model.generated.OAuthConsentRead;
import io.airbyte.api.model.generated.OperationCreate;
import io.airbyte.api.model.generated.OperationIdRequestBody;
import io.airbyte.api.model.generated.OperationRead;
import io.airbyte.api.model.generated.OperationReadList;
import io.airbyte.api.model.generated.OperationUpdate;
import io.airbyte.api.model.generated.OperatorConfiguration;
import io.airbyte.api.model.generated.PrivateDestinationDefinitionRead;
import io.airbyte.api.model.generated.PrivateDestinationDefinitionReadList;
import io.airbyte.api.model.generated.PrivateSourceDefinitionRead;
import io.airbyte.api.model.generated.PrivateSourceDefinitionReadList;
import io.airbyte.api.model.generated.SetInstancewideDestinationOauthParamsRequestBody;
import io.airbyte.api.model.generated.SetInstancewideSourceOauthParamsRequestBody;
import io.airbyte.api.model.generated.SetWorkflowInAttemptRequestBody;
import io.airbyte.api.model.generated.SlugRequestBody;
import io.airbyte.api.model.generated.SourceCloneRequestBody;
import io.airbyte.api.model.generated.SourceCoreConfig;
import io.airbyte.api.model.generated.SourceCreate;
import io.airbyte.api.model.generated.SourceDefinitionCreate;
import io.airbyte.api.model.generated.SourceDefinitionIdRequestBody;
import io.airbyte.api.model.generated.SourceDefinitionIdWithWorkspaceId;
import io.airbyte.api.model.generated.SourceDefinitionRead;
import io.airbyte.api.model.generated.SourceDefinitionReadList;
import io.airbyte.api.model.generated.SourceDefinitionSpecificationRead;
import io.airbyte.api.model.generated.SourceDefinitionUpdate;
import io.airbyte.api.model.generated.SourceDiscoverSchemaRead;
import io.airbyte.api.model.generated.SourceDiscoverSchemaRequestBody;
import io.airbyte.api.model.generated.SourceIdRequestBody;
import io.airbyte.api.model.generated.SourceOauthConsentRequest;
import io.airbyte.api.model.generated.SourceRead;
import io.airbyte.api.model.generated.SourceReadList;
import io.airbyte.api.model.generated.SourceSearch;
import io.airbyte.api.model.generated.SourceUpdate;
import io.airbyte.api.model.generated.UploadRead;
import io.airbyte.api.model.generated.WebBackendConnectionCreate;
import io.airbyte.api.model.generated.WebBackendConnectionRead;
import io.airbyte.api.model.generated.WebBackendConnectionReadList;
import io.airbyte.api.model.generated.WebBackendConnectionRequestBody;
import io.airbyte.api.model.generated.WebBackendConnectionSearch;
import io.airbyte.api.model.generated.WebBackendConnectionUpdate;
import io.airbyte.api.model.generated.WebBackendWorkspaceState;
import io.airbyte.api.model.generated.WebBackendWorkspaceStateResult;
import io.airbyte.api.model.generated.WorkspaceCreate;
import io.airbyte.api.model.generated.WorkspaceGiveFeedback;
import io.airbyte.api.model.generated.WorkspaceIdRequestBody;
import io.airbyte.api.model.generated.WorkspaceRead;
import io.airbyte.api.model.generated.WorkspaceReadList;
import io.airbyte.api.model.generated.WorkspaceUpdate;
import io.airbyte.api.model.generated.WorkspaceUpdateName;
import io.airbyte.commons.io.FileTtlManager;
import io.airbyte.commons.version.AirbyteVersion;
import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.helpers.LogConfigs;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigPersistence;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.SecretsRepositoryReader;
import io.airbyte.config.persistence.SecretsRepositoryWriter;
import io.airbyte.config.persistence.StatePersistence;
import io.airbyte.db.Database;
import io.airbyte.scheduler.client.EventRunner;
import io.airbyte.scheduler.client.SynchronousSchedulerClient;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.scheduler.persistence.WorkspaceHelper;
import io.airbyte.server.errors.BadObjectSchemaKnownException;
import io.airbyte.server.errors.IdNotFoundKnownException;
import io.airbyte.server.handlers.ArchiveHandler;
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
import io.airbyte.server.handlers.WorkspacesHandler;
import io.airbyte.validation.json.JsonSchemaValidator;
import io.airbyte.validation.json.JsonValidationException;
import java.io.File;
import java.io.IOException;
import java.net.http.HttpClient;
import java.nio.file.Path;
import java.util.Map;
import lombok.extern.slf4j.Slf4j;
import org.flywaydb.core.Flyway;

@javax.ws.rs.Path("/v1")
@Slf4j
public class ConfigurationApi implements io.airbyte.api.generated.V1Api {

  private final WorkspacesHandler workspacesHandler;
  private final SourceDefinitionsHandler sourceDefinitionsHandler;
  private final SourceHandler sourceHandler;
  private final DestinationDefinitionsHandler destinationDefinitionsHandler;
  private final DestinationHandler destinationHandler;
  private final ConnectionsHandler connectionsHandler;
  private final OperationsHandler operationsHandler;
  private final SchedulerHandler schedulerHandler;
  private final StateHandler stateHandler;
  private final JobHistoryHandler jobHistoryHandler;
  private final WebBackendConnectionsHandler webBackendConnectionsHandler;
  private final HealthCheckHandler healthCheckHandler;
  private final ArchiveHandler archiveHandler;
  private final LogsHandler logsHandler;
  private final OpenApiConfigHandler openApiConfigHandler;
  private final DbMigrationHandler dbMigrationHandler;
  private final OAuthHandler oAuthHandler;
  private final AttemptHandler attemptHandler;
  private final WorkerEnvironment workerEnvironment;
  private final LogConfigs logConfigs;
  private final Path workspaceRoot;

  public ConfigurationApi(final ConfigRepository configRepository,
                          final JobPersistence jobPersistence,
                          final ConfigPersistence seed,
                          final SecretsRepositoryReader secretsRepositoryReader,
                          final SecretsRepositoryWriter secretsRepositoryWriter,
                          final SynchronousSchedulerClient synchronousSchedulerClient,
                          final FileTtlManager archiveTtlManager,
                          final Database configsDatabase,
                          final Database jobsDatabase,
                          final StatePersistence statePersistence,
                          final TrackingClient trackingClient,
                          final WorkerEnvironment workerEnvironment,
                          final LogConfigs logConfigs,
                          final AirbyteVersion airbyteVersion,
                          final Path workspaceRoot,
                          final HttpClient httpClient,
                          final EventRunner eventRunner,
                          final Flyway configsFlyway,
                          final Flyway jobsFlyway) {
    this.workerEnvironment = workerEnvironment;
    this.logConfigs = logConfigs;
    this.workspaceRoot = workspaceRoot;

    final JsonSchemaValidator schemaValidator = new JsonSchemaValidator();

    final WorkspaceHelper workspaceHelper = new WorkspaceHelper(configRepository, jobPersistence);

    schedulerHandler = new SchedulerHandler(
        configRepository,
        secretsRepositoryReader,
        secretsRepositoryWriter,
        synchronousSchedulerClient,
        jobPersistence,
        workerEnvironment,
        logConfigs,
        eventRunner);

    stateHandler = new StateHandler(statePersistence);
    connectionsHandler = new ConnectionsHandler(
        configRepository,
        workspaceHelper,
        trackingClient,
        eventRunner);
    sourceHandler = new SourceHandler(
        configRepository,
        secretsRepositoryReader,
        secretsRepositoryWriter,
        schemaValidator,
        connectionsHandler);
    sourceDefinitionsHandler = new SourceDefinitionsHandler(configRepository, synchronousSchedulerClient, sourceHandler);
    operationsHandler = new OperationsHandler(configRepository);
    destinationHandler = new DestinationHandler(
        configRepository,
        secretsRepositoryReader,
        secretsRepositoryWriter,
        schemaValidator,
        connectionsHandler);
    destinationDefinitionsHandler = new DestinationDefinitionsHandler(configRepository, synchronousSchedulerClient, destinationHandler);
    workspacesHandler = new WorkspacesHandler(configRepository, connectionsHandler, destinationHandler, sourceHandler);
    jobHistoryHandler = new JobHistoryHandler(jobPersistence, workerEnvironment, logConfigs, connectionsHandler, sourceHandler,
        sourceDefinitionsHandler, destinationHandler, destinationDefinitionsHandler, airbyteVersion);
    oAuthHandler = new OAuthHandler(configRepository, httpClient, trackingClient);
    webBackendConnectionsHandler = new WebBackendConnectionsHandler(
        connectionsHandler,
        stateHandler,
        sourceHandler,
        destinationHandler,
        jobHistoryHandler,
        schedulerHandler,
        operationsHandler,
        eventRunner,
        configRepository);
    healthCheckHandler = new HealthCheckHandler(configRepository);
    archiveHandler = new ArchiveHandler(
        airbyteVersion,
        configRepository,
        secretsRepositoryReader,
        secretsRepositoryWriter,
        jobPersistence,
        seed,
        workspaceHelper,
        archiveTtlManager,
        true);
    logsHandler = new LogsHandler();
    openApiConfigHandler = new OpenApiConfigHandler();
    dbMigrationHandler = new DbMigrationHandler(configsDatabase, configsFlyway, jobsDatabase, jobsFlyway);
    attemptHandler = new AttemptHandler(jobPersistence);
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
  public WorkspaceRead updateWorkspaceName(final WorkspaceUpdateName workspaceUpdateName) {
    return execute(() -> workspacesHandler.updateWorkspaceName(workspaceUpdateName));
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
  public SourceDefinitionReadList listSourceDefinitionsForWorkspace(final WorkspaceIdRequestBody workspaceIdRequestBody) {
    return execute(() -> sourceDefinitionsHandler.listSourceDefinitionsForWorkspace(workspaceIdRequestBody));
  }

  @Override
  public SourceDefinitionReadList listLatestSourceDefinitions() {
    return execute(sourceDefinitionsHandler::listLatestSourceDefinitions);
  }

  @Override
  public PrivateSourceDefinitionReadList listPrivateSourceDefinitions(final WorkspaceIdRequestBody workspaceIdRequestBody) {
    return execute(() -> sourceDefinitionsHandler.listPrivateSourceDefinitions(workspaceIdRequestBody));
  }

  @Override
  public SourceDefinitionRead getSourceDefinition(final SourceDefinitionIdRequestBody sourceDefinitionIdRequestBody) {
    return execute(() -> sourceDefinitionsHandler.getSourceDefinition(sourceDefinitionIdRequestBody));
  }

  @Override
  public SourceDefinitionRead getSourceDefinitionForWorkspace(final SourceDefinitionIdWithWorkspaceId sourceDefinitionIdWithWorkspaceId) {
    return execute(() -> sourceDefinitionsHandler.getSourceDefinitionForWorkspace(sourceDefinitionIdWithWorkspaceId));
  }

  // TODO: Deprecate this route in favor of createCustomSourceDefinition
  // since all connector definitions created through the API are custom
  @Override
  public SourceDefinitionRead createSourceDefinition(final SourceDefinitionCreate sourceDefinitionCreate) {
    return execute(() -> sourceDefinitionsHandler.createPrivateSourceDefinition(sourceDefinitionCreate));
  }

  @Override
  public SourceDefinitionRead createCustomSourceDefinition(final CustomSourceDefinitionCreate customSourceDefinitionCreate) {
    return execute(() -> sourceDefinitionsHandler.createCustomSourceDefinition(customSourceDefinitionCreate));
  }

  @Override
  public SourceDefinitionRead updateSourceDefinition(final SourceDefinitionUpdate sourceDefinitionUpdate) {
    return execute(() -> sourceDefinitionsHandler.updateSourceDefinition(sourceDefinitionUpdate));
  }

  @Override
  public SourceDefinitionRead updateCustomSourceDefinition(final CustomSourceDefinitionUpdate customSourceDefinitionUpdate) {
    return execute(() -> sourceDefinitionsHandler.updateCustomSourceDefinition(customSourceDefinitionUpdate));
  }

  @Override
  public void deleteSourceDefinition(final SourceDefinitionIdRequestBody sourceDefinitionIdRequestBody) {
    execute(() -> {
      sourceDefinitionsHandler.deleteSourceDefinition(sourceDefinitionIdRequestBody);
      return null;
    });
  }

  @Override
  public void deleteCustomSourceDefinition(final SourceDefinitionIdWithWorkspaceId sourceDefinitionIdWithWorkspaceId) {
    execute(() -> {
      sourceDefinitionsHandler.deleteCustomSourceDefinition(sourceDefinitionIdWithWorkspaceId);
      return null;
    });
  }

  @Override
  public PrivateSourceDefinitionRead grantSourceDefinitionToWorkspace(final SourceDefinitionIdWithWorkspaceId sourceDefinitionIdWithWorkspaceId) {
    return execute(() -> sourceDefinitionsHandler.grantSourceDefinitionToWorkspace(sourceDefinitionIdWithWorkspaceId));
  }

  @Override
  public void revokeSourceDefinitionFromWorkspace(final SourceDefinitionIdWithWorkspaceId sourceDefinitionIdWithWorkspaceId) {
    execute(() -> {
      sourceDefinitionsHandler.revokeSourceDefinitionFromWorkspace(sourceDefinitionIdWithWorkspaceId);
      return null;
    });
  }

  // SOURCE SPECIFICATION

  @Override
  public SourceDefinitionSpecificationRead getSourceDefinitionSpecification(final SourceDefinitionIdWithWorkspaceId sourceDefinitionIdWithWorkspaceId) {
    return execute(() -> schedulerHandler.getSourceDefinitionSpecification(sourceDefinitionIdWithWorkspaceId));
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
  public SourceRead cloneSource(final SourceCloneRequestBody sourceCloneRequestBody) {
    return execute(() -> sourceHandler.cloneSource(sourceCloneRequestBody));
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
  public SourceDiscoverSchemaRead discoverSchemaForSource(final SourceDiscoverSchemaRequestBody discoverSchemaRequestBody) {
    return execute(() -> schedulerHandler.discoverSchemaForSourceFromSourceId(discoverSchemaRequestBody));
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
  public DestinationDefinitionReadList listDestinationDefinitionsForWorkspace(final WorkspaceIdRequestBody workspaceIdRequestBody) {
    return execute(() -> destinationDefinitionsHandler.listDestinationDefinitionsForWorkspace(workspaceIdRequestBody));
  }

  @Override
  public DestinationDefinitionReadList listLatestDestinationDefinitions() {
    return execute(destinationDefinitionsHandler::listLatestDestinationDefinitions);
  }

  @Override
  public PrivateDestinationDefinitionReadList listPrivateDestinationDefinitions(final WorkspaceIdRequestBody workspaceIdRequestBody) {
    return execute(() -> destinationDefinitionsHandler.listPrivateDestinationDefinitions(workspaceIdRequestBody));
  }

  @Override
  public DestinationDefinitionRead getDestinationDefinition(final DestinationDefinitionIdRequestBody destinationDefinitionIdRequestBody) {
    return execute(() -> destinationDefinitionsHandler.getDestinationDefinition(destinationDefinitionIdRequestBody));
  }

  @Override
  public DestinationDefinitionRead getDestinationDefinitionForWorkspace(
                                                                        final DestinationDefinitionIdWithWorkspaceId destinationDefinitionIdWithWorkspaceId) {
    return execute(() -> destinationDefinitionsHandler.getDestinationDefinitionForWorkspace(destinationDefinitionIdWithWorkspaceId));
  }

  // TODO: Deprecate this route in favor of createCustomDestinationDefinition
  // since all connector definitions created through the API are custom
  @Override
  public DestinationDefinitionRead createDestinationDefinition(final DestinationDefinitionCreate destinationDefinitionCreate) {
    return execute(() -> destinationDefinitionsHandler.createPrivateDestinationDefinition(destinationDefinitionCreate));
  }

  @Override
  public DestinationDefinitionRead createCustomDestinationDefinition(final CustomDestinationDefinitionCreate customDestinationDefinitionCreate) {
    return execute(() -> destinationDefinitionsHandler.createCustomDestinationDefinition(customDestinationDefinitionCreate));
  }

  @Override
  public DestinationDefinitionRead updateDestinationDefinition(final DestinationDefinitionUpdate destinationDefinitionUpdate) {
    return execute(() -> destinationDefinitionsHandler.updateDestinationDefinition(destinationDefinitionUpdate));
  }

  @Override
  public DestinationDefinitionRead updateCustomDestinationDefinition(final CustomDestinationDefinitionUpdate customDestinationDefinitionUpdate) {
    return execute(() -> destinationDefinitionsHandler.updateCustomDestinationDefinition(customDestinationDefinitionUpdate));
  }

  @Override
  public void deleteDestinationDefinition(final DestinationDefinitionIdRequestBody destinationDefinitionIdRequestBody) {
    execute(() -> {
      destinationDefinitionsHandler.deleteDestinationDefinition(destinationDefinitionIdRequestBody);
      return null;
    });
  }

  @Override
  public void deleteCustomDestinationDefinition(final DestinationDefinitionIdWithWorkspaceId destinationDefinitionIdWithWorkspaceId) {
    execute(() -> {
      destinationDefinitionsHandler.deleteCustomDestinationDefinition(destinationDefinitionIdWithWorkspaceId);
      return null;
    });
  }

  @Override
  public PrivateDestinationDefinitionRead grantDestinationDefinitionToWorkspace(
                                                                                final DestinationDefinitionIdWithWorkspaceId destinationDefinitionIdWithWorkspaceId) {
    return execute(() -> destinationDefinitionsHandler.grantDestinationDefinitionToWorkspace(destinationDefinitionIdWithWorkspaceId));
  }

  @Override
  public void revokeDestinationDefinitionFromWorkspace(final DestinationDefinitionIdWithWorkspaceId destinationDefinitionIdWithWorkspaceId) {
    execute(() -> {
      destinationDefinitionsHandler.revokeDestinationDefinitionFromWorkspace(destinationDefinitionIdWithWorkspaceId);
      return null;
    });
  }

  // DESTINATION SPECIFICATION

  @Override
  public DestinationDefinitionSpecificationRead getDestinationDefinitionSpecification(
                                                                                      final DestinationDefinitionIdWithWorkspaceId destinationDefinitionIdWithWorkspaceId) {
    return execute(() -> schedulerHandler.getDestinationSpecification(destinationDefinitionIdWithWorkspaceId));
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
  public DestinationRead cloneDestination(final DestinationCloneRequestBody destinationCloneRequestBody) {
    return execute(() -> destinationHandler.cloneDestination(destinationCloneRequestBody));
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
  public ConnectionState createOrUpdateState(final ConnectionStateCreateOrUpdate connectionStateCreateOrUpdate) {
    return execute(() -> stateHandler.createOrUpdateState(connectionStateCreateOrUpdate));
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
    return execute(() -> stateHandler.getState(connectionIdRequestBody));
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
  public JobDebugInfoRead getJobDebugInfo(final JobIdRequestBody jobIdRequestBody) {
    return execute(() -> jobHistoryHandler.getJobDebugInfo(jobIdRequestBody));
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

  @Override
  public ConnectionStateType getStateType(final ConnectionIdRequestBody connectionIdRequestBody) {
    return execute(() -> webBackendConnectionsHandler.getStateType(connectionIdRequestBody));
  }

  @Override
  public WebBackendWorkspaceStateResult webBackendGetWorkspaceState(final WebBackendWorkspaceState webBackendWorkspaceState) {
    return execute(() -> webBackendConnectionsHandler.getWorkspaceState(webBackendWorkspaceState));
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

  @Override
  public InternalOperationResult setWorkflowInAttempt(final SetWorkflowInAttemptRequestBody requestBody) {
    return execute(() -> attemptHandler.setWorkflowInAttempt(requestBody));
  }

  public boolean canImportDefinitions() {
    return archiveHandler.canImportDefinitions();
  }

  private static <T> T execute(final HandlerCall<T> call) {
    try {
      return call.call();
    } catch (final ConfigNotFoundException e) {
      throw new IdNotFoundKnownException(String.format("Could not find configuration for %s: %s.", e.getType(), e.getConfigId()),
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
