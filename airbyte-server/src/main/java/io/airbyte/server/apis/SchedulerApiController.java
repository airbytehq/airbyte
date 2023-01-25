/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis;

import static io.airbyte.commons.auth.AuthRoleConstants.AUTHENTICATED_USER;
import static io.airbyte.commons.auth.AuthRoleConstants.EDITOR;

import io.airbyte.api.generated.SchedulerApi;
import io.airbyte.api.model.generated.CheckConnectionRead;
import io.airbyte.api.model.generated.DestinationCoreConfig;
import io.airbyte.api.model.generated.SourceCoreConfig;
import io.airbyte.api.model.generated.SourceDiscoverSchemaRead;
import io.airbyte.commons.server.handlers.SchedulerHandler;
import io.micronaut.context.annotation.Requires;
import io.micronaut.http.annotation.Controller;
import io.micronaut.http.annotation.Post;
import io.micronaut.security.annotation.Secured;
import io.micronaut.security.rules.SecurityRule;

@Controller("/api/v1/scheduler")
@Requires(property = "airbyte.deployment-mode",
          value = "OSS")
@Secured(SecurityRule.IS_AUTHENTICATED)
public class SchedulerApiController implements SchedulerApi {

  private final SchedulerHandler schedulerHandler;

  public SchedulerApiController(final SchedulerHandler schedulerHandler) {
    this.schedulerHandler = schedulerHandler;
  }

  @Post("/destinations/check_connection")
  @Secured({AUTHENTICATED_USER})
  @Override
  public CheckConnectionRead executeDestinationCheckConnection(final DestinationCoreConfig destinationCoreConfig) {
    return ApiHelper.execute(() -> schedulerHandler.checkDestinationConnectionFromDestinationCreate(destinationCoreConfig));
  }

  @Post("/sources/check_connection")
  @Secured({AUTHENTICATED_USER})
  @Override
  public CheckConnectionRead executeSourceCheckConnection(final SourceCoreConfig sourceCoreConfig) {
    return ApiHelper.execute(() -> schedulerHandler.checkSourceConnectionFromSourceCreate(sourceCoreConfig));
  }

  @Post("/sources/discover_schema")
  @Secured({EDITOR})
  @Override
  public SourceDiscoverSchemaRead executeSourceDiscoverSchema(final SourceCoreConfig sourceCoreConfig) {
    return ApiHelper.execute(() -> schedulerHandler.discoverSchemaForSourceFromSourceCreate(sourceCoreConfig));
  }

}
