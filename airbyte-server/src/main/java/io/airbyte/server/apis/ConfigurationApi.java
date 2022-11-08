/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis;

import io.airbyte.analytics.TrackingClient;
import io.airbyte.api.model.generated.AttemptNormalizationStatusReadList;
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
import io.airbyte.api.model.generated.InternalOperationResult;
import io.airbyte.api.model.generated.JobDebugInfoRead;
import io.airbyte.api.model.generated.JobIdRequestBody;
import io.airbyte.api.model.generated.JobInfoLightRead;
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
import io.airbyte.api.model.generated.SaveStatsRequestBody;
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
import io.airbyte.api.model.generated.WebBackendConnectionCreate;
import io.airbyte.api.model.generated.WebBackendConnectionRead;
import io.airbyte.api.model.generated.WebBackendConnectionReadList;
import io.airbyte.api.model.generated.WebBackendConnectionRequestBody;
import io.airbyte.api.model.generated.WebBackendConnectionUpdate;
import io.airbyte.api.model.generated.WebBackendGeographiesListResult;
import io.airbyte.api.model.generated.WebBackendWorkspaceState;
import io.airbyte.api.model.generated.WebBackendWorkspaceStateResult;
import io.airbyte.api.model.generated.WorkspaceCreate;
import io.airbyte.api.model.generated.WorkspaceGiveFeedback;
import io.airbyte.api.model.generated.WorkspaceIdRequestBody;
import io.airbyte.api.model.generated.WorkspaceRead;
import io.airbyte.api.model.generated.WorkspaceReadList;
import io.airbyte.api.model.generated.WorkspaceUpdate;
import io.airbyte.api.model.generated.WorkspaceUpdateName;
import io.airbyte.commons.version.AirbyteVersion;
import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.helpers.LogConfigs;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.SecretsRepositoryReader;
import io.airbyte.config.persistence.SecretsRepositoryWriter;
import io.airbyte.persistence.job.JobPersistence;
import io.airbyte.persistence.job.WorkspaceHelper;
import io.airbyte.server.errors.BadObjectSchemaKnownException;
import io.airbyte.server.errors.IdNotFoundKnownException;
import io.airbyte.server.handlers.ConnectionsHandler;
import io.airbyte.server.handlers.DestinationDefinitionsHandler;
import io.airbyte.server.handlers.DestinationHandler;
import io.airbyte.server.handlers.JobHistoryHandler;
import io.airbyte.server.handlers.SchedulerHandler;
import io.airbyte.server.handlers.SourceDefinitionsHandler;
import io.airbyte.server.handlers.SourceHandler;
import io.airbyte.server.handlers.WorkspacesHandler;
import io.airbyte.server.scheduler.EventRunner;
import io.airbyte.server.scheduler.SynchronousSchedulerClient;
import io.airbyte.validation.json.JsonSchemaValidator;
import io.airbyte.validation.json.JsonValidationException;
import java.io.File;
import java.io.IOException;
import java.util.Map;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.NotImplementedException;

@javax.ws.rs.Path("/v1")
@Slf4j
public class ConfigurationApi implements io.airbyte.api.generated.V1Api {

  private final WorkspacesHandler workspacesHandler;
  private final SourceDefinitionsHandler sourceDefinitionsHandler;
  private final SourceHandler sourceHandler;
  private final DestinationDefinitionsHandler destinationDefinitionsHandler;
  private final DestinationHandler destinationHandler;
  private final ConnectionsHandler connectionsHandler;
  private final SchedulerHandler schedulerHandler;
  private final JobHistoryHandler jobHistoryHandler;

  public ConfigurationApi(final ConfigRepository configRepository,
                          final JobPersistence jobPersistence,
                          final SecretsRepositoryReader secretsRepositoryReader,
                          final SecretsRepositoryWriter secretsRepositoryWriter,
                          final SynchronousSchedulerClient synchronousSchedulerClient,
                          final TrackingClient trackingClient,
                          final WorkerEnvironment workerEnvironment,
                          final LogConfigs logConfigs,
                          final AirbyteVersion airbyteVersion,
                          final EventRunner eventRunner) {

    final JsonSchemaValidator schemaValidator = new JsonSchemaValidator();

    final WorkspaceHelper workspaceHelper = new WorkspaceHelper(configRepository, jobPersistence);

    connectionsHandler = new ConnectionsHandler(
        configRepository,
        workspaceHelper,
        trackingClient,
        eventRunner);

    schedulerHandler = new SchedulerHandler(
        configRepository,
        secretsRepositoryReader,
        secretsRepositoryWriter,
        synchronousSchedulerClient,
        jobPersistence,
        workerEnvironment,
        logConfigs,
        eventRunner,
        connectionsHandler);

    sourceHandler = new SourceHandler(
        configRepository,
        secretsRepositoryReader,
        secretsRepositoryWriter,
        schemaValidator,
        connectionsHandler);
    sourceDefinitionsHandler = new SourceDefinitionsHandler(configRepository, synchronousSchedulerClient, sourceHandler);
    destinationHandler = new DestinationHandler(
        configRepository,
        secretsRepositoryReader,
        secretsRepositoryWriter,
        schemaValidator,
        connectionsHandler);
    destinationDefinitionsHandler = new DestinationDefinitionsHandler(configRepository, synchronousSchedulerClient, destinationHandler);
    workspacesHandler = new WorkspacesHandler(
        configRepository,
        secretsRepositoryWriter,
        connectionsHandler,
        destinationHandler,
        sourceHandler);
    jobHistoryHandler = new JobHistoryHandler(jobPersistence, workerEnvironment, logConfigs, connectionsHandler, sourceHandler,
        sourceDefinitionsHandler, destinationHandler, destinationDefinitionsHandler, airbyteVersion);
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
  public WorkspaceRead getWorkspaceByConnectionId(final ConnectionIdRequestBody connectionIdRequestBody) {
    return execute(() -> workspacesHandler.getWorkspaceByConnectionId(connectionIdRequestBody));
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

  /**
   * This implementation has been moved to {@link AttemptApiController}. Since the path of
   * {@link AttemptApiController} is more granular, it will override this implementation
   */
  @Override
  public NotificationRead tryNotificationConfig(final Notification notification) {
    throw new NotImplementedException();
  }

  // SOURCE

  /**
   * This implementation has been moved to {@link SourceDefinitionApiController}. Since the path of
   * {@link SourceDefinitionApiController} is more granular, it will override this implementation
   */
  @Override
  public SourceDefinitionReadList listSourceDefinitions() {
    throw new NotImplementedException();
  }

  /**
   * This implementation has been moved to {@link SourceDefinitionApiController}. Since the path of
   * {@link SourceDefinitionApiController} is more granular, it will override this implementation
   */
  @Override
  public SourceDefinitionReadList listSourceDefinitionsForWorkspace(final WorkspaceIdRequestBody workspaceIdRequestBody) {
    throw new NotImplementedException();
  }

  /**
   * This implementation has been moved to {@link SourceDefinitionApiController}. Since the path of
   * {@link SourceDefinitionApiController} is more granular, it will override this implementation
   */
  @Override
  public SourceDefinitionReadList listLatestSourceDefinitions() {
    throw new NotImplementedException();
  }

  /**
   * This implementation has been moved to {@link SourceDefinitionApiController}. Since the path of
   * {@link SourceDefinitionApiController} is more granular, it will override this implementation
   */
  @Override
  public PrivateSourceDefinitionReadList listPrivateSourceDefinitions(final WorkspaceIdRequestBody workspaceIdRequestBody) {
    throw new NotImplementedException();
  }

  /**
   * This implementation has been moved to {@link SourceDefinitionApiController}. Since the path of
   * {@link SourceDefinitionApiController} is more granular, it will override this implementation
   */
  @Override
  public SourceDefinitionRead getSourceDefinition(final SourceDefinitionIdRequestBody sourceDefinitionIdRequestBody) {
    throw new NotImplementedException();
  }

  /**
   * This implementation has been moved to {@link SourceDefinitionApiController}. Since the path of
   * {@link SourceDefinitionApiController} is more granular, it will override this implementation
   */
  @Override
  public SourceDefinitionRead getSourceDefinitionForWorkspace(final SourceDefinitionIdWithWorkspaceId sourceDefinitionIdWithWorkspaceId) {
    throw new NotImplementedException();
  }

  // TODO: Deprecate this route in favor of createCustomSourceDefinition
  // since all connector definitions created through the API are custom
  /**
   * This implementation has been moved to {@link SourceDefinitionApiController}. Since the path of
   * {@link SourceDefinitionApiController} is more granular, it will override this implementation
   */
  @Override
  public SourceDefinitionRead createSourceDefinition(final SourceDefinitionCreate sourceDefinitionCreate) {
    throw new NotImplementedException();
  }

  /**
   * This implementation has been moved to {@link SourceDefinitionApiController}. Since the path of
   * {@link SourceDefinitionApiController} is more granular, it will override this implementation
   */
  @Override
  public SourceDefinitionRead createCustomSourceDefinition(final CustomSourceDefinitionCreate customSourceDefinitionCreate) {
    throw new NotImplementedException();
  }

  /**
   * This implementation has been moved to {@link SourceDefinitionApiController}. Since the path of
   * {@link SourceDefinitionApiController} is more granular, it will override this implementation
   */
  @Override
  public SourceDefinitionRead updateSourceDefinition(final SourceDefinitionUpdate sourceDefinitionUpdate) {
    throw new NotImplementedException();
  }

  /**
   * This implementation has been moved to {@link SourceDefinitionApiController}. Since the path of
   * {@link SourceDefinitionApiController} is more granular, it will override this implementation
   */
  @Override
  public SourceDefinitionRead updateCustomSourceDefinition(final CustomSourceDefinitionUpdate customSourceDefinitionUpdate) {
    throw new NotImplementedException();
  }

  /**
   * This implementation has been moved to {@link SourceDefinitionApiController}. Since the path of
   * {@link SourceDefinitionApiController} is more granular, it will override this implementation
   */
  @Override
  public void deleteSourceDefinition(final SourceDefinitionIdRequestBody sourceDefinitionIdRequestBody) {
    throw new NotImplementedException();
  }

  /**
   * This implementation has been moved to {@link SourceDefinitionApiController}. Since the path of
   * {@link SourceDefinitionApiController} is more granular, it will override this implementation
   */
  @Override
  public void deleteCustomSourceDefinition(final SourceDefinitionIdWithWorkspaceId sourceDefinitionIdWithWorkspaceId) {
    throw new NotImplementedException();
  }

  /**
   * This implementation has been moved to {@link SourceDefinitionApiController}. Since the path of
   * {@link SourceDefinitionApiController} is more granular, it will override this implementation
   */
  @Override
  public PrivateSourceDefinitionRead grantSourceDefinitionToWorkspace(final SourceDefinitionIdWithWorkspaceId sourceDefinitionIdWithWorkspaceId) {
    throw new NotImplementedException();
  }

  /**
   * This implementation has been moved to {@link SourceDefinitionApiController}. Since the path of
   * {@link SourceDefinitionApiController} is more granular, it will override this implementation
   */
  @Override
  public void revokeSourceDefinitionFromWorkspace(final SourceDefinitionIdWithWorkspaceId sourceDefinitionIdWithWorkspaceId) {
    throw new NotImplementedException();
  }

  @Override
  public InternalOperationResult saveStats(final SaveStatsRequestBody saveStatsRequestBody) {
    throw new NotImplementedException();
  }

  // SOURCE SPECIFICATION

  @Override
  public SourceDefinitionSpecificationRead getSourceDefinitionSpecification(final SourceDefinitionIdWithWorkspaceId sourceDefinitionIdWithWorkspaceId) {
    return execute(() -> schedulerHandler.getSourceDefinitionSpecification(sourceDefinitionIdWithWorkspaceId));
  }

  // OAUTH

  /**
   * This implementation has been moved to {@link SourceOauthApiController}. Since the path of
   * {@link SourceOauthApiController} is more granular, it will override this implementation
   */
  @Override
  public OAuthConsentRead getSourceOAuthConsent(final SourceOauthConsentRequest sourceOauthConsentRequest) {
    throw new NotImplementedException();
  }

  /**
   * This implementation has been moved to {@link SourceOauthApiController}. Since the path of
   * {@link SourceOauthApiController} is more granular, it will override this implementation
   */
  @Override
  public Map<String, Object> completeSourceOAuth(final CompleteSourceOauthRequest completeSourceOauthRequest) {
    throw new NotImplementedException();
  }

  /**
   * This implementation has been moved to {@link DestinationOauthApiController}. Since the path of
   * {@link DestinationOauthApiController} is more granular, it will override this implementation
   */
  @Override
  public OAuthConsentRead getDestinationOAuthConsent(final DestinationOauthConsentRequest destinationOauthConsentRequest) {
    throw new NotImplementedException();
  }

  /**
   * This implementation has been moved to {@link DestinationOauthApiController}. Since the path of
   * {@link DestinationOauthApiController} is more granular, it will override this implementation
   */
  @Override
  public Map<String, Object> completeDestinationOAuth(final CompleteDestinationOAuthRequest requestBody) {
    throw new NotImplementedException();
  }

  /**
   * This implementation has been moved to {@link DestinationOauthApiController}. Since the path of
   * {@link DestinationOauthApiController} is more granular, it will override this implementation
   */
  @Override
  public void setInstancewideDestinationOauthParams(final SetInstancewideDestinationOauthParamsRequestBody requestBody) {
    throw new NotImplementedException();
  }

  /**
   * This implementation has been moved to {@link SourceOauthApiController}. Since the path of
   * {@link SourceOauthApiController} is more granular, it will override this implementation
   */
  @Override
  public void setInstancewideSourceOauthParams(final SetInstancewideSourceOauthParamsRequestBody requestBody) {
    throw new NotImplementedException();
  }

  /**
   * This implementation has been moved to {@link AttemptApiController}. Since the path of
   * {@link AttemptApiController} is more granular, it will override this implementation
   */
  @Override
  public InternalOperationResult setWorkflowInAttempt(final SetWorkflowInAttemptRequestBody setWorkflowInAttemptRequestBody) {
    throw new NotImplementedException();
  }

  // SOURCE IMPLEMENTATION

  /**
   * This implementation has been moved to {@link SourceApiController}. Since the path of
   * {@link SourceApiController} is more granular, it will override this implementation
   */
  @Override
  public SourceRead createSource(final SourceCreate sourceCreate) {
    throw new NotImplementedException();
  }

  /**
   * This implementation has been moved to {@link SourceApiController}. Since the path of
   * {@link SourceApiController} is more granular, it will override this implementation
   */
  @Override
  public SourceRead updateSource(final SourceUpdate sourceUpdate) {
    throw new NotImplementedException();
  }

  /**
   * This implementation has been moved to {@link SourceApiController}. Since the path of
   * {@link SourceApiController} is more granular, it will override this implementation
   */
  @Override
  public SourceReadList listSourcesForWorkspace(final WorkspaceIdRequestBody workspaceIdRequestBody) {
    throw new NotImplementedException();
  }

  /**
   * This implementation has been moved to {@link SourceApiController}. Since the path of
   * {@link SourceApiController} is more granular, it will override this implementation
   */
  @Override
  public SourceReadList searchSources(final SourceSearch sourceSearch) {
    throw new NotImplementedException();
  }

  /**
   * This implementation has been moved to {@link SourceApiController}. Since the path of
   * {@link SourceApiController} is more granular, it will override this implementation
   */
  @Override
  public SourceRead getSource(final SourceIdRequestBody sourceIdRequestBody) {
    throw new NotImplementedException();
  }

  /**
   * This implementation has been moved to {@link SourceApiController}. Since the path of
   * {@link SourceApiController} is more granular, it will override this implementation
   */
  @Override
  public void deleteSource(final SourceIdRequestBody sourceIdRequestBody) {
    throw new NotImplementedException();
  }

  /**
   * This implementation has been moved to {@link SourceApiController}. Since the path of
   * {@link SourceApiController} is more granular, it will override this implementation
   */
  @Override
  public SourceRead cloneSource(final SourceCloneRequestBody sourceCloneRequestBody) {
    throw new NotImplementedException();
  }

  /**
   * This implementation has been moved to {@link SourceApiController}. Since the path of
   * {@link SourceApiController} is more granular, it will override this implementation
   */
  @Override
  public CheckConnectionRead checkConnectionToSource(final SourceIdRequestBody sourceIdRequestBody) {
    throw new NotImplementedException();
  }

  /**
   * This implementation has been moved to {@link SourceApiController}. Since the path of
   * {@link SourceApiController} is more granular, it will override this implementation
   */
  @Override
  public CheckConnectionRead checkConnectionToSourceForUpdate(final SourceUpdate sourceUpdate) {
    throw new NotImplementedException();
  }

  /**
   * This implementation has been moved to {@link SourceApiController}. Since the path of
   * {@link SourceApiController} is more granular, it will override this implementation
   */
  @Override
  public SourceDiscoverSchemaRead discoverSchemaForSource(final SourceDiscoverSchemaRequestBody discoverSchemaRequestBody) {
    throw new NotImplementedException();
  }

  // DB MIGRATION

  /**
   * This implementation has been moved to {@link DbMigrationApiController}. Since the path of
   * {@link DbMigrationApiController} is more granular, it will override this implementation
   */
  @Override
  public DbMigrationReadList listMigrations(final DbMigrationRequestBody request) {
    throw new NotImplementedException();
  }

  /**
   * This implementation has been moved to {@link DbMigrationApiController}. Since the path of
   * {@link DbMigrationApiController} is more granular, it will override this implementation
   */
  @Override
  public DbMigrationExecutionRead executeMigrations(final DbMigrationRequestBody request) {
    throw new NotImplementedException();
  }

  // DESTINATION

  /**
   * This implementation has been moved to {@link DestinationDefinitionApiController}. Since the path
   * of {@link DestinationDefinitionApiController} is more granular, it will override this
   * implementation
   */
  @Override
  public DestinationDefinitionReadList listDestinationDefinitions() {
    throw new NotImplementedException();
  }

  /**
   * This implementation has been moved to {@link DestinationDefinitionApiController}. Since the path
   * of {@link DestinationDefinitionApiController} is more granular, it will override this
   * implementation
   */
  @Override
  public DestinationDefinitionReadList listDestinationDefinitionsForWorkspace(final WorkspaceIdRequestBody workspaceIdRequestBody) {
    throw new NotImplementedException();
  }

  /**
   * This implementation has been moved to {@link DestinationDefinitionApiController}. Since the path
   * of {@link DestinationDefinitionApiController} is more granular, it will override this
   * implementation
   */
  @Override
  public DestinationDefinitionReadList listLatestDestinationDefinitions() {
    throw new NotImplementedException();
  }

  /**
   * This implementation has been moved to {@link DestinationDefinitionApiController}. Since the path
   * of {@link DestinationDefinitionApiController} is more granular, it will override this
   * implementation
   */
  @Override
  public PrivateDestinationDefinitionReadList listPrivateDestinationDefinitions(final WorkspaceIdRequestBody workspaceIdRequestBody) {
    throw new NotImplementedException();
  }

  /**
   * This implementation has been moved to {@link DestinationDefinitionApiController}. Since the path
   * of {@link DestinationDefinitionApiController} is more granular, it will override this
   * implementation
   */
  @Override
  public DestinationDefinitionRead getDestinationDefinition(final DestinationDefinitionIdRequestBody destinationDefinitionIdRequestBody) {
    throw new NotImplementedException();
  }

  /**
   * This implementation has been moved to {@link DestinationDefinitionApiController}. Since the path
   * of {@link DestinationDefinitionApiController} is more granular, it will override this
   * implementation
   */
  @Override
  public DestinationDefinitionRead getDestinationDefinitionForWorkspace(
                                                                        final DestinationDefinitionIdWithWorkspaceId destinationDefinitionIdWithWorkspaceId) {
    throw new NotImplementedException();
  }

  /**
   * This implementation has been moved to {@link DestinationDefinitionApiController}. Since the path
   * of {@link DestinationDefinitionApiController} is more granular, it will override this
   * implementation
   */
  // TODO: Deprecate this route in favor of createCustomDestinationDefinition
  // since all connector definitions created through the API are custom
  @Override
  public DestinationDefinitionRead createDestinationDefinition(final DestinationDefinitionCreate destinationDefinitionCreate) {
    throw new NotImplementedException();
  }

  /**
   * This implementation has been moved to {@link DestinationDefinitionApiController}. Since the path
   * of {@link DestinationDefinitionApiController} is more granular, it will override this
   * implementation
   */
  @Override
  public DestinationDefinitionRead createCustomDestinationDefinition(final CustomDestinationDefinitionCreate customDestinationDefinitionCreate) {
    throw new NotImplementedException();
  }

  /**
   * This implementation has been moved to {@link DestinationDefinitionApiController}. Since the path
   * of {@link DestinationDefinitionApiController} is more granular, it will override this
   * implementation
   */
  @Override
  public DestinationDefinitionRead updateDestinationDefinition(final DestinationDefinitionUpdate destinationDefinitionUpdate) {
    throw new NotImplementedException();
  }

  /**
   * This implementation has been moved to {@link DestinationDefinitionApiController}. Since the path
   * of {@link DestinationDefinitionApiController} is more granular, it will override this
   * implementation
   */
  @Override
  public DestinationDefinitionRead updateCustomDestinationDefinition(final CustomDestinationDefinitionUpdate customDestinationDefinitionUpdate) {
    throw new NotImplementedException();
  }

  /**
   * This implementation has been moved to {@link DestinationDefinitionApiController}. Since the path
   * of {@link DestinationDefinitionApiController} is more granular, it will override this
   * implementation
   */
  @Override
  public void deleteDestinationDefinition(final DestinationDefinitionIdRequestBody destinationDefinitionIdRequestBody) {
    throw new NotImplementedException();
  }

  /**
   * This implementation has been moved to {@link DestinationDefinitionApiController}. Since the path
   * of {@link DestinationDefinitionApiController} is more granular, it will override this
   * implementation
   */
  @Override
  public void deleteCustomDestinationDefinition(final DestinationDefinitionIdWithWorkspaceId destinationDefinitionIdWithWorkspaceId) {
    throw new NotImplementedException();
  }

  /**
   * This implementation has been moved to {@link DestinationDefinitionApiController}. Since the path
   * of {@link DestinationDefinitionApiController} is more granular, it will override this
   * implementation
   */
  @Override
  public PrivateDestinationDefinitionRead grantDestinationDefinitionToWorkspace(
                                                                                final DestinationDefinitionIdWithWorkspaceId destinationDefinitionIdWithWorkspaceId) {
    throw new NotImplementedException();
  }

  /**
   * This implementation has been moved to {@link DestinationDefinitionApiController}. Since the path
   * of {@link DestinationDefinitionApiController} is more granular, it will override this
   * implementation
   */
  @Override
  public void revokeDestinationDefinitionFromWorkspace(final DestinationDefinitionIdWithWorkspaceId destinationDefinitionIdWithWorkspaceId) {
    throw new NotImplementedException();
  }

  // DESTINATION SPECIFICATION
  /**
   * This implementation has been moved to {@link DestinationDefinitionSpecificationApiController}.
   * Since the path of {@link DestinationDefinitionSpecificationApiController} is more granular, it
   * will override this implementation
   */
  @Override
  public DestinationDefinitionSpecificationRead getDestinationDefinitionSpecification(
                                                                                      final DestinationDefinitionIdWithWorkspaceId destinationDefinitionIdWithWorkspaceId) {
    throw new NotImplementedException();
  }

  // DESTINATION IMPLEMENTATION

  /**
   * This implementation has been moved to {@link DestinationApiController}. Since the path of
   * {@link DestinationApiController} is more granular, it will override this implementation
   */
  @Override
  public DestinationRead createDestination(final DestinationCreate destinationCreate) {
    throw new NotImplementedException();
  }

  /**
   * This implementation has been moved to {@link DestinationApiController}. Since the path of
   * {@link DestinationApiController} is more granular, it will override this implementation
   */
  @Override
  public void deleteDestination(final DestinationIdRequestBody destinationIdRequestBody) {
    throw new NotImplementedException();
  }

  /**
   * This implementation has been moved to {@link DestinationApiController}. Since the path of
   * {@link DestinationApiController} is more granular, it will override this implementation
   */
  @Override
  public DestinationRead updateDestination(final DestinationUpdate destinationUpdate) {
    throw new NotImplementedException();
  }

  /**
   * This implementation has been moved to {@link DestinationApiController}. Since the path of
   * {@link DestinationApiController} is more granular, it will override this implementation
   */
  @Override
  public DestinationReadList listDestinationsForWorkspace(final WorkspaceIdRequestBody workspaceIdRequestBody) {
    throw new NotImplementedException();
  }

  /**
   * This implementation has been moved to {@link DestinationApiController}. Since the path of
   * {@link DestinationApiController} is more granular, it will override this implementation
   */
  @Override
  public DestinationReadList searchDestinations(final DestinationSearch destinationSearch) {
    throw new NotImplementedException();
  }

  /**
   * This implementation has been moved to {@link DestinationApiController}. Since the path of
   * {@link DestinationApiController} is more granular, it will override this implementation
   */
  @Override
  public DestinationRead getDestination(final DestinationIdRequestBody destinationIdRequestBody) {
    throw new NotImplementedException();
  }

  /**
   * This implementation has been moved to {@link DestinationApiController}. Since the path of
   * {@link DestinationApiController} is more granular, it will override this implementation
   */
  @Override
  public DestinationRead cloneDestination(final DestinationCloneRequestBody destinationCloneRequestBody) {
    throw new NotImplementedException();
  }

  /**
   * This implementation has been moved to {@link DestinationApiController}. Since the path of
   * {@link DestinationApiController} is more granular, it will override this implementation
   */
  @Override
  public CheckConnectionRead checkConnectionToDestination(final DestinationIdRequestBody destinationIdRequestBody) {
    throw new NotImplementedException();
  }

  /**
   * This implementation has been moved to {@link DestinationApiController}. Since the path of
   * {@link DestinationApiController} is more granular, it will override this implementation
   */
  @Override
  public CheckConnectionRead checkConnectionToDestinationForUpdate(final DestinationUpdate destinationUpdate) {
    throw new NotImplementedException();
  }

  // CONNECTION

  /**
   * This implementation has been moved to {@link ConnectionApiController}. Since the path of
   * {@link ConnectionApiController} is more granular, it will override this implementation
   */
  @Override
  public ConnectionRead createConnection(final ConnectionCreate connectionCreate) {
    throw new NotImplementedException();
  }

  /**
   * This implementation has been moved to {@link ConnectionApiController}. Since the path of
   * {@link ConnectionApiController} is more granular, it will override this implementation
   */
  @Override
  public ConnectionRead updateConnection(final ConnectionUpdate connectionUpdate) {
    throw new NotImplementedException();
  }

  /**
   * This implementation has been moved to {@link ConnectionApiController}. Since the path of
   * {@link ConnectionApiController} is more granular, it will override this implementation
   */
  @Override
  public ConnectionReadList listConnectionsForWorkspace(final WorkspaceIdRequestBody workspaceIdRequestBody) {
    throw new NotImplementedException();
  }

  /**
   * This implementation has been moved to {@link ConnectionApiController}. Since the path of
   * {@link ConnectionApiController} is more granular, it will override this implementation
   */
  @Override
  public ConnectionReadList listAllConnectionsForWorkspace(final WorkspaceIdRequestBody workspaceIdRequestBody) {
    throw new NotImplementedException();
  }

  /**
   * This implementation has been moved to {@link ConnectionApiController}. Since the path of
   * {@link ConnectionApiController} is more granular, it will override this implementation
   */
  @Override
  public ConnectionReadList searchConnections(final ConnectionSearch connectionSearch) {
    throw new NotImplementedException();
  }

  /**
   * This implementation has been moved to {@link ConnectionApiController}. Since the path of
   * {@link ConnectionApiController} is more granular, it will override this implementation
   */
  @Override
  public ConnectionRead getConnection(final ConnectionIdRequestBody connectionIdRequestBody) {
    throw new NotImplementedException();
  }

  /**
   * This implementation has been moved to {@link ConnectionApiController}. Since the path of
   * {@link ConnectionApiController} is more granular, it will override this implementation
   */
  @Override
  public void deleteConnection(final ConnectionIdRequestBody connectionIdRequestBody) {
    throw new NotImplementedException();
  }

  /**
   * This implementation has been moved to {@link ConnectionApiController}. Since the path of
   * {@link ConnectionApiController} is more granular, it will override this implementation
   */
  @Override
  public JobInfoRead syncConnection(final ConnectionIdRequestBody connectionIdRequestBody) {
    throw new NotImplementedException();
  }

  /**
   * This implementation has been moved to {@link ConnectionApiController}. Since the path of
   * {@link ConnectionApiController} is more granular, it will override this implementation
   */
  @Override
  public JobInfoRead resetConnection(final ConnectionIdRequestBody connectionIdRequestBody) {
    throw new NotImplementedException();
  }

  // Operations

  /**
   * This implementation has been moved to {@link OperationApiController}. Since the path of
   * {@link OperationApiController} is more granular, it will override this implementation
   */
  @Override
  public CheckOperationRead checkOperation(final OperatorConfiguration operatorConfiguration) {
    throw new NotImplementedException();
  }

  /**
   * This implementation has been moved to {@link OperationApiController}. Since the path of
   * {@link OperationApiController} is more granular, it will override this implementation
   */
  @Override
  public OperationRead createOperation(final OperationCreate operationCreate) {
    throw new NotImplementedException();
  }

  /**
   * This implementation has been moved to {@link StateApiController}. Since the path of
   * {@link StateApiController} is more granular, it will override this implementation
   */
  @Override
  public ConnectionState createOrUpdateState(final ConnectionStateCreateOrUpdate connectionStateCreateOrUpdate) {
    throw new NotImplementedException();
  }

  /**
   * This implementation has been moved to {@link OperationApiController}. Since the path of
   * {@link OperationApiController} is more granular, it will override this implementation
   */
  @Override
  public void deleteOperation(final OperationIdRequestBody operationIdRequestBody) {
    throw new NotImplementedException();
  }

  /**
   * This implementation has been moved to {@link OperationApiController}. Since the path of
   * {@link OperationApiController} is more granular, it will override this implementation
   */
  @Override
  public OperationReadList listOperationsForConnection(final ConnectionIdRequestBody connectionIdRequestBody) {
    throw new NotImplementedException();
  }

  /**
   * This implementation has been moved to {@link OperationApiController}. Since the path of
   * {@link OperationApiController} is more granular, it will override this implementation
   */
  @Override
  public OperationRead getOperation(final OperationIdRequestBody operationIdRequestBody) {
    throw new NotImplementedException();
  }

  /**
   * This implementation has been moved to {@link OperationApiController}. Since the path of
   * {@link OperationApiController} is more granular, it will override this implementation
   */
  @Override
  public OperationRead updateOperation(final OperationUpdate operationUpdate) {
    throw new NotImplementedException();
  }

  /**
   * This implementation has been moved to {@link StateApiController}. Since the path of
   * {@link StateApiController} is more granular, it will override this implementation
   */
  @Override
  public ConnectionState getState(final ConnectionIdRequestBody connectionIdRequestBody) {
    throw new NotImplementedException();
  }

  // SCHEDULER
  /**
   * This implementation has been moved to {@link SchedulerApiController}. Since the path of
   * {@link SchedulerApiController} is more granular, it will override this implementation
   */
  @Override
  public CheckConnectionRead executeSourceCheckConnection(final SourceCoreConfig sourceConfig) {
    throw new NotImplementedException();
  }

  /**
   * This implementation has been moved to {@link SchedulerApiController}. Since the path of
   * {@link SchedulerApiController} is more granular, it will override this implementation
   */
  @Override
  public CheckConnectionRead executeDestinationCheckConnection(final DestinationCoreConfig destinationConfig) {
    throw new NotImplementedException();
  }

  /**
   * This implementation has been moved to {@link SchedulerApiController}. Since the path of
   * {@link SchedulerApiController} is more granular, it will override this implementation
   */
  @Override
  public SourceDiscoverSchemaRead executeSourceDiscoverSchema(final SourceCoreConfig sourceCreate) {
    throw new NotImplementedException();
  }

  /**
   * This implementation has been moved to {@link JobsApiController}. Since the path of
   * {@link JobsApiController} is more granular, it will override this implementation
   */
  @Override
  public JobInfoRead cancelJob(final JobIdRequestBody jobIdRequestBody) {
    throw new NotImplementedException();
  }

  // JOB HISTORY

  /**
   * This implementation has been moved to {@link JobsApiController}. Since the path of
   * {@link JobsApiController} is more granular, it will override this implementation
   */
  @Override
  public JobReadList listJobsFor(final JobListRequestBody jobListRequestBody) {
    throw new NotImplementedException();
  }

  /**
   * This implementation has been moved to {@link JobsApiController}. Since the path of
   * {@link JobsApiController} is more granular, it will override this implementation
   */
  @Override
  public JobInfoRead getJobInfo(final JobIdRequestBody jobIdRequestBody) {
    throw new NotImplementedException();
  }

  /**
   * This implementation has been moved to {@link JobsApiController}. Since the path of
   * {@link JobsApiController} is more granular, it will override this implementation
   */
  @Override
  public JobInfoLightRead getJobInfoLight(final JobIdRequestBody jobIdRequestBody) {
    throw new NotImplementedException();
  }

  /**
   * This implementation has been moved to {@link JobsApiController}. Since the path of
   * {@link JobsApiController} is more granular, it will override this implementation
   */
  @Override
  public JobDebugInfoRead getJobDebugInfo(final JobIdRequestBody jobIdRequestBody) {
    throw new NotImplementedException();
  }

  /**
   * This implementation has been moved to {@link JobsApiController}. Since the path of
   * {@link JobsApiController} is more granular, it will override this implementation
   */
  @Override
  public AttemptNormalizationStatusReadList getAttemptNormalizationStatusesForJob(final JobIdRequestBody jobIdRequestBody) {
    return execute(() -> jobHistoryHandler.getAttemptNormalizationStatuses(jobIdRequestBody));
  }

  /**
   * This implementation has been moved to {@link LogsApiController}. Since the path of
   * {@link LogsApiController} is more granular, it will override this implementation
   */
  @Override
  public File getLogs(final LogsRequestBody logsRequestBody) {
    throw new NotImplementedException();
  }

  /**
   * This implementation has been moved to {@link HealthApiController}. Since the path of
   * {@link HealthApiController} is more granular, it will override this implementation
   */
  @Override
  public File getOpenApiSpec() {
    throw new NotImplementedException();
  }

  // HEALTH
  /**
   * This implementation has been moved to {@link HealthApiController}. Since the path of
   * {@link HealthApiController} is more granular, it will override this implementation
   */
  @Override
  public HealthCheckRead getHealthCheck() {
    throw new NotImplementedException();
  }

  // WEB BACKEND

  /**
   * This implementation has been moved to {@link HealthApiController}. Since the path of
   * {@link HealthApiController} is more granular, it will override this implementation
   */
  @Override
  public WebBackendConnectionReadList webBackendListConnectionsForWorkspace(final WorkspaceIdRequestBody workspaceIdRequestBody) {
    throw new NotImplementedException();
  }

  /**
   * This implementation has been moved to {@link HealthApiController}. Since the path of
   * {@link HealthApiController} is more granular, it will override this implementation
   */
  @Override
  public WebBackendGeographiesListResult webBackendListGeographies() {
    throw new NotImplementedException();
  }

  /**
   * This implementation has been moved to {@link HealthApiController}. Since the path of
   * {@link HealthApiController} is more granular, it will override this implementation
   */
  @Override
  public WebBackendConnectionRead webBackendGetConnection(final WebBackendConnectionRequestBody webBackendConnectionRequestBody) {
    throw new NotImplementedException();
  }

  /**
   * This implementation has been moved to {@link HealthApiController}. Since the path of
   * {@link HealthApiController} is more granular, it will override this implementation
   */
  @Override
  public WebBackendConnectionRead webBackendCreateConnection(final WebBackendConnectionCreate webBackendConnectionCreate) {
    throw new NotImplementedException();
  }

  /**
   * This implementation has been moved to {@link HealthApiController}. Since the path of
   * {@link HealthApiController} is more granular, it will override this implementation
   */
  @Override
  public WebBackendConnectionRead webBackendUpdateConnection(final WebBackendConnectionUpdate webBackendConnectionUpdate) {
    throw new NotImplementedException();
  }

  /**
   * This implementation has been moved to {@link HealthApiController}. Since the path of
   * {@link HealthApiController} is more granular, it will override this implementation
   */
  @Override
  public ConnectionStateType getStateType(final ConnectionIdRequestBody connectionIdRequestBody) {
    throw new NotImplementedException();
  }

  /**
   * This implementation has been moved to {@link HealthApiController}. Since the path of
   * {@link HealthApiController} is more granular, it will override this implementation
   */
  @Override
  public WebBackendWorkspaceStateResult webBackendGetWorkspaceState(final WebBackendWorkspaceState webBackendWorkspaceState) {
    throw new NotImplementedException();
  }

  // TODO: Move to common when all the api are moved
  static <T> T execute(final HandlerCall<T> call) {
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

  interface HandlerCall<T> {

    T call() throws ConfigNotFoundException, IOException, JsonValidationException;

  }

}
