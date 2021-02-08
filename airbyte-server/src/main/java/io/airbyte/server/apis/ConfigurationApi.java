/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.server.apis;

import io.airbyte.api.model.CheckConnectionRead;
import io.airbyte.api.model.ConnectionCreate;
import io.airbyte.api.model.ConnectionIdRequestBody;
import io.airbyte.api.model.ConnectionRead;
import io.airbyte.api.model.ConnectionReadList;
import io.airbyte.api.model.ConnectionUpdate;
import io.airbyte.api.model.DestinationCoreConfig;
import io.airbyte.api.model.DestinationCreate;
import io.airbyte.api.model.DestinationDefinitionCreate;
import io.airbyte.api.model.DestinationDefinitionIdRequestBody;
import io.airbyte.api.model.DestinationDefinitionRead;
import io.airbyte.api.model.DestinationDefinitionReadList;
import io.airbyte.api.model.DestinationDefinitionSpecificationRead;
import io.airbyte.api.model.DestinationDefinitionUpdate;
import io.airbyte.api.model.DestinationIdRequestBody;
import io.airbyte.api.model.DestinationRead;
import io.airbyte.api.model.DestinationReadList;
import io.airbyte.api.model.DestinationRecreate;
import io.airbyte.api.model.DestinationUpdate;
import io.airbyte.api.model.HealthCheckRead;
import io.airbyte.api.model.ImportRead;
import io.airbyte.api.model.JobIdRequestBody;
import io.airbyte.api.model.JobInfoRead;
import io.airbyte.api.model.JobListRequestBody;
import io.airbyte.api.model.JobReadList;
import io.airbyte.api.model.LogsRequestBody;
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
import io.airbyte.api.model.SourceRead;
import io.airbyte.api.model.SourceReadList;
import io.airbyte.api.model.SourceRecreate;
import io.airbyte.api.model.SourceUpdate;
import io.airbyte.api.model.WbConnectionRead;
import io.airbyte.api.model.WbConnectionReadList;
import io.airbyte.api.model.WebBackendConnectionRequestBody;
import io.airbyte.api.model.WebBackendConnectionUpdate;
import io.airbyte.api.model.WorkspaceIdRequestBody;
import io.airbyte.api.model.WorkspaceRead;
import io.airbyte.api.model.WorkspaceUpdate;
import io.airbyte.commons.io.FileTtlManager;
import io.airbyte.config.Configs;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.scheduler.client.CachingSchedulerJobClient;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.server.converters.SpecFetcher;
import io.airbyte.server.errors.KnownException;
import io.airbyte.server.handlers.ArchiveHandler;
import io.airbyte.server.handlers.ConnectionsHandler;
import io.airbyte.server.handlers.DestinationDefinitionsHandler;
import io.airbyte.server.handlers.DestinationHandler;
import io.airbyte.server.handlers.HealthCheckHandler;
import io.airbyte.server.handlers.JobHistoryHandler;
import io.airbyte.server.handlers.LogsHandler;
import io.airbyte.server.handlers.SchedulerHandler;
import io.airbyte.server.handlers.SourceDefinitionsHandler;
import io.airbyte.server.handlers.SourceHandler;
import io.airbyte.server.handlers.WebBackendConnectionsHandler;
import io.airbyte.server.handlers.WebBackendDestinationHandler;
import io.airbyte.server.handlers.WebBackendSourceHandler;
import io.airbyte.server.handlers.WorkspacesHandler;
import io.airbyte.server.validators.DockerImageValidator;
import io.airbyte.validation.json.JsonSchemaValidator;
import io.airbyte.validation.json.JsonValidationException;
import java.io.File;
import java.io.IOException;
import javax.validation.Valid;
import org.eclipse.jetty.http.HttpStatus;

@javax.ws.rs.Path("/v1")
public class ConfigurationApi implements io.airbyte.api.V1Api {

  private final WorkspacesHandler workspacesHandler;
  private final SourceDefinitionsHandler sourceDefinitionsHandler;
  private final SourceHandler sourceHandler;
  private final DestinationDefinitionsHandler destinationDefinitionsHandler;
  private final DestinationHandler destinationHandler;
  private final ConnectionsHandler connectionsHandler;
  private final SchedulerHandler schedulerHandler;
  private final JobHistoryHandler jobHistoryHandler;
  private final WebBackendConnectionsHandler webBackendConnectionsHandler;
  private final WebBackendSourceHandler webBackendSourceHandler;
  private final WebBackendDestinationHandler webBackendDestinationHandler;
  private final HealthCheckHandler healthCheckHandler;
  private final ArchiveHandler archiveHandler;
  private final LogsHandler logsHandler;
  private final Configs configs;

  public ConfigurationApi(final ConfigRepository configRepository,
                          final JobPersistence jobPersistence,
                          final CachingSchedulerJobClient schedulerJobClient,
                          final Configs configs,
                          final FileTtlManager archiveTtlManager) {
    final SpecFetcher specFetcher = new SpecFetcher(schedulerJobClient);
    final JsonSchemaValidator schemaValidator = new JsonSchemaValidator();
    schedulerHandler = new SchedulerHandler(configRepository, schedulerJobClient);
    workspacesHandler = new WorkspacesHandler(configRepository);
    final DockerImageValidator dockerImageValidator = new DockerImageValidator(schedulerJobClient);
    sourceDefinitionsHandler = new SourceDefinitionsHandler(configRepository, dockerImageValidator, schedulerJobClient);
    connectionsHandler = new ConnectionsHandler(configRepository);
    destinationDefinitionsHandler = new DestinationDefinitionsHandler(configRepository, dockerImageValidator, schedulerJobClient);
    destinationHandler = new DestinationHandler(configRepository, schemaValidator, specFetcher, connectionsHandler);
    sourceHandler = new SourceHandler(configRepository, schemaValidator, specFetcher, connectionsHandler);
    jobHistoryHandler = new JobHistoryHandler(jobPersistence);
    webBackendConnectionsHandler =
        new WebBackendConnectionsHandler(connectionsHandler, sourceHandler, destinationHandler, jobHistoryHandler, schedulerHandler);
    webBackendSourceHandler = new WebBackendSourceHandler(sourceHandler, schedulerHandler);
    webBackendDestinationHandler = new WebBackendDestinationHandler(destinationHandler, schedulerHandler);
    healthCheckHandler = new HealthCheckHandler(configRepository);
    archiveHandler = new ArchiveHandler(configs.getAirbyteVersion(), configRepository, jobPersistence, archiveTtlManager);
    logsHandler = new LogsHandler();
    this.configs = configs;
  }

  // WORKSPACE

  @Override
  public WorkspaceRead getWorkspace(@Valid WorkspaceIdRequestBody workspaceIdRequestBody) {
    return execute(() -> workspacesHandler.getWorkspace(workspaceIdRequestBody));
  }

  @Override
  public WorkspaceRead getWorkspaceBySlug(@Valid SlugRequestBody slugRequestBody) {
    return execute(() -> workspacesHandler.getWorkspaceBySlug(slugRequestBody));
  }

  @Override
  public WorkspaceRead updateWorkspace(@Valid WorkspaceUpdate workspaceUpdate) {
    return execute(() -> workspacesHandler.updateWorkspace(workspaceUpdate));
  }

  // SOURCE

  @Override
  public SourceDefinitionReadList listSourceDefinitions() {
    return execute(sourceDefinitionsHandler::listSourceDefinitions);
  }

  @Override
  public SourceDefinitionRead getSourceDefinition(@Valid SourceDefinitionIdRequestBody sourceDefinitionIdRequestBody) {
    return execute(() -> sourceDefinitionsHandler.getSourceDefinition(sourceDefinitionIdRequestBody));
  }

  @Override
  public SourceDefinitionRead createSourceDefinition(@Valid SourceDefinitionCreate sourceDefinitionCreate) {
    return execute(() -> sourceDefinitionsHandler.createSourceDefinition(sourceDefinitionCreate));
  }

  @Override
  public SourceDefinitionRead updateSourceDefinition(@Valid SourceDefinitionUpdate sourceDefinitionUpdate) {
    return execute(() -> sourceDefinitionsHandler.updateSourceDefinition(sourceDefinitionUpdate));
  }

  // SOURCE SPECIFICATION

  @Override
  public SourceDefinitionSpecificationRead getSourceDefinitionSpecification(@Valid SourceDefinitionIdRequestBody sourceDefinitionIdRequestBody) {
    return execute(() -> schedulerHandler.getSourceDefinitionSpecification(sourceDefinitionIdRequestBody));
  }
  // SOURCE IMPLEMENTATION

  @Override
  public SourceRead createSource(@Valid SourceCreate sourceCreate) {
    return execute(() -> sourceHandler.createSource(sourceCreate));
  }

  @Override
  public SourceRead updateSource(@Valid SourceUpdate sourceUpdate) {
    return execute(() -> sourceHandler.updateSource(sourceUpdate));
  }

  @Override
  public SourceReadList listSourcesForWorkspace(@Valid WorkspaceIdRequestBody workspaceIdRequestBody) {
    return execute(() -> sourceHandler.listSourcesForWorkspace(workspaceIdRequestBody));
  }

  @Override
  public SourceRead getSource(@Valid SourceIdRequestBody sourceIdRequestBody) {
    return execute(() -> sourceHandler.getSource(sourceIdRequestBody));
  }

  @Override
  public void deleteSource(@Valid SourceIdRequestBody sourceIdRequestBody) {
    execute(() -> {
      sourceHandler.deleteSource(sourceIdRequestBody);
      return null;
    });
  }

  @Override
  public CheckConnectionRead checkConnectionToSource(@Valid SourceIdRequestBody sourceIdRequestBody) {
    return execute(() -> schedulerHandler.checkSourceConnectionFromSourceId(sourceIdRequestBody));
  }

  @Override
  public CheckConnectionRead checkConnectionToSourceForUpdate(@Valid SourceUpdate sourceUpdate) {
    return execute(() -> schedulerHandler.checkSourceConnectionFromSourceIdForUpdate(sourceUpdate));
  }

  @Override
  public SourceDiscoverSchemaRead discoverSchemaForSource(@Valid SourceIdRequestBody sourceIdRequestBody) {
    return execute(() -> schedulerHandler.discoverSchemaForSourceFromSourceId(sourceIdRequestBody));
  }

  // DESTINATION

  @Override
  public DestinationDefinitionReadList listDestinationDefinitions() {
    return execute(destinationDefinitionsHandler::listDestinationDefinitions);
  }

  @Override
  public DestinationDefinitionRead getDestinationDefinition(@Valid DestinationDefinitionIdRequestBody destinationDefinitionIdRequestBody) {
    return execute(() -> destinationDefinitionsHandler.getDestinationDefinition(destinationDefinitionIdRequestBody));
  }

  @Override
  public DestinationDefinitionRead createDestinationDefinition(@Valid DestinationDefinitionCreate destinationDefinitionCreate) {
    return execute(() -> destinationDefinitionsHandler.createDestinationDefinition(destinationDefinitionCreate));
  }

  @Override
  public DestinationDefinitionRead updateDestinationDefinition(@Valid DestinationDefinitionUpdate destinationDefinitionUpdate) {
    return execute(() -> destinationDefinitionsHandler.updateDestinationDefinition(destinationDefinitionUpdate));
  }

  // DESTINATION SPECIFICATION

  @Override
  public DestinationDefinitionSpecificationRead getDestinationDefinitionSpecification(@Valid DestinationDefinitionIdRequestBody destinationDefinitionIdRequestBody) {
    return execute(() -> schedulerHandler.getDestinationSpecification(destinationDefinitionIdRequestBody));
  }

  // DESTINATION IMPLEMENTATION

  @Override
  public DestinationRead createDestination(@Valid DestinationCreate destinationCreate) {
    return execute(() -> destinationHandler.createDestination(destinationCreate));
  }

  @Override
  public void deleteDestination(@Valid DestinationIdRequestBody destinationIdRequestBody) {
    execute(() -> {
      destinationHandler.deleteDestination(destinationIdRequestBody);
      return null;
    });
  }

  @Override
  public DestinationRead updateDestination(@Valid DestinationUpdate destinationUpdate) {
    return execute(() -> destinationHandler.updateDestination(destinationUpdate));
  }

  @Override
  public DestinationReadList listDestinationsForWorkspace(@Valid WorkspaceIdRequestBody workspaceIdRequestBody) {
    return execute(() -> destinationHandler.listDestinationsForWorkspace(workspaceIdRequestBody));
  }

  @Override
  public DestinationRead getDestination(@Valid DestinationIdRequestBody destinationIdRequestBody) {
    return execute(() -> destinationHandler.getDestination(destinationIdRequestBody));
  }

  @Override
  public CheckConnectionRead checkConnectionToDestination(@Valid DestinationIdRequestBody destinationIdRequestBody) {
    return execute(() -> schedulerHandler.checkDestinationConnectionFromDestinationId(destinationIdRequestBody));
  }

  @Override
  public CheckConnectionRead checkConnectionToDestinationForUpdate(@Valid DestinationUpdate destinationUpdate) {
    return execute(() -> schedulerHandler.checkDestinationConnectionFromDestinationIdForUpdate(destinationUpdate));
  }

  // CONNECTION

  @Override
  public ConnectionRead createConnection(@Valid ConnectionCreate connectionCreate) {
    return execute(() -> connectionsHandler.createConnection(connectionCreate));
  }

  @Override
  public ConnectionRead updateConnection(@Valid ConnectionUpdate connectionUpdate) {
    return execute(() -> connectionsHandler.updateConnection(connectionUpdate));
  }

  @Override
  public ConnectionReadList listConnectionsForWorkspace(@Valid WorkspaceIdRequestBody workspaceIdRequestBody) {
    return execute(() -> connectionsHandler.listConnectionsForWorkspace(workspaceIdRequestBody));
  }

  @Override
  public ConnectionRead getConnection(@Valid ConnectionIdRequestBody connectionIdRequestBody) {
    return execute(() -> connectionsHandler.getConnection(connectionIdRequestBody));
  }

  @Override
  public void deleteConnection(@Valid ConnectionIdRequestBody connectionIdRequestBody) {
    execute(() -> {
      connectionsHandler.deleteConnection(connectionIdRequestBody);
      return null;
    });

  }

  @Override
  public JobInfoRead syncConnection(@Valid ConnectionIdRequestBody connectionIdRequestBody) {
    return execute(() -> schedulerHandler.syncConnection(connectionIdRequestBody));
  }

  @Override
  public JobInfoRead resetConnection(@Valid ConnectionIdRequestBody connectionIdRequestBody) {
    return execute(() -> schedulerHandler.resetConnection(connectionIdRequestBody));
  }

  // SCHEDULER
  @Override
  public CheckConnectionRead executeSourceCheckConnection(@Valid SourceCoreConfig sourceConfig) {
    return execute(() -> schedulerHandler.checkSourceConnectionFromSourceCreate(sourceConfig));
  }

  @Override
  public CheckConnectionRead executeDestinationCheckConnection(@Valid DestinationCoreConfig destinationConfig) {
    return execute(() -> schedulerHandler.checkDestinationConnectionFromDestinationCreate(destinationConfig));
  }

  @Override
  public SourceDiscoverSchemaRead executeSourceDiscoverSchema(@Valid SourceCoreConfig sourceCreate) {
    return execute(() -> schedulerHandler.discoverSchemaForSourceFromSourceCreate(sourceCreate));
  }

  // JOB HISTORY

  @Override
  public JobReadList listJobsFor(@Valid JobListRequestBody jobListRequestBody) {
    return execute(() -> jobHistoryHandler.listJobsFor(jobListRequestBody));
  }

  @Override
  public JobInfoRead getJobInfo(@Valid JobIdRequestBody jobIdRequestBody) {
    return execute(() -> jobHistoryHandler.getJobInfo(jobIdRequestBody));
  }

  @Override
  public File getLogs(@Valid LogsRequestBody logsRequestBody) {
    return execute(() -> logsHandler.getLogs(configs, logsRequestBody));
  }

  // HEALTH
  @Override
  public HealthCheckRead getHealthCheck() {
    return healthCheckHandler.health();
  }

  // WEB BACKEND

  @Override
  public WbConnectionReadList webBackendListConnectionsForWorkspace(@Valid WorkspaceIdRequestBody workspaceIdRequestBody) {
    return execute(() -> webBackendConnectionsHandler.webBackendListConnectionsForWorkspace(workspaceIdRequestBody));
  }

  @Override
  public DestinationRead webBackendRecreateDestination(@Valid DestinationRecreate destinationRecreate) {
    return execute(
        () -> webBackendDestinationHandler.webBackendRecreateDestinationAndCheck(destinationRecreate));
  }

  @Override
  public SourceRead webBackendRecreateSource(@Valid SourceRecreate sourceRecreate) {
    return execute(() -> webBackendSourceHandler.webBackendRecreateSourceAndCheck(sourceRecreate));
  }

  @Override
  public WbConnectionRead webBackendGetConnection(@Valid WebBackendConnectionRequestBody webBackendConnectionRequestBody) {
    return execute(() -> webBackendConnectionsHandler.webBackendGetConnection(webBackendConnectionRequestBody));
  }

  @Override
  public ConnectionRead webBackendUpdateConnection(@Valid WebBackendConnectionUpdate webBackendConnectionUpdate) {
    return execute(() -> webBackendConnectionsHandler.webBackendUpdateConnection(webBackendConnectionUpdate));
  }

  // ARCHIVES

  @Override
  public File exportArchive() {
    return execute(archiveHandler::exportData);
  }

  @Override
  public ImportRead importArchive(@Valid File archiveFile) {
    return execute(() -> archiveHandler.importData(archiveFile));
  }

  private <T> T execute(HandlerCall<T> call) {
    try {
      return call.call();
    } catch (ConfigNotFoundException e) {
      throw new KnownException(
          HttpStatus.UNPROCESSABLE_ENTITY_422,
          String.format("Could not find configuration for %s: %s.", e.getType().toString(), e.getConfigId()), e);
    } catch (JsonValidationException e) {
      throw new KnownException(
          HttpStatus.UNPROCESSABLE_ENTITY_422,
          String.format("The provided configuration does not fulfill the specification. Errors: %s", e.getMessage()), e);
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  private interface HandlerCall<T> {

    T call() throws ConfigNotFoundException, IOException, JsonValidationException;

  }

}
