/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.features;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class FeatureFlagHelperTest {

  FeatureFlags featureFlags;

  @BeforeEach
  void beforeEach() {
    featureFlags = mock(FeatureFlags.class);
  }

  @Test
  void isFieldSelectionEnabledForWorkspaceWithEmptyString() {
    when(featureFlags.fieldSelectionWorkspaces()).thenReturn("");

    assertFalse(FeatureFlagHelper.isFieldSelectionEnabledForWorkspace(featureFlags, UUID.randomUUID()));
  }

  @Test
  void isFieldSelectionEnabledForWorkspaceWithSpaceString() {
    when(featureFlags.fieldSelectionWorkspaces()).thenReturn(" ");

    assertFalse(FeatureFlagHelper.isFieldSelectionEnabledForWorkspace(featureFlags, UUID.randomUUID()));
  }

  @Test
  void isFieldSelectionEnabledForWorkspaceWithNullString() {
    when(featureFlags.fieldSelectionWorkspaces()).thenReturn(null);

    assertFalse(FeatureFlagHelper.isFieldSelectionEnabledForWorkspace(featureFlags, UUID.randomUUID()));
  }

  @Test
  void isFieldSelectionEnabledForWorkspaceWithSomeIdsAndAMatch() {
    final UUID workspaceId = UUID.randomUUID();
    final UUID randomId = UUID.randomUUID();
    when(featureFlags.fieldSelectionWorkspaces()).thenReturn(randomId.toString() + "," + workspaceId.toString());

    assertTrue(FeatureFlagHelper.isFieldSelectionEnabledForWorkspace(featureFlags, workspaceId));
  }

  @Test
  void isFieldSelectionEnabledForWorkspaceWithSomeIdsAndNoMatch() {
    final UUID workspaceId = UUID.randomUUID();
    final UUID randomId1 = UUID.randomUUID();
    final UUID randomId2 = UUID.randomUUID();
    when(featureFlags.fieldSelectionWorkspaces()).thenReturn(randomId1.toString() + "," + randomId2.toString());

    assertFalse(FeatureFlagHelper.isFieldSelectionEnabledForWorkspace(featureFlags, workspaceId));
  }

}
