/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.activities;

import io.airbyte.api.client.AirbyteApiClient;
import io.airbyte.api.client.generated.ConnectionApi;
import io.airbyte.api.client.generated.SourceApi;
import io.airbyte.api.client.model.generated.ConnectionIdRequestBody;
import io.airbyte.api.client.model.generated.ConnectionRead;
import io.airbyte.api.client.model.generated.SourceIdRequestBody;
import io.airbyte.api.client.model.generated.SourceRead;
import io.airbyte.featureflag.FeatureFlagClient;
import io.airbyte.featureflag.FieldSelectionEnabled;
import io.airbyte.featureflag.Flag;
import io.airbyte.featureflag.Workspace;
import jakarta.inject.Singleton;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import lombok.extern.slf4j.Slf4j;

@Slf4j
@Singleton
public class FeatureFlagFetchActivityImpl implements FeatureFlagFetchActivity {

  private final SourceApi sourceApi;
  private final ConnectionApi connectionApi;
  private final FeatureFlagClient featureFlagClient;

  public FeatureFlagFetchActivityImpl(SourceApi sourceApi,
                                      ConnectionApi connectionApi,
                                      FeatureFlagClient featureFlagClient) {
    this.sourceApi = sourceApi;
    this.connectionApi = connectionApi;
    this.featureFlagClient = featureFlagClient;
  }

  public UUID getWorkspaceId(final UUID connectionId) {
    final ConnectionRead connection = AirbyteApiClient.retryWithJitter(
        () -> connectionApi.getConnection(new ConnectionIdRequestBody().connectionId(connectionId)),
        "get connection");

    final SourceRead source = AirbyteApiClient.retryWithJitter(
        () -> sourceApi.getSource(new SourceIdRequestBody().sourceId(connection.getSourceId())),
        "get source");

    return source.getWorkspaceId();
  }

  @Override
  public FeatureFlagFetchOutput getFeatureFlags(final FeatureFlagFetchInput input) {
    final UUID workspaceId = getWorkspaceId(input.getConnectionId());

    // TODO: remove this feature flag from here - not really needed by consumers but in here to get this
    // activity up and running
    final List<Flag> workspaceFlags = List.of(FieldSelectionEnabled.INSTANCE);
    final Map<String, Boolean> featureFlags = new HashMap<>();
    for (Flag flag : workspaceFlags) {
      featureFlags.put(flag.getKey(), featureFlagClient.enabled(flag, new Workspace(workspaceId)));
    }

    return new FeatureFlagFetchOutput(featureFlags);
  }

}
