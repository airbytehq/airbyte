/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.commons.features

import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.mockito.Mockito
import java.util.*

internal class FeatureFlagHelperTest {
    var featureFlags: FeatureFlags? = null

    @BeforeEach
    fun beforeEach() {
        featureFlags = Mockito.mock(FeatureFlags::class.java)
    }

    @get:Test
    val isFieldSelectionEnabledForWorkspaceWithEmptyString: Unit
        get() {
            Mockito.`when`(featureFlags!!.fieldSelectionWorkspaces()).thenReturn("")

            Assertions.assertFalse(FeatureFlagHelper.isWorkspaceIncludedInFlag(featureFlags, { obj: FeatureFlags -> obj.fieldSelectionWorkspaces() }, UUID.randomUUID(), null))
        }

    @get:Test
    val isFieldSelectionEnabledForNullWorkspaceWithEmptyString: Unit
        get() {
            Mockito.`when`(featureFlags!!.fieldSelectionWorkspaces()).thenReturn("")

            Assertions.assertFalse(FeatureFlagHelper.isWorkspaceIncludedInFlag(featureFlags, { obj: FeatureFlags -> obj.fieldSelectionWorkspaces() }, null, null))
        }

    @get:Test
    val isFieldSelectionEnabledForWorkspaceWithSpaceString: Unit
        get() {
            Mockito.`when`(featureFlags!!.fieldSelectionWorkspaces()).thenReturn(" ")

            Assertions.assertFalse(FeatureFlagHelper.isWorkspaceIncludedInFlag(featureFlags, { obj: FeatureFlags -> obj.fieldSelectionWorkspaces() }, UUID.randomUUID(), null))
        }

    @get:Test
    val isFieldSelectionEnabledForWorkspaceWithNullString: Unit
        get() {
            Mockito.`when`(featureFlags!!.fieldSelectionWorkspaces()).thenReturn(null)

            Assertions.assertFalse(FeatureFlagHelper.isWorkspaceIncludedInFlag(featureFlags, { obj: FeatureFlags -> obj.fieldSelectionWorkspaces() }, UUID.randomUUID(), null))
        }

    @get:Test
    val isFieldSelectionEnabledForWorkspaceWithSomeIdsAndAMatch: Unit
        get() {
            val workspaceId = UUID.randomUUID()
            val randomId = UUID.randomUUID()
            Mockito.`when`(featureFlags!!.fieldSelectionWorkspaces()).thenReturn("$randomId,$workspaceId")

            Assertions.assertTrue(FeatureFlagHelper.isWorkspaceIncludedInFlag(featureFlags, { obj: FeatureFlags -> obj.fieldSelectionWorkspaces() }, workspaceId, null))
        }

    @get:Test
    val isFieldSelectionEnabledForWorkspaceWithSomeIdsAndNoMatch: Unit
        get() {
            val workspaceId = UUID.randomUUID()
            val randomId1 = UUID.randomUUID()
            val randomId2 = UUID.randomUUID()
            Mockito.`when`(featureFlags!!.fieldSelectionWorkspaces()).thenReturn("$randomId1,$randomId2")

            Assertions.assertFalse(FeatureFlagHelper.isWorkspaceIncludedInFlag(featureFlags, { obj: FeatureFlags -> obj.fieldSelectionWorkspaces() }, workspaceId, null))
        }
}
