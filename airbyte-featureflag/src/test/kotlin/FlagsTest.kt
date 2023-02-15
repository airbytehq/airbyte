/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.featureflag

import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import kotlin.test.assertFalse
import kotlin.test.assertTrue

class FieldSelectionWorkspacesTest {
    /**
     * Used for tracking the default fetcher on the [FieldSelectionWorkspaces].
     * As this test modifies the [FieldSelectionWorkspaces] fetcher object, it also needs
     * to ensure that it resets it back to its default state.
     */
    private lateinit var fetcher: (String) -> String?

    @BeforeEach
    fun setup() {
        fetcher = FieldSelectionWorkspaces.fetcher
    }

    @AfterEach
    fun teardown() {
        FieldSelectionWorkspaces.fetcher = fetcher
    }

    @Test
    fun `happy path`() {
        val workspaceIds = listOf("0000", "0001", "0002")
        FieldSelectionWorkspaces.fetcher = { workspaceIds.joinToString() }

        // true if matching workspace
        FieldSelectionWorkspaces.enabled(Workspace("0000"))
            .also { assertTrue(it) }

        // true if matching workspace in multi
        FieldSelectionWorkspaces.enabled(Multi(listOf(User("0000"), Workspace("0000"))))
            .also { assertTrue(it) }

        // false if no matching workspace
        FieldSelectionWorkspaces.enabled(Workspace("1111"))
            .also { assertFalse(it) }

        // false if incorrect type
        FieldSelectionWorkspaces.enabled(User("0000"))
            .also { assertFalse(it) }

        // false if matching workspace in multi
        FieldSelectionWorkspaces.enabled(Multi(listOf(User("0000"), Workspace("1111"))))
            .also { assertFalse(it) }

    }
}
