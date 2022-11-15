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
import lombok.AllArgsConstructor;

@AllArgsConstructor
public class SchedulerApiController implements SchedulerApi {

  private final SchedulerHandler schedulerHandler;

  @Override
  public CheckConnectionRead executeDestinationCheckConnection(final DestinationCoreConfig destinationCoreConfig) {
    return ApiHelper.execute(() -> schedulerHandler.checkDestinationConnectionFromDestinationCreate(destinationCoreConfig));
  }

  @Override
  public CheckConnectionRead executeSourceCheckConnection(final SourceCoreConfig sourceCoreConfig) {
    return ApiHelper.execute(() -> schedulerHandler.checkSourceConnectionFromSourceCreate(sourceCoreConfig));
  }

  @Override
  public SourceDiscoverSchemaRead executeSourceDiscoverSchema(final SourceCoreConfig sourceCoreConfig) {
    return ApiHelper.execute(() -> schedulerHandler.discoverSchemaForSourceFromSourceCreate(sourceCoreConfig));
  }

}
