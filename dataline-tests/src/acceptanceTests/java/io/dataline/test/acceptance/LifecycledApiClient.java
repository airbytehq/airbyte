package io.dataline.test.acceptance;

import io.dataline.api.client.DatalineApiClient;
import io.dataline.api.client.invoker.ApiClient;
import io.dataline.api.client.invoker.ApiException;
import io.dataline.api.client.model.ConnectionCreate;
import io.dataline.api.client.model.ConnectionRead;
import io.dataline.api.client.model.ConnectionStatus;
import io.dataline.api.client.model.ConnectionUpdate;
import io.dataline.api.client.model.SourceImplementationCreate;
import io.dataline.api.client.model.SourceImplementationIdRequestBody;
import io.dataline.api.client.model.SourceImplementationRead;
import org.apache.commons.compress.utils.Lists;
import java.util.List;
import java.util.UUID;

/**
 * An API Client wrapper which makes it convenient to create and destroy API resources.
 */
class LifecycledApiClient extends DatalineApiClient {

  private DatalineApiClient apiClient;

  List<UUID> sourceImplIds = Lists.newArrayList();
  List<UUID> connectionIds = Lists.newArrayList();

  public LifecycledApiClient(ApiClient apiClient) {
    super(apiClient);
  }

  public SourceImplementationRead managedCreateSourceImplementation(SourceImplementationCreate params) throws ApiException {
    SourceImplementationRead sourceImplementation = getSourceImplementationApi().createSourceImplementation(params);
    sourceImplIds.add(sourceImplementation.getSourceImplementationId());
    return sourceImplementation;
  }

  public ConnectionRead managedCreateConnection(ConnectionCreate params) throws ApiException {
    ConnectionRead connection = getConnectionApi().createConnection(params);
    connectionIds.add(connection.getConnectionId());
    return connection;
  }

  public void tearDown() throws ApiException {
    for (UUID sourceImplId : sourceImplIds) {
      deleteSourceImpl(sourceImplId);
    }

    for (UUID connectionId : connectionIds) {
      disableConnection(connectionId);
    }

  }
}
