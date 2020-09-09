/*
 * MIT License
 *
 * Copyright (c) 2020 Dataline
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

package io.dataline.server.apis;

import io.dataline.api.model.CheckConnectionRead;
import io.dataline.api.model.ConnectionCreate;
import io.dataline.api.model.ConnectionIdRequestBody;
import io.dataline.api.model.ConnectionRead;
import io.dataline.api.model.ConnectionReadList;
import io.dataline.api.model.ConnectionSyncRead;
import io.dataline.api.model.ConnectionUpdate;
import io.dataline.api.model.DestinationIdRequestBody;
import io.dataline.api.model.DestinationImplementationCreate;
import io.dataline.api.model.DestinationImplementationIdRequestBody;
import io.dataline.api.model.DestinationImplementationRead;
import io.dataline.api.model.DestinationImplementationReadList;
import io.dataline.api.model.DestinationImplementationUpdate;
import io.dataline.api.model.DestinationRead;
import io.dataline.api.model.DestinationReadList;
import io.dataline.api.model.DestinationSpecificationRead;
import io.dataline.api.model.JobIdRequestBody;
import io.dataline.api.model.JobInfoRead;
import io.dataline.api.model.JobListRequestBody;
import io.dataline.api.model.JobReadList;
import io.dataline.api.model.SlugRequestBody;
import io.dataline.api.model.SourceIdRequestBody;
import io.dataline.api.model.SourceImplementationCreate;
import io.dataline.api.model.SourceImplementationDiscoverSchemaRead;
import io.dataline.api.model.SourceImplementationIdRequestBody;
import io.dataline.api.model.SourceImplementationRead;
import io.dataline.api.model.SourceImplementationReadList;
import io.dataline.api.model.SourceImplementationUpdate;
import io.dataline.api.model.SourceRead;
import io.dataline.api.model.SourceReadList;
import io.dataline.api.model.SourceSpecificationRead;
import io.dataline.api.model.WbConnectionRead;
import io.dataline.api.model.WbConnectionReadList;
import io.dataline.api.model.WorkspaceIdRequestBody;
import io.dataline.api.model.WorkspaceRead;
import io.dataline.api.model.WorkspaceUpdate;
import io.dataline.config.persistence.ConfigNotFoundException;
import io.dataline.config.persistence.ConfigRepository;
import io.dataline.config.persistence.JsonValidationException;
import io.dataline.scheduler.persistence.DefaultSchedulerPersistence;
import io.dataline.scheduler.persistence.SchedulerPersistence;
import io.dataline.server.errors.KnownException;
import io.dataline.server.handlers.ConnectionsHandler;
import io.dataline.server.handlers.DestinationImplementationsHandler;
import io.dataline.server.handlers.DestinationSpecificationsHandler;
import io.dataline.server.handlers.DestinationsHandler;
import io.dataline.server.handlers.JobHistoryHandler;
import io.dataline.server.handlers.SchedulerHandler;
import io.dataline.server.handlers.SourceImplementationsHandler;
import io.dataline.server.handlers.SourceSpecificationsHandler;
import io.dataline.server.handlers.SourcesHandler;
import io.dataline.server.handlers.WebBackendConnectionsHandler;
import io.dataline.server.handlers.WorkspacesHandler;
import io.dataline.server.validation.IntegrationSchemaValidation;
import java.io.IOException;
import javax.validation.Valid;
import org.apache.commons.dbcp2.BasicDataSource;
import org.eclipse.jetty.http.HttpStatus;

@javax.ws.rs.Path("/v1")
public class ConfigurationApi implements io.dataline.api.V1Api {

  private final WorkspacesHandler workspacesHandler;
  private final SourcesHandler sourcesHandler;
  private final SourceSpecificationsHandler sourceSpecificationsHandler;
  private final SourceImplementationsHandler sourceImplementationsHandler;
  private final DestinationsHandler destinationsHandler;
  private final DestinationSpecificationsHandler destinationSpecificationsHandler;
  private final DestinationImplementationsHandler destinationImplementationsHandler;
  private final ConnectionsHandler connectionsHandler;
  private final SchedulerHandler schedulerHandler;
  private final JobHistoryHandler jobHistoryHandler;
  private final WebBackendConnectionsHandler webBackendConnectionsHandler;

  public ConfigurationApi(final ConfigRepository configRepository, BasicDataSource connectionPool) {
    final IntegrationSchemaValidation integrationSchemaValidation = new IntegrationSchemaValidation();
    workspacesHandler = new WorkspacesHandler(configRepository);
    sourcesHandler = new SourcesHandler(configRepository);
    sourceSpecificationsHandler = new SourceSpecificationsHandler(configRepository);
    connectionsHandler = new ConnectionsHandler(configRepository);
    sourceImplementationsHandler = new SourceImplementationsHandler(configRepository, integrationSchemaValidation, connectionsHandler);
    destinationsHandler = new DestinationsHandler(configRepository);
    destinationSpecificationsHandler = new DestinationSpecificationsHandler(configRepository);
    destinationImplementationsHandler = new DestinationImplementationsHandler(configRepository, integrationSchemaValidation);
    final SchedulerPersistence schedulerPersistence = new DefaultSchedulerPersistence(connectionPool);
    schedulerHandler = new SchedulerHandler(configRepository, schedulerPersistence);
    jobHistoryHandler = new JobHistoryHandler(schedulerPersistence);
    webBackendConnectionsHandler = new WebBackendConnectionsHandler(connectionsHandler, sourceImplementationsHandler, jobHistoryHandler);
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
  public SourceReadList listSources() {
    return execute(sourcesHandler::listSources);
  }

  @Override
  public SourceRead getSource(@Valid SourceIdRequestBody sourceIdRequestBody) {
    return execute(() -> sourcesHandler.getSource(sourceIdRequestBody));
  }

  // SOURCE SPECIFICATION

  @Override
  public SourceSpecificationRead getSourceSpecification(@Valid SourceIdRequestBody sourceIdRequestBody) {
    return execute(() -> sourceSpecificationsHandler.getSourceSpecification(sourceIdRequestBody));
  }

  // SOURCE IMPLEMENTATION

  @Override
  public SourceImplementationRead createSourceImplementation(@Valid SourceImplementationCreate sourceImplementationCreate) {
    return execute(() -> sourceImplementationsHandler.createSourceImplementation(sourceImplementationCreate));
  }

  @Override
  public SourceImplementationRead updateSourceImplementation(@Valid SourceImplementationUpdate sourceImplementationUpdate) {
    return execute(() -> sourceImplementationsHandler.updateSourceImplementation(sourceImplementationUpdate));
  }

  @Override
  public SourceImplementationReadList listSourceImplementationsForWorkspace(@Valid WorkspaceIdRequestBody workspaceIdRequestBody) {
    return execute(() -> sourceImplementationsHandler.listSourceImplementationsForWorkspace(workspaceIdRequestBody));
  }

  @Override
  public SourceImplementationRead getSourceImplementation(@Valid SourceImplementationIdRequestBody sourceImplementationIdRequestBody) {
    return execute(() -> sourceImplementationsHandler.getSourceImplementation(sourceImplementationIdRequestBody));
  }

  @Override
  public void deleteSourceImplementation(@Valid SourceImplementationIdRequestBody sourceImplementationIdRequestBody) {
    execute(() -> {
      sourceImplementationsHandler.deleteSourceImplementation(sourceImplementationIdRequestBody);
      return null;
    });
  }

  @Override
  public CheckConnectionRead checkConnectionToSourceImplementation(@Valid SourceImplementationIdRequestBody sourceImplementationIdRequestBody) {
    return execute(() -> schedulerHandler.checkSourceImplementationConnection(sourceImplementationIdRequestBody));
  }

  @Override
  public SourceImplementationDiscoverSchemaRead discoverSchemaForSourceImplementation(@Valid SourceImplementationIdRequestBody sourceImplementationIdRequestBody) {
    return execute(() -> schedulerHandler.discoverSchemaForSourceImplementation(sourceImplementationIdRequestBody));
  }

  // DESTINATION

  @Override
  public DestinationReadList listDestinations() {
    return execute(destinationsHandler::listDestinations);
  }

  @Override
  public DestinationRead getDestination(@Valid DestinationIdRequestBody destinationIdRequestBody) {
    return execute(() -> destinationsHandler.getDestination(destinationIdRequestBody));
  }

  // DESTINATION SPECIFICATION

  @Override
  public DestinationSpecificationRead getDestinationSpecification(@Valid DestinationIdRequestBody destinationIdRequestBody) {
    return execute(() -> destinationSpecificationsHandler.getDestinationSpecification(destinationIdRequestBody));
  }

  // DESTINATION IMPLEMENTATION
  @Override
  public DestinationImplementationRead createDestinationImplementation(@Valid DestinationImplementationCreate destinationImplementationCreate) {
    return execute(() -> destinationImplementationsHandler.createDestinationImplementation(destinationImplementationCreate));
  }

  @Override
  public DestinationImplementationRead updateDestinationImplementation(@Valid DestinationImplementationUpdate destinationImplementationUpdate) {
    return execute(() -> destinationImplementationsHandler.updateDestinationImplementation(destinationImplementationUpdate));
  }

  @Override
  public DestinationImplementationReadList listDestinationImplementationsForWorkspace(@Valid WorkspaceIdRequestBody workspaceIdRequestBody) {
    return execute(() -> destinationImplementationsHandler.listDestinationImplementationsForWorkspace(workspaceIdRequestBody));
  }

  @Override
  public DestinationImplementationRead getDestinationImplementation(@Valid DestinationImplementationIdRequestBody destinationImplementationIdRequestBody) {
    return execute(() -> destinationImplementationsHandler.getDestinationImplementation(destinationImplementationIdRequestBody));
  }

  @Override
  public CheckConnectionRead checkConnectionToDestinationImplementation(@Valid DestinationImplementationIdRequestBody destinationImplementationIdRequestBody) {
    return execute(() -> schedulerHandler.checkDestinationImplementationConnection(destinationImplementationIdRequestBody));
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
  public ConnectionSyncRead syncConnection(@Valid ConnectionIdRequestBody connectionIdRequestBody) {
    return execute(() -> schedulerHandler.syncConnection(connectionIdRequestBody));
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

  // WEB BACKEND

  @Override
  public WbConnectionReadList webBackendListConnectionsForWorkspace(@Valid WorkspaceIdRequestBody workspaceIdRequestBody) {
    return execute(() -> webBackendConnectionsHandler.webBackendListConnectionsForWorkspace(workspaceIdRequestBody));
  }

  @Override
  public WbConnectionRead webBackendGetConnection(@Valid ConnectionIdRequestBody connectionIdRequestBody) {
    return execute(() -> webBackendConnectionsHandler.webBackendGetConnection(connectionIdRequestBody));
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
