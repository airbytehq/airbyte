/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis;

import static io.airbyte.commons.auth.AuthRoleConstants.EDITOR;
import static io.airbyte.commons.auth.AuthRoleConstants.READER;

import io.airbyte.api.generated.SourceApi;
import io.airbyte.api.model.generated.ActorCatalogWithUpdatedAt;
import io.airbyte.api.model.generated.CheckConnectionRead;
import io.airbyte.api.model.generated.DiscoverCatalogResult;
import io.airbyte.api.model.generated.SourceCloneRequestBody;
import io.airbyte.api.model.generated.SourceCreate;
import io.airbyte.api.model.generated.SourceDiscoverSchemaRead;
import io.airbyte.api.model.generated.SourceDiscoverSchemaRequestBody;
import io.airbyte.api.model.generated.SourceDiscoverSchemaWriteRequestBody;
import io.airbyte.api.model.generated.SourceIdRequestBody;
import io.airbyte.api.model.generated.SourceRead;
import io.airbyte.api.model.generated.SourceReadList;
import io.airbyte.api.model.generated.SourceSearch;
import io.airbyte.api.model.generated.SourceUpdate;
import io.airbyte.api.model.generated.WorkspaceIdRequestBody;
import io.airbyte.commons.server.handlers.SchedulerHandler;
import io.airbyte.commons.server.handlers.SourceHandler;
import io.micronaut.context.annotation.Requires;
import io.micronaut.http.HttpStatus;
import io.micronaut.http.annotation.Controller;
import io.micronaut.http.annotation.Post;
import io.micronaut.http.annotation.Status;
import io.micronaut.security.annotation.Secured;
import io.micronaut.security.rules.SecurityRule;

@Controller("/api/v1/sources")
@Requires(property = "airbyte.deployment-mode",
          value = "OSS")
@Secured(SecurityRule.IS_AUTHENTICATED)
public class SourceApiController implements SourceApi {

  private final SchedulerHandler schedulerHandler;
  private final SourceHandler sourceHandler;

  public SourceApiController(final SchedulerHandler schedulerHandler, final SourceHandler sourceHandler) {
    this.schedulerHandler = schedulerHandler;
    this.sourceHandler = sourceHandler;
  }

  @Post("/check_connection")
  @Secured({EDITOR})
  @Override
  public CheckConnectionRead checkConnectionToSource(final SourceIdRequestBody sourceIdRequestBody) {
    return ApiHelper.execute(() -> schedulerHandler.checkSourceConnectionFromSourceId(sourceIdRequestBody));
  }

  @Post("/check_connection_for_update")
  @Secured({EDITOR})
  @Override
  public CheckConnectionRead checkConnectionToSourceForUpdate(final SourceUpdate sourceUpdate) {
    return ApiHelper.execute(() -> schedulerHandler.checkSourceConnectionFromSourceIdForUpdate(sourceUpdate));
  }

  @Post("/clone")
  @Override
  public SourceRead cloneSource(final SourceCloneRequestBody sourceCloneRequestBody) {
    return ApiHelper.execute(() -> sourceHandler.cloneSource(sourceCloneRequestBody));
  }

  @Post("/create")
  @Secured({EDITOR})
  @Override
  public SourceRead createSource(final SourceCreate sourceCreate) {
    return ApiHelper.execute(() -> sourceHandler.createSource(sourceCreate));
  }

  @Post("/delete")
  @Secured({EDITOR})
  @Override
  @Status(HttpStatus.NO_CONTENT)
  public void deleteSource(final SourceIdRequestBody sourceIdRequestBody) {
    ApiHelper.execute(() -> {
      sourceHandler.deleteSource(sourceIdRequestBody);
      return null;
    });
  }

  @Post("/discover_schema")
  @Secured({EDITOR})
  @Override
  public SourceDiscoverSchemaRead discoverSchemaForSource(final SourceDiscoverSchemaRequestBody sourceDiscoverSchemaRequestBody) {
    return ApiHelper.execute(() -> schedulerHandler.discoverSchemaForSourceFromSourceId(sourceDiscoverSchemaRequestBody));
  }

  @Post("/get")
  @Secured({READER})
  @Override
  public SourceRead getSource(final SourceIdRequestBody sourceIdRequestBody) {
    return ApiHelper.execute(() -> sourceHandler.getSource(sourceIdRequestBody));
  }

  @Post("/most_recent_source_actor_catalog")
  @Secured({READER})
  @Override
  public ActorCatalogWithUpdatedAt getMostRecentSourceActorCatalog(final SourceIdRequestBody sourceIdRequestBody) {
    return ApiHelper.execute(() -> sourceHandler.getMostRecentSourceActorCatalogWithUpdatedAt(sourceIdRequestBody));
  }

  @Post("/list")
  @Secured({READER})
  @Override
  public SourceReadList listSourcesForWorkspace(final WorkspaceIdRequestBody workspaceIdRequestBody) {
    return ApiHelper.execute(() -> sourceHandler.listSourcesForWorkspace(workspaceIdRequestBody));
  }

  @Post("/search")
  @Override
  public SourceReadList searchSources(final SourceSearch sourceSearch) {
    return ApiHelper.execute(() -> sourceHandler.searchSources(sourceSearch));
  }

  @Post("/update")
  @Secured({EDITOR})
  @Override
  public SourceRead updateSource(final SourceUpdate sourceUpdate) {
    return ApiHelper.execute(() -> sourceHandler.updateSource(sourceUpdate));
  }

  @Post("/write_discover_catalog_result")
  @Override
  public DiscoverCatalogResult writeDiscoverCatalogResult(final SourceDiscoverSchemaWriteRequestBody request) {
    return ApiHelper.execute(() -> sourceHandler.writeDiscoverCatalogResult(request));
  }

}
