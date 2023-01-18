/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.activities;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import io.airbyte.api.client.generated.SourceApi;
import io.airbyte.api.client.invoker.generated.ApiException;
import io.airbyte.api.client.model.generated.ActorCatalogWithUpdatedAt;
import io.airbyte.api.client.model.generated.SourceDiscoverSchemaRequestBody;
import io.airbyte.commons.features.EnvVariableFeatureFlags;
import io.airbyte.workers.temporal.sync.RefreshSchemaActivityImpl;
import java.time.OffsetDateTime;
import java.util.UUID;
import org.assertj.core.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
class RefreshSchemaActivityTest {

  static private SourceApi mSourceApi;
  static private EnvVariableFeatureFlags mEnvVariableFeatureFlags;

  static private RefreshSchemaActivityImpl refreshSchemaActivity;

  static private final UUID SOURCE_ID = UUID.randomUUID();

  @BeforeEach
  void setUp() {
    mSourceApi = mock(SourceApi.class);
    mEnvVariableFeatureFlags = mock(EnvVariableFeatureFlags.class);
    mSourceApi = mock(SourceApi.class);
    when(mEnvVariableFeatureFlags.autoDetectSchema()).thenReturn(true);
    refreshSchemaActivity = new RefreshSchemaActivityImpl(mSourceApi, mEnvVariableFeatureFlags);
  }

  @Test
  void testShouldRefreshSchemaNoRecentRefresh() throws ApiException {
    when(mSourceApi.getMostRecentSourceActorCatalog(any())).thenReturn(new ActorCatalogWithUpdatedAt());
    Assertions.assertThat(true).isEqualTo(refreshSchemaActivity.shouldRefreshSchema(SOURCE_ID));
  }

  @Test
  void testShouldRefreshSchemaRecentRefreshOver24HoursAgo() throws ApiException {
    Long twoDaysAgo = OffsetDateTime.now().minusHours(48l).toEpochSecond();
    ActorCatalogWithUpdatedAt actorCatalogWithUpdatedAt = new ActorCatalogWithUpdatedAt().updatedAt(twoDaysAgo);
    when(mSourceApi.getMostRecentSourceActorCatalog(any())).thenReturn(actorCatalogWithUpdatedAt);
    Assertions.assertThat(true).isEqualTo(refreshSchemaActivity.shouldRefreshSchema(SOURCE_ID));
  }

  @Test
  void testShouldRefreshSchemaRecentRefreshLessThan24HoursAgo() throws ApiException {
    Long twelveHoursAgo = OffsetDateTime.now().minusHours(12l).toEpochSecond();
    ActorCatalogWithUpdatedAt actorCatalogWithUpdatedAt = new ActorCatalogWithUpdatedAt().updatedAt(twelveHoursAgo);
    when(mSourceApi.getMostRecentSourceActorCatalog(any())).thenReturn(actorCatalogWithUpdatedAt);
    Assertions.assertThat(false).isEqualTo(refreshSchemaActivity.shouldRefreshSchema(SOURCE_ID));
  }

  @Test
  void testRefreshSchema() throws ApiException {
    UUID sourceId = UUID.randomUUID();
    UUID connectionId = UUID.randomUUID();
    refreshSchemaActivity.refreshSchema(sourceId, connectionId);
    SourceDiscoverSchemaRequestBody requestBody =
        new SourceDiscoverSchemaRequestBody().sourceId(sourceId).disableCache(true).connectionId(connectionId);
    verify(mSourceApi, times(1)).discoverSchemaForSource(requestBody);
  }

}
