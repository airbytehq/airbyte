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
import io.micronaut.http.annotation.Controller;
import io.micronaut.http.annotation.Post;
import javax.transaction.Transactional;

@Controller("/api/v1/sources")
@Transactional
public class SourceApiController implements SourceApi {

  private final SchedulerHandler schedulerHandler;
  private final SourceHandler sourceHandler;

  public SourceApiController(final SchedulerHandler schedulerHandler, final SourceHandler sourceHandler) {
    this.schedulerHandler = schedulerHandler;
    this.sourceHandler = sourceHandler;
  }

  @Post("/check_connection")
  @Override
  @Transactional
  public CheckConnectionRead checkConnectionToSource(final SourceIdRequestBody sourceIdRequestBody) {
    return ApiHelper.execute(() -> schedulerHandler.checkSourceConnectionFromSourceId(sourceIdRequestBody));
  }

  @Post("/check_connection_for_update")
  @Override
  @Transactional
  public CheckConnectionRead checkConnectionToSourceForUpdate(final SourceUpdate sourceUpdate) {
    return ApiHelper.execute(() -> schedulerHandler.checkSourceConnectionFromSourceIdForUpdate(sourceUpdate));
  }

  @Post("/clone")
  @Override
  @Transactional
  public SourceRead cloneSource(final SourceCloneRequestBody sourceCloneRequestBody) {
    return ApiHelper.execute(() -> sourceHandler.cloneSource(sourceCloneRequestBody));
  }

  @Post("/create")
  @Override
  @Transactional
  public SourceRead createSource(final SourceCreate sourceCreate) {
    return ApiHelper.execute(() -> sourceHandler.createSource(sourceCreate));
  }

  @Post("/delete")
  @Override
  @Transactional
  public void deleteSource(final SourceIdRequestBody sourceIdRequestBody) {
    ApiHelper.execute(() -> {
      sourceHandler.deleteSource(sourceIdRequestBody);
      return null;
    });
  }

  @Post("/discover_schema")
  @Override
  @Transactional
  public SourceDiscoverSchemaRead discoverSchemaForSource(final SourceDiscoverSchemaRequestBody sourceDiscoverSchemaRequestBody) {
    return ApiHelper.execute(() -> schedulerHandler.discoverSchemaForSourceFromSourceId(sourceDiscoverSchemaRequestBody));
  }

  @Post("/get")
  @Override
  @Transactional
  public SourceRead getSource(final SourceIdRequestBody sourceIdRequestBody) {
    return ApiHelper.execute(() -> sourceHandler.getSource(sourceIdRequestBody));
  }

  @Post("/list")
  @Override
  @Transactional
  public SourceReadList listSourcesForWorkspace(final WorkspaceIdRequestBody workspaceIdRequestBody) {
    return ApiHelper.execute(() -> sourceHandler.listSourcesForWorkspace(workspaceIdRequestBody));
  }

  @Post("/search")
  @Override
  @Transactional
  public SourceReadList searchSources(final SourceSearch sourceSearch) {
    return ApiHelper.execute(() -> sourceHandler.searchSources(sourceSearch));
  }

  @Post("/update")
  @Override
  @Transactional
  public SourceRead updateSource(final SourceUpdate sourceUpdate) {
    return ApiHelper.execute(() -> sourceHandler.updateSource(sourceUpdate));
  }

}
