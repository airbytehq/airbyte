/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.sync;

import static io.airbyte.metrics.lib.ApmTraceConstants.ACTIVITY_TRACE_OPERATION_NAME;

import datadog.trace.api.Trace;
import io.airbyte.api.client.generated.SourceApi;
import io.airbyte.api.client.model.generated.SourceDiscoverSchemaRequestBody;
import io.airbyte.commons.features.EnvVariableFeatureFlags;
import io.airbyte.config.ActorCatalogFetchEvent;
import io.airbyte.config.persistence.ConfigRepository;
import jakarta.inject.Singleton;
import java.io.IOException;
import java.time.OffsetDateTime;
import java.util.Optional;
import java.util.UUID;
import lombok.extern.slf4j.Slf4j;

@Slf4j
@Singleton
public class RefreshSchemaActivityImpl implements RefreshSchemaActivity {

  private final Optional<ConfigRepository> configRepository;

  private final SourceApi sourceApi;
  private final EnvVariableFeatureFlags envVariableFeatureFlags;

  public RefreshSchemaActivityImpl(Optional<ConfigRepository> configRepository,
                                   SourceApi sourceApi,
                                   EnvVariableFeatureFlags envVariableFeatureFlags) {
    this.configRepository = configRepository;
    this.sourceApi = sourceApi;
    this.envVariableFeatureFlags = envVariableFeatureFlags;
  }

  @Override
  @Trace(operationName = ACTIVITY_TRACE_OPERATION_NAME)
  public boolean shouldRefreshSchema(UUID sourceCatalogId) {
    // if job persistence is unavailable, default to skipping the schema refresh
    if (configRepository.isEmpty() || !envVariableFeatureFlags.autoDetectSchema()) {
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
      Optional<ActorCatalogFetchEvent> mostRecentFetchEvent = configRepository.get().getMostRecentActorCatalogFetchEventForSource(sourceCatalogId);
      if (mostRecentFetchEvent.isEmpty()) {
        return false;
      }
      return mostRecentFetchEvent.get().getCreatedAt() > OffsetDateTime.now().minusHours(24l).toEpochSecond();
    } catch (IOException e) {
      // catching this exception because we don't want to block replication due to a failed schema refresh
      log.info("Encountered an error fetching most recent actor catalog fetch event: ", e);
      return true;
    }
  }

}
