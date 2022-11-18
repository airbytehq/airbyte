/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis;

import io.airbyte.api.generated.SourceApi;
import io.airbyte.api.model.generated.CheckConnectionRead;
import io.airbyte.api.model.generated.SourceCloneRequestBody;
import io.airbyte.api.model.generated.SourceCreate;
import io.airbyte.api.model.generated.SourceDiscoverSchemaRead;
import io.airbyte.api.model.generated.SourceDiscoverSchemaRequestBody;
import io.airbyte.api.model.generated.SourceIdRequestBody;
import io.airbyte.api.model.generated.SourceRead;
import io.airbyte.api.model.generated.SourceReadList;
import io.airbyte.api.model.generated.SourceSearch;
import io.airbyte.api.model.generated.SourceUpdate;
import io.airbyte.api.model.generated.WorkspaceIdRequestBody;
import io.airbyte.server.handlers.SchedulerHandler;
import io.airbyte.server.handlers.SourceHandler;
import javax.ws.rs.Path;
import lombok.AllArgsConstructor;

@Path("/v1/sources")
@AllArgsConstructor
public class SourceApiController implements SourceApi {

  private final SchedulerHandler schedulerHandler;
  private final SourceHandler sourceHandler;

  @Override
  public CheckConnectionRead checkConnectionToSource(final SourceIdRequestBody sourceIdRequestBody) {
    return ConfigurationApi.execute(() -> schedulerHandler.checkSourceConnectionFromSourceId(sourceIdRequestBody));
  }

  @Override
  public CheckConnectionRead checkConnectionToSourceForUpdate(final SourceUpdate sourceUpdate) {
    return ConfigurationApi.execute(() -> schedulerHandler.checkSourceConnectionFromSourceIdForUpdate(sourceUpdate));
  }

  @Override
  public SourceRead cloneSource(final SourceCloneRequestBody sourceCloneRequestBody) {
    return ConfigurationApi.execute(() -> sourceHandler.cloneSource(sourceCloneRequestBody));
  }

  @Override
  public SourceRead createSource(final SourceCreate sourceCreate) {
    return ConfigurationApi.execute(() -> sourceHandler.createSource(sourceCreate));
  }

  @Override
  public void deleteSource(final SourceIdRequestBody sourceIdRequestBody) {
    ConfigurationApi.execute(() -> {
      sourceHandler.deleteSource(sourceIdRequestBody);
      return null;
    });
  }

  @Override
  public SourceDiscoverSchemaRead discoverSchemaForSource(final SourceDiscoverSchemaRequestBody sourceDiscoverSchemaRequestBody) {
    return ConfigurationApi.execute(() -> schedulerHandler.discoverSchemaForSourceFromSourceId(sourceDiscoverSchemaRequestBody));
  }

  @Override
  public SourceRead getSource(final SourceIdRequestBody sourceIdRequestBody) {
    return ConfigurationApi.execute(() -> sourceHandler.getSource(sourceIdRequestBody));
  }

  @Override
  public SourceReadList listSourcesForWorkspace(final WorkspaceIdRequestBody workspaceIdRequestBody) {
    return ConfigurationApi.execute(() -> sourceHandler.listSourcesForWorkspace(workspaceIdRequestBody));
  }

  @Override
  public SourceReadList searchSources(final SourceSearch sourceSearch) {
    return ConfigurationApi.execute(() -> sourceHandler.searchSources(sourceSearch));
  }

  @Override
  public SourceRead updateSource(final SourceUpdate sourceUpdate) {
    return ConfigurationApi.execute(() -> sourceHandler.updateSource(sourceUpdate));
  }

}
