/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.featureflag

import com.launchdarkly.shaded.kotlin.Pair
import io.airbyte.commons.features.FeatureFlags
import io.mockk.every
import io.mockk.mockk
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.slf4j.Logger
import org.slf4j.LoggerFactory
import kotlin.test.assertFalse
import kotlin.test.assertTrue
import java.util.UUID

internal class FeatureFlagHelperTest {


    var featureFlags: FeatureFlags? = null
    var featureFlagClient: TestClient? = null
    var log: Logger? = null
    @BeforeEach
    fun beforeEach() {
        featureFlags = mockk()
        featureFlagClient = mockk()
        log = mockk()
        every {featureFlagClient!!.enabled(ColumnSelectionExcludeForUnexpectedFields, any())} answers {false}
    }

    @Test
    fun `verify isFieldSelectionEnabledForWorkspace with empty string`() {
        every {featureFlags!!.fieldSelectionWorkspaces()} answers {""}
        every {featureFlags!!.applyFieldSelection()} answers {false}
        assertFalse(isFieldSelectionEnabledForWorkspace(featureFlags!!, featureFlagClient!!, UUID.randomUUID(), log!!))
    }

    @Test
    fun `isFieldSelectionEnabledForWorkspace with space string`() {
        every {featureFlags!!.fieldSelectionWorkspaces()} answers {" "}
        every {featureFlags!!.applyFieldSelection()} answers {false}
        assertFalse(isFieldSelectionEnabledForWorkspace(featureFlags!!, featureFlagClient!!, UUID.randomUUID(), log!!))
    }

    @Test
    fun `isFieldSelectionEnabledForWorkspace with null string`() {
        every {featureFlags!!.fieldSelectionWorkspaces()} answers {null}
        every {featureFlags!!.applyFieldSelection()} answers {false}
        assertFalse(isFieldSelectionEnabledForWorkspace(featureFlags!!, featureFlagClient!!, UUID.randomUUID(), log!!))
    }

    @Test
    fun `isFieldSelectionEnabledForWorkspace with some ids and a match`() {
        val workspaceId = UUID.randomUUID()
        val randomId = UUID.randomUUID()
        every {featureFlags!!.fieldSelectionWorkspaces()} answers {"$workspaceId,$randomId"}
        every {featureFlags!!.applyFieldSelection()} answers {false}
        assertTrue(isFieldSelectionEnabledForWorkspace(featureFlags!!, featureFlagClient!!, workspaceId, log!!))
    }

    @Test
    fun `isFieldSelectionEnabledForWorkspace with some ids and no match`() {
        val workspaceId = UUID.randomUUID()
        val randomId1 = UUID.randomUUID()
        val randomId2 = UUID.randomUUID()
        every {featureFlags!!.fieldSelectionWorkspaces()} answers {"$randomId1,$randomId2"}
        every {featureFlags!!.applyFieldSelection()} answers {false}
        assertFalse(isFieldSelectionEnabledForWorkspace(featureFlags!!, featureFlagClient!!, workspaceId, log!!))
    }

    @Test
    fun `isFieldSelectionEnabledForWorkspace both include and exclude lists`() {
        val workspaceId = UUID.randomUUID()
        every {featureFlags!!.fieldSelectionWorkspaces()} answers {"$workspaceId"}
        every {featureFlagClient!!.enabled(ColumnSelectionExcludeForUnexpectedFields, Workspace(workspaceId))} answers {true}
        // Field selection is enabled because the include-list takes precedence.
        assertTrue(isFieldSelectionEnabledForWorkspace(featureFlags!!, featureFlagClient!!, workspaceId, log!!))
    }

    @Test
    fun `isFieldSelectionEnabledForWorkspace disabled by exclude list`() {
        val workspaceId = UUID.randomUUID()
        every {featureFlags!!.fieldSelectionWorkspaces()} answers {""}
        every {featureFlags!!.applyFieldSelection()} answers {true}
        every {featureFlagClient!!.enabled(ColumnSelectionExcludeForUnexpectedFields, Workspace(workspaceId))} answers {true}
        // Field selection is disabled because the exclude-list takes precedence over the general flag.
        assertFalse(isFieldSelectionEnabledForWorkspace(featureFlags!!, featureFlagClient!!, workspaceId, log!!))
    }

    @Test
    fun `isFieldSelectionEnabledForWorkspace uses applyFieldSelection flag if neither other flag applies`() {
        val workspaceId = UUID.randomUUID()
        every {featureFlags!!.fieldSelectionWorkspaces()} answers {""}
        every {featureFlags!!.applyFieldSelection()} answers {true}
        every {featureFlagClient!!.enabled(ColumnSelectionExcludeForUnexpectedFields, Workspace(workspaceId))} answers {false}
        assertTrue(isFieldSelectionEnabledForWorkspace(featureFlags!!, featureFlagClient!!, workspaceId, log!!))
    }
}