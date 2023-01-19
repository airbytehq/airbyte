/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.sync;

import static io.airbyte.metrics.lib.ApmTraceConstants.ACTIVITY_TRACE_OPERATION_NAME;

import datadog.trace.api.Trace;
import io.airbyte.api.client.generated.SourceApi;
import io.airbyte.api.client.invoker.generated.ApiException;
import io.airbyte.api.client.model.generated.ActorCatalogWithUpdatedAt;
import io.airbyte.api.client.model.generated.SourceDiscoverSchemaRequestBody;
import io.airbyte.api.client.model.generated.SourceIdRequestBody;
import io.airbyte.commons.features.EnvVariableFeatureFlags;
import jakarta.inject.Singleton;
import java.time.OffsetDateTime;
import java.util.UUID;
import lombok.extern.slf4j.Slf4j;

@Slf4j
@Singleton
public class RefreshSchemaActivityImpl implements RefreshSchemaActivity {

  private final SourceApi sourceApi;
  private final EnvVariableFeatureFlags envVariableFeatureFlags;

  public RefreshSchemaActivityImpl(SourceApi sourceApi,
                                   EnvVariableFeatureFlags envVariableFeatureFlags) {
    this.sourceApi = sourceApi;
    this.envVariableFeatureFlags = envVariableFeatureFlags;
  }

  @Override
  @Trace(operationName = ACTIVITY_TRACE_OPERATION_NAME)
  public boolean shouldRefreshSchema(UUID sourceCatalogId) {
    if (!envVariableFeatureFlags.autoDetectSchema()) {
      return false;
    }

    return !schemaRefreshRanRecently(sourceCatalogId);
  }

  @Override
  public void refreshSchema(UUID sourceCatalogId, UUID connectionId) {
    if (!envVariableFeatureFlags.autoDetectSchema()) {
      return;
    }

    SourceDiscoverSchemaRequestBody requestBody =
        new SourceDiscoverSchemaRequestBody().sourceId(sourceCatalogId).disableCache(true).connectionId(connectionId);

    try {
      sourceApi.discoverSchemaForSource(requestBody);
    } catch (final Exception e) {
      // catching this exception because we don't want to block replication due to a failed schema refresh
      log.error("Attempted schema refresh, but failed with error: ", e);
    }
  }

  private boolean schemaRefreshRanRecently(UUID sourceCatalogId) {
    try {
      SourceIdRequestBody sourceIdRequestBody = new SourceIdRequestBody().sourceId(sourceCatalogId);
      ActorCatalogWithUpdatedAt mostRecentFetchEvent = sourceApi.getMostRecentSourceActorCatalog(sourceIdRequestBody);
      if (mostRecentFetchEvent.getUpdatedAt() == null) {
        return false;
      }
      return mostRecentFetchEvent.getUpdatedAt() > OffsetDateTime.now().minusHours(24l).toEpochSecond();
    } catch (ApiException e) {
      // catching this exception because we don't want to block replication due to a failed schema refresh
      log.info("Encountered an error fetching most recent actor catalog fetch event: ", e);
      return true;
    }
  }

}
