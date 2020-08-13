package io.dataline.server.apis;

import io.dataline.api.model.*;
import io.dataline.config.persistence.ConfigPersistence;
import io.dataline.config.persistence.ConfigPersistenceImpl;
import io.dataline.server.handlers.SourceImplementationsHandler;
import io.dataline.server.handlers.SourceSpecificationsHandler;
import io.dataline.server.handlers.SourcesHandler;
import io.dataline.server.handlers.WorkspacesHandler;
import javax.validation.Valid;
import javax.ws.rs.Path;

@Path("/v1")
public class ConfigurationApi implements io.dataline.api.V1Api {
  private final WorkspacesHandler workspacesHandler;
  private final SourcesHandler sourcesHandler;
  private final SourceSpecificationsHandler sourceSpecificationsHandler;
  private final SourceImplementationsHandler sourceImplementationsHandler;

  public ConfigurationApi() {
    ConfigPersistence configPersistence = ConfigPersistenceImpl.get();
    workspacesHandler = new WorkspacesHandler(configPersistence);
    sourcesHandler = new SourcesHandler(configPersistence);
    sourceSpecificationsHandler = new SourceSpecificationsHandler(configPersistence);
    sourceImplementationsHandler = new SourceImplementationsHandler(configPersistence);
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
  public SourceImplementationRead getSourceImplementation(
      @Valid SourceImplementationIdRequestBody sourceImplementationIdRequestBody) {
    return sourceImplementationsHandler.getSourceImplementation(sourceImplementationIdRequestBody);
  }

  @Override
  public SourceImplementationReadList listSourceImplementationsForWorkspace(
      @Valid WorkspaceIdRequestBody workspaceIdRequestBody) {
    return sourceImplementationsHandler.listSourceImplementationsForWorkspace(
        workspaceIdRequestBody);
  }

  @Override
  public SourceImplementationTestConnectionRead testConnectionToSourceImplementation(
      @Valid SourceImplementationIdRequestBody sourceImplementationIdRequestBody) {
    return null;
  }

  @Override
  public SourceImplementationRead updateSourceImplementation(
      @Valid SourceImplementationUpdate sourceImplementationUpdate) {
    return sourceImplementationsHandler.updateSourceImplementation(sourceImplementationUpdate);
  }

  @Override
  public SourceImplementationDiscoverSchemaRead discoverSchemaForSourceImplementation(
      @Valid SourceImplementationIdRequestBody sourceImplementationIdRequestBody) {
    return null;
  }

  @Override
  public ConnectionRead createConnection(@Valid ConnectionCreate connectionCreate) {
    return null;
  }

  @Override
  public DestinationImplementationRead createDestinationImplementation(
      @Valid DestinationImplementationCreate destinationImplementationCreate) {
    return null;
  }

  @Override
  public ConnectionRead getConnection(@Valid ConnectionIdRequestBody connectionIdRequestBody) {
    return null;
  }

  @Override
  public DestinationRead getDestination(@Valid DestinationIdRequestBody destinationIdRequestBody) {
    return null;
  }

  @Override
  public DestinationImplementationRead getDestinationImplementation(
      @Valid DestinationImplementationIdRequestBody destinationImplementationIdRequestBody) {
    return null;
  }

  @Override
  public DestinationSpecificationRead getDestinationSpecification(
      @Valid DestinationIdRequestBody destinationIdRequestBody) {
    return null;
  }

  @Override
  public ConnectionReadList listConnectionsForWorkspace(
      @Valid WorkspaceIdRequestBody workspaceIdRequestBody) {
    return null;
  }

  @Override
  public DestinationImplementationReadList listDestinationImplementationsForWorkspace(
      @Valid WorkspaceIdRequestBody workspaceIdRequestBody) {
    return null;
  }

  @Override
  public DestinationReadList listDestinations() {
    return null;
  }

  @Override
  public ConnectionSyncRead syncConnection(@Valid ConnectionIdRequestBody connectionIdRequestBody) {
    return null;
  }

  @Override
  public ConnectionRead updateConnection(@Valid ConnectionUpdate connectionUpdate) {
    return null;
  }

  @Override
  public DestinationImplementationRead updateDestinationImplementation(
      @Valid DestinationImplementationUpdate destinationImplementationUpdate) {
    return null;
  }
}
