/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.sync;

import static io.airbyte.metrics.lib.ApmTraceConstants.ACTIVITY_TRACE_OPERATION_NAME;

import datadog.trace.api.Trace;
import io.airbyte.api.client.AirbyteApiClient;
import io.airbyte.api.client.invoker.generated.ApiException;
import io.airbyte.api.client.model.generated.SourceDiscoverSchemaRequestBody;
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

  private final AirbyteApiClient airbyteApiClient;

  public RefreshSchemaActivityImpl(Optional<ConfigRepository> configRepository, AirbyteApiClient airbyteApiClient) {
    this.configRepository = configRepository;
    this.airbyteApiClient = airbyteApiClient;
  }

  @Override
  @Trace(operationName = ACTIVITY_TRACE_OPERATION_NAME)
  public boolean shouldRefreshSchema(UUID sourceCatalogId) throws IOException {
    // if job persistence is unavailable, default to skipping the schema refresh
    if (configRepository.isEmpty()) {
      return false;
    }

    return !schemaRefreshRanRecently(sourceCatalogId);
  }

  @Override
  public void refreshSchema(UUID sourceCatalogId, UUID connectionId) throws ApiException {
    SourceDiscoverSchemaRequestBody requestBody =
        new SourceDiscoverSchemaRequestBody().sourceId(sourceCatalogId).disableCache(true).connectionId(connectionId);

    try {
      airbyteApiClient.getSourceApi().discoverSchemaForSource(requestBody);
    } catch (final Exception e) {
      log.info("Attempted schema refresh, but failed.");
    }
  }

  private boolean schemaRefreshRanRecently(UUID sourceCatalogId) throws IOException {
    Optional<ActorCatalogFetchEvent> mostRecentFetchEvent = configRepository.get().getMostRecentActorCatalogFetchEventForSource(sourceCatalogId);

    if (mostRecentFetchEvent.isEmpty()) {
      return false;
    }

    return mostRecentFetchEvent.get().getCreatedAt() > OffsetDateTime.now().minusHours(24l).toEpochSecond();
  }

}
