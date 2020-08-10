package io.dataline.conduit.server.apis;

import javax.validation.Valid;
import javax.ws.rs.Path;

import io.dataline.conduit.api.model.*;

@Path("/v1")
public class ConduitConfigurationApi implements io.dataline.conduit.api.V1Api {

    @Override
    public ConnectionRead createConnection(@Valid ConnectionCreate connectionCreate) {
        return null;
    }

    @Override
    public DestinationImplementationRead createDestinationImplementation(@Valid DestinationImplementationCreate destinationImplementationCreate) {
        return null;
    }

    @Override
    public SourceImplementationRead createSourceImplementation(@Valid SourceImplementationCreate sourceImplementationCreate) {
        return null;
    }

    @Override
    public SourceImplementationDiscoverSchemaRead discoverSchemaForSourceImplementation(@Valid SourceImplementationIdRequestBody sourceImplementationIdRequestBody) {
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
    public DestinationImplementationRead getDestinationImplementation(@Valid DestinationImplementationIdRequestBody destinationImplementationIdRequestBody) {
        return null;
    }

    @Override
    public DestinationSpecificationRead getDestinationSpecification(@Valid DestinationIdRequestBody destinationIdRequestBody) {
        return null;
    }

    @Override
    public SourceRead getSource(@Valid SourceIdRequestBody sourceIdRequestBody) {
        return null;
    }

    @Override
    public SourceImplementationRead getSourceImplementation(@Valid SourceImplementationIdRequestBody sourceImplementationIdRequestBody) {
        return null;
    }

    @Override
    public SourceImplementationReadList getSourceImplementationsForWorkspace(@Valid WorkspaceIdRequestBody workspaceIdRequestBody) {
        return null;
    }

    @Override
    public SourceSpecificationRead getSourceSpecification(@Valid SourceIdRequestBody sourceIdRequestBody) {
        return null;
    }

    @Override
    public WorkspaceRead getWorkspace(@Valid WorkspaceIdRequestBody workspaceIdRequestBody) {
        return null;
    }

    @Override
    public WorkspaceRead getWorkspaceBySlug(@Valid SlugRequestBody slugRequestBody) {
        return null;
    }

    @Override
    public ConnectionReadList listConnectionsForWorkspace(@Valid WorkspaceIdRequestBody workspaceIdRequestBody) {
        return null;
    }

    @Override
    public DestinationImplementationReadList listDestinationImplementationsForWorkspace(@Valid WorkspaceIdRequestBody workspaceIdRequestBody) {
        return null;
    }

    @Override
    public DestinationReadList listDestinations() {
        return null;
    }

    @Override
    public SourceReadList listSources() {
        return null;
    }

    @Override
    public ConnectionSyncRead syncConnection(@Valid ConnectionIdRequestBody connectionIdRequestBody) {
        return null;
    }

    @Override
    public SourceImplementationTestConnectionRead testConnectiontoSourceImplementation(@Valid SourceImplementationIdRequestBody sourceImplementationIdRequestBody) {
        return null;
    }

    @Override
    public ConnectionRead updateConnection(@Valid ConnectionUpdate connectionUpdate) {
        return null;
    }

    @Override
    public DestinationImplementationRead updateDestinationImplementation(@Valid DestinationImplementationUpdate destinationImplementationUpdate) {
        return null;
    }

    @Override
    public SourceImplementationRead updateSourceImplementation(@Valid SourceImplementationUpdate sourceImplementationUpdate) {
        return null;
    }
}
