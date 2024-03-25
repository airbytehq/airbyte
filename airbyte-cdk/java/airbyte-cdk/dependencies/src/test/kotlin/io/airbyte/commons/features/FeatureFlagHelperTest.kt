/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.commons.features

import java.util.*
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.mockito.Mockito

internal class FeatureFlagHelperTest {
    private lateinit var featureFlags: FeatureFlags

    @BeforeEach
    fun beforeEach() {
        featureFlags = Mockito.mock(FeatureFlags::class.java)
    }

    @Test
    fun isFieldSelectionEnabledForWorkspaceWithEmptyString() {
        Mockito.`when`(featureFlags!!.fieldSelectionWorkspaces()).thenReturn("")

        Assertions.assertFalse(
            FeatureFlagHelper.isWorkspaceIncludedInFlag(
                featureFlags,
                { obj: FeatureFlags -> obj.fieldSelectionWorkspaces() },
                UUID.randomUUID(),
                null
            )
        )
    }

    @Test
    fun isFieldSelectionEnabledForNullWorkspaceWithEmptyString() {
        Mockito.`when`(featureFlags!!.fieldSelectionWorkspaces()).thenReturn("")

        Assertions.assertFalse(
            FeatureFlagHelper.isWorkspaceIncludedInFlag(
                featureFlags,
                { obj: FeatureFlags -> obj.fieldSelectionWorkspaces() },
                null,
                null
            )
        )
    }

    @Test
    fun isFieldSelectionEnabledForWorkspaceWithSpaceString() {
        Mockito.`when`(featureFlags!!.fieldSelectionWorkspaces()).thenReturn(" ")

        Assertions.assertFalse(
            FeatureFlagHelper.isWorkspaceIncludedInFlag(
                featureFlags,
                { obj: FeatureFlags -> obj.fieldSelectionWorkspaces() },
                UUID.randomUUID(),
                null
            )
        )
    }

    @Test
    fun isFieldSelectionEnabledForWorkspaceWithNullString() {
        Mockito.`when`(featureFlags!!.fieldSelectionWorkspaces()).thenReturn(null)

        Assertions.assertFalse(
            FeatureFlagHelper.isWorkspaceIncludedInFlag(
                featureFlags,
                { obj: FeatureFlags -> obj.fieldSelectionWorkspaces() },
                UUID.randomUUID(),
                null
            )
        )
    }

    @Test
    fun isFieldSelectionEnabledForWorkspaceWithSomeIdsAndAMatch() {
        val workspaceId = UUID.randomUUID()
        val randomId = UUID.randomUUID()
        Mockito.`when`(featureFlags!!.fieldSelectionWorkspaces())
            .thenReturn("$randomId,$workspaceId")

        Assertions.assertTrue(
            FeatureFlagHelper.isWorkspaceIncludedInFlag(
                featureFlags,
                { obj: FeatureFlags -> obj.fieldSelectionWorkspaces() },
                workspaceId,
                null
            )
        )
    }

    @Test
    fun isFieldSelectionEnabledForWorkspaceWithSomeIdsAndNoMatch() {
        val workspaceId = UUID.randomUUID()
        val randomId1 = UUID.randomUUID()
        val randomId2 = UUID.randomUUID()
        Mockito.`when`(featureFlags!!.fieldSelectionWorkspaces())
            .thenReturn("$randomId1,$randomId2")

        Assertions.assertFalse(
            FeatureFlagHelper.isWorkspaceIncludedInFlag(
                featureFlags,
                { obj: FeatureFlags -> obj.fieldSelectionWorkspaces() },
                workspaceId,
                null
            )
        )
    }
}
