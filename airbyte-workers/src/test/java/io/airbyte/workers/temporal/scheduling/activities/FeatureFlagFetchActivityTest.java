/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.activities;

import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import io.airbyte.api.client.generated.WorkspaceApi;
import io.airbyte.api.client.invoker.generated.ApiException;
import io.airbyte.api.client.model.generated.ConnectionIdRequestBody;
import io.airbyte.api.client.model.generated.WorkspaceRead;
import io.airbyte.featureflag.FeatureFlagClient;
import io.airbyte.featureflag.FieldSelectionEnabled;
import io.airbyte.featureflag.TestClient;
import java.util.Map;
import java.util.UUID;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class FeatureFlagFetchActivityTest {

  final static UUID CONNECTION_ID = UUID.randomUUID();
  final static UUID WORKSPACE_ID = UUID.randomUUID();

  FeatureFlagFetchActivity featureFlagFetchActivity;
  FeatureFlagClient featureFlagClient;

  @BeforeEach
  void setUp() throws ApiException {
    final WorkspaceApi workspaceApi = mock(WorkspaceApi.class);

    featureFlagClient = new TestClient(Map.of(FieldSelectionEnabled.INSTANCE.getKey(), true));
    featureFlagFetchActivity = new FeatureFlagFetchActivityImpl(workspaceApi, featureFlagClient);

    when(workspaceApi.getWorkspaceByConnectionId(new ConnectionIdRequestBody().connectionId(CONNECTION_ID)))
        .thenReturn(new WorkspaceRead().workspaceId(WORKSPACE_ID));
  }

  @Test
  void testGetFeatureFlags() {
    final FeatureFlagFetchActivity.FeatureFlagFetchInput input = new FeatureFlagFetchActivity.FeatureFlagFetchInput(CONNECTION_ID);

    final FeatureFlagFetchActivity.FeatureFlagFetchOutput output = featureFlagFetchActivity.getFeatureFlags(input);
    Assertions.assertEquals(output.getFeatureFlags(), Map.of(FieldSelectionEnabled.INSTANCE.getKey(), true));

  }

}
