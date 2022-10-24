package io.airbyte.server.apis;

import io.airbyte.analytics.TrackingClient;
import io.airbyte.api.generated.ConnectionApi;
import io.airbyte.api.model.generated.ConnectionCreate;
import io.airbyte.api.model.generated.ConnectionIdRequestBody;
import io.airbyte.api.model.generated.ConnectionRead;
import io.airbyte.api.model.generated.ConnectionReadList;
import io.airbyte.api.model.generated.ConnectionSearch;
import io.airbyte.api.model.generated.ConnectionState;
import io.airbyte.api.model.generated.ConnectionStateCreateOrUpdate;
import io.airbyte.api.model.generated.ConnectionStateType;
import io.airbyte.api.model.generated.ConnectionUpdate;
import io.airbyte.api.model.generated.JobInfoRead;
import io.airbyte.api.model.generated.WorkspaceIdRequestBody;
import io.airbyte.commons.version.AirbyteVersion;
import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.helpers.LogConfigs;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.SecretsRepositoryReader;
import io.airbyte.config.persistence.SecretsRepositoryWriter;
import io.airbyte.config.persistence.StatePersistence;
import io.airbyte.persistence.job.JobPersistence;
import io.airbyte.persistence.job.WorkspaceHelper;
import io.airbyte.server.handlers.ConnectionsHandler;
import io.airbyte.server.handlers.DestinationDefinitionsHandler;
import io.airbyte.server.handlers.DestinationHandler;
import io.airbyte.server.handlers.JobHistoryHandler;
import io.airbyte.server.handlers.OperationsHandler;
import io.airbyte.server.handlers.SchedulerHandler;
import io.airbyte.server.handlers.SourceDefinitionsHandler;
import io.airbyte.server.handlers.SourceHandler;
import io.airbyte.server.handlers.StateHandler;
import io.airbyte.server.handlers.WebBackendConnectionsHandler;
import io.airbyte.server.scheduler.EventRunner;
import io.airbyte.server.scheduler.SynchronousSchedulerClient;
import io.airbyte.validation.json.JsonSchemaValidator;

public class ConnectionApiImpl implements ConnectionApi {

  private final ConnectionsHandler connectionsHandler;
  private final OperationsHandler operationsHandler;
  private final SchedulerHandler schedulerHandler;
  private final StateHandler stateHandler;
  private final WebBackendConnectionsHandler webBackendConnectionsHandler;

  public ConnectionApiImpl(final ConfigRepository configRepository,
                           final JobPersistence jobPersistence,
                           final TrackingClient trackingClient,
                           final EventRunner eventRunner,
                           final SecretsRepositoryReader secretsRepositoryReader,
                           final SecretsRepositoryWriter secretsRepositoryWriter,
                           final SynchronousSchedulerClient synchronousSchedulerClient,
                           final WorkerEnvironment workerEnvironment,
                           final LogConfigs logConfigs,
                           final StatePersistence statePersistence,
                           final AirbyteVersion airbyteVersion) {

    final JsonSchemaValidator schemaValidator = new JsonSchemaValidator();

    final WorkspaceHelper workspaceHelper = new WorkspaceHelper(configRepository, jobPersistence);

    connectionsHandler = new ConnectionsHandler(
        configRepository,
        workspaceHelper,
        trackingClient,
        eventRunner);

    operationsHandler = new OperationsHandler(configRepository);

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

    final SourceHandler sourceHandler = new SourceHandler(
        configRepository,
        secretsRepositoryReader,
        secretsRepositoryWriter,
        schemaValidator,
        connectionsHandler);

    final DestinationHandler destinationHandler = new DestinationHandler(
        configRepository,
        secretsRepositoryReader,
        secretsRepositoryWriter,
        schemaValidator,
        connectionsHandler);

    final SourceDefinitionsHandler sourceDefinitionsHandler = new SourceDefinitionsHandler(configRepository, synchronousSchedulerClient, sourceHandler);

    final DestinationDefinitionsHandler destinationDefinitionsHandler = new DestinationDefinitionsHandler(configRepository, synchronousSchedulerClient,
        destinationHandler);

    final JobHistoryHandler jobHistoryHandler = new JobHistoryHandler(jobPersistence, workerEnvironment, logConfigs, connectionsHandler, sourceHandler,
        sourceDefinitionsHandler, destinationHandler, destinationDefinitionsHandler, airbyteVersion);

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
  }

  @Override
  public ConnectionRead createConnection(final ConnectionCreate connectionCreate) {
    return ConfigurationApi.execute(() -> connectionsHandler.createConnection(connectionCreate));
  }

  @Override
  public ConnectionState createOrUpdateState(final ConnectionStateCreateOrUpdate connectionStateCreateOrUpdate) {
    return ConfigurationApi.execute(() -> stateHandler.createOrUpdateState(connectionStateCreateOrUpdate));
  }

  @Override
  public ConnectionRead updateConnection(final ConnectionUpdate connectionUpdate) {
    return ConfigurationApi.execute(() -> connectionsHandler.updateConnection(connectionUpdate));
  }

  @Override
  public ConnectionReadList listConnectionsForWorkspace(final WorkspaceIdRequestBody workspaceIdRequestBody) {
    return ConfigurationApi.execute(() -> connectionsHandler.listConnectionsForWorkspace(workspaceIdRequestBody));
  }

  @Override
  public ConnectionReadList listAllConnectionsForWorkspace(final WorkspaceIdRequestBody workspaceIdRequestBody) {
    return ConfigurationApi.execute(() -> connectionsHandler.listAllConnectionsForWorkspace(workspaceIdRequestBody));
  }

  @Override
  public ConnectionReadList searchConnections(final ConnectionSearch connectionSearch) {
    return ConfigurationApi.execute(() -> connectionsHandler.searchConnections(connectionSearch));
  }

  @Override
  public ConnectionRead getConnection(final ConnectionIdRequestBody connectionIdRequestBody) {
    return ConfigurationApi.execute(() -> connectionsHandler.getConnection(connectionIdRequestBody.getConnectionId()));
  }

  @Override
  public ConnectionState getState(final ConnectionIdRequestBody connectionIdRequestBody) {
    return ConfigurationApi.execute(() -> stateHandler.getState(connectionIdRequestBody));
  }

  @Override
  public ConnectionStateType getStateType(final ConnectionIdRequestBody connectionIdRequestBody) {
    // TODO: move to connectionHandler
    return ConfigurationApi.execute(() -> webBackendConnectionsHandler.getStateType(connectionIdRequestBody));
  }

  @Override
  public void deleteConnection(final ConnectionIdRequestBody connectionIdRequestBody) {
    ConfigurationApi.execute(() -> {
      operationsHandler.deleteOperationsForConnection(connectionIdRequestBody);
      connectionsHandler.deleteConnection(connectionIdRequestBody.getConnectionId());
      return null;
    });
  }

  @Override
  public JobInfoRead syncConnection(final ConnectionIdRequestBody connectionIdRequestBody) {
    return ConfigurationApi.execute(() -> schedulerHandler.syncConnection(connectionIdRequestBody));
  }

  @Override
  public JobInfoRead resetConnection(final ConnectionIdRequestBody connectionIdRequestBody) {
    return ConfigurationApi.execute(() -> schedulerHandler.resetConnection(connectionIdRequestBody));
  }
}
