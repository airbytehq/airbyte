package io.dataline.server.apis;

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
import io.dataline.api.model.SlugRequestBody;
import io.dataline.api.model.SourceIdRequestBody;
import io.dataline.api.model.SourceImplementationCreate;
import io.dataline.api.model.SourceImplementationDiscoverSchemaRead;
import io.dataline.api.model.SourceImplementationIdRequestBody;
import io.dataline.api.model.SourceImplementationRead;
import io.dataline.api.model.SourceImplementationReadList;
import io.dataline.api.model.SourceImplementationTestConnectionRead;
import io.dataline.api.model.SourceImplementationUpdate;
import io.dataline.api.model.SourceRead;
import io.dataline.api.model.SourceReadList;
import io.dataline.api.model.SourceSpecificationRead;
import io.dataline.api.model.WorkspaceIdRequestBody;
import io.dataline.api.model.WorkspaceRead;
import io.dataline.api.model.WorkspaceUpdate;
import io.dataline.config.persistence.ConfigPersistence;
import io.dataline.config.persistence.DefaultConfigPersistence;
import io.dataline.server.errors.KnownException;
import io.dataline.server.handlers.ConnectionsHandler;
import io.dataline.server.handlers.DestinationImplementationsHandler;
import io.dataline.server.handlers.DestinationSpecificationsHandler;
import io.dataline.server.handlers.DestinationsHandler;
import io.dataline.server.handlers.SourceImplementationsHandler;
import io.dataline.server.handlers.SourceSpecificationsHandler;
import io.dataline.server.handlers.SourcesHandler;
import io.dataline.server.handlers.WorkspacesHandler;
import io.dataline.server.validation.IntegrationSchemaValidation;
import javax.validation.Valid;
import javax.ws.rs.Path;

@Path("/v1")
public class ConfigurationApi implements io.dataline.api.V1Api {
  private final WorkspacesHandler workspacesHandler;
  private final SourcesHandler sourcesHandler;
  private final SourceSpecificationsHandler sourceSpecificationsHandler;
  private final SourceImplementationsHandler sourceImplementationsHandler;
  private final DestinationsHandler destinationsHandler;
  private final DestinationSpecificationsHandler destinationSpecificationsHandler;
  private final DestinationImplementationsHandler destinationImplementationsHandler;
  private final ConnectionsHandler connectionsHandler;

  public ConfigurationApi() {
    // todo: configure with env variable.
    ConfigPersistence configPersistence = new DefaultConfigPersistence("../data/config/");
    final IntegrationSchemaValidation integrationSchemaValidation =
        new IntegrationSchemaValidation(configPersistence);
    workspacesHandler = new WorkspacesHandler(configPersistence);
    sourcesHandler = new SourcesHandler(configPersistence);
    sourceSpecificationsHandler = new SourceSpecificationsHandler(configPersistence);
    sourceImplementationsHandler =
        new SourceImplementationsHandler(configPersistence, integrationSchemaValidation);
    destinationsHandler = new DestinationsHandler(configPersistence);
    destinationSpecificationsHandler = new DestinationSpecificationsHandler(configPersistence);
    destinationImplementationsHandler =
        new DestinationImplementationsHandler(configPersistence, integrationSchemaValidation);
    connectionsHandler = new ConnectionsHandler(configPersistence);
  }

  // WORKSPACE

  @Override
  public WorkspaceRead getWorkspace(@Valid WorkspaceIdRequestBody workspaceIdRequestBody) {
    return workspacesHandler.getWorkspace(workspaceIdRequestBody);
  }

  @Override
  public WorkspaceRead getWorkspaceBySlug(@Valid SlugRequestBody slugRequestBody) {
    return workspacesHandler.getWorkspaceBySlug(slugRequestBody);
  }

  @Override
  public WorkspaceRead updateWorkspace(@Valid WorkspaceUpdate workspaceUpdate) {
    return workspacesHandler.updateWorkspace(workspaceUpdate);
  }

  // SOURCE

  @Override
  public SourceReadList listSources() {
    return sourcesHandler.listSources();
  }

  @Override
  public SourceRead getSource(@Valid SourceIdRequestBody sourceIdRequestBody) {
    return sourcesHandler.getSource(sourceIdRequestBody);
  }

  // SOURCE SPECIFICATION

  @Override
  public SourceSpecificationRead getSourceSpecification(
      @Valid SourceIdRequestBody sourceIdRequestBody) {
    return sourceSpecificationsHandler.getSourceSpecification(sourceIdRequestBody);
  }

  // SOURCE IMPLEMENTATION

  @Override
  public SourceImplementationRead createSourceImplementation(
      @Valid SourceImplementationCreate sourceImplementationCreate) {
    return sourceImplementationsHandler.createSourceImplementation(sourceImplementationCreate);
  }

  @Override
  public SourceImplementationRead updateSourceImplementation(
      @Valid SourceImplementationUpdate sourceImplementationUpdate) {
    return sourceImplementationsHandler.updateSourceImplementation(sourceImplementationUpdate);
  }

  @Override
  public SourceImplementationReadList listSourceImplementationsForWorkspace(
      @Valid WorkspaceIdRequestBody workspaceIdRequestBody) {
    return sourceImplementationsHandler.listSourceImplementationsForWorkspace(
        workspaceIdRequestBody);
  }

  @Override
  public SourceImplementationRead getSourceImplementation(
      @Valid SourceImplementationIdRequestBody sourceImplementationIdRequestBody) {
    return sourceImplementationsHandler.getSourceImplementation(sourceImplementationIdRequestBody);
  }

  @Override
  public SourceImplementationTestConnectionRead testConnectionToSourceImplementation(
      @Valid SourceImplementationIdRequestBody sourceImplementationIdRequestBody) {
    throw new KnownException(404, "Not implemented");
  }

  @Override
  public SourceImplementationDiscoverSchemaRead discoverSchemaForSourceImplementation(
      @Valid SourceImplementationIdRequestBody sourceImplementationIdRequestBody) {
    throw new KnownException(404, "Not implemented");
  }

  // DESTINATION

  @Override
  public DestinationReadList listDestinations() {
    return destinationsHandler.listDestinations();
  }

  @Override
  public DestinationRead getDestination(@Valid DestinationIdRequestBody destinationIdRequestBody) {
    return destinationsHandler.getDestination(destinationIdRequestBody);
  }

  // DESTINATION SPECIFICATION

  @Override
  public DestinationSpecificationRead getDestinationSpecification(
      @Valid DestinationIdRequestBody destinationIdRequestBody) {
    return destinationSpecificationsHandler.getDestinationSpecification(destinationIdRequestBody);
  }

  // DESTINATION IMPLEMENTATION
  @Override
  public DestinationImplementationRead createDestinationImplementation(
      @Valid DestinationImplementationCreate destinationImplementationCreate) {
    return destinationImplementationsHandler.createDestinationImplementation(
        destinationImplementationCreate);
  }

  @Override
  public DestinationImplementationRead updateDestinationImplementation(
      @Valid DestinationImplementationUpdate destinationImplementationUpdate) {
    return destinationImplementationsHandler.updateDestinationImplementation(
        destinationImplementationUpdate);
  }

  @Override
  public DestinationImplementationReadList listDestinationImplementationsForWorkspace(
      @Valid WorkspaceIdRequestBody workspaceIdRequestBody) {
    return destinationImplementationsHandler.listDestinationImplementationsForWorkspace(
        workspaceIdRequestBody);
  }

  @Override
  public DestinationImplementationRead getDestinationImplementation(
      @Valid DestinationImplementationIdRequestBody destinationImplementationIdRequestBody) {
    return destinationImplementationsHandler.getDestinationImplementation(
        destinationImplementationIdRequestBody);
  }

  // CONNECTION

  @Override
  public ConnectionRead createConnection(@Valid ConnectionCreate connectionCreate) {
    return connectionsHandler.createConnection(connectionCreate);
  }

  @Override
  public ConnectionRead updateConnection(@Valid ConnectionUpdate connectionUpdate) {
    return connectionsHandler.updateConnection(connectionUpdate);
  }

  @Override
  public ConnectionReadList listConnectionsForWorkspace(
      @Valid WorkspaceIdRequestBody workspaceIdRequestBody) {
    return connectionsHandler.listConnectionsForWorkspace(workspaceIdRequestBody);
  }

  @Override
  public ConnectionRead getConnection(@Valid ConnectionIdRequestBody connectionIdRequestBody) {
    return connectionsHandler.getConnection(connectionIdRequestBody);
  }

  @Override
  public ConnectionSyncRead syncConnection(@Valid ConnectionIdRequestBody connectionIdRequestBody) {
    throw new KnownException(404, "Not implemented");
  }
}
