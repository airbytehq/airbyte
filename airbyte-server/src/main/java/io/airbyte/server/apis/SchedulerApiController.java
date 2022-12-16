/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis;

import io.airbyte.api.generated.SchedulerApi;
import io.airbyte.api.model.generated.CheckConnectionRead;
import io.airbyte.api.model.generated.DestinationCoreConfig;
import io.airbyte.api.model.generated.SourceCoreConfig;
import io.airbyte.api.model.generated.SourceDiscoverSchemaRead;
import io.airbyte.server.handlers.SchedulerHandler;
import io.micronaut.http.annotation.Controller;
import io.micronaut.http.annotation.Post;

@Controller("/api/v1/scheduler")
public class SchedulerApiController implements SchedulerApi {

  private final SchedulerHandler schedulerHandler;

  public SchedulerApiController(final SchedulerHandler schedulerHandler) {
    this.schedulerHandler = schedulerHandler;
  }

  @Post("/destinations/check_connection")
  @Override
  public CheckConnectionRead executeDestinationCheckConnection(final DestinationCoreConfig destinationCoreConfig) {
    return ApiHelper.execute(() -> schedulerHandler.checkDestinationConnectionFromDestinationCreate(destinationCoreConfig));
  }

  @Post("/sources/check_connection")
  @Override
  public CheckConnectionRead executeSourceCheckConnection(final SourceCoreConfig sourceCoreConfig) {
    return ApiHelper.execute(() -> schedulerHandler.checkSourceConnectionFromSourceCreate(sourceCoreConfig));
  }

  @Post("/sources/discover_schema")
  @Override
  public SourceDiscoverSchemaRead executeSourceDiscoverSchema(final SourceCoreConfig sourceCoreConfig) {
    return ApiHelper.execute(() -> schedulerHandler.discoverSchemaForSourceFromSourceCreate(sourceCoreConfig));
  }

}
