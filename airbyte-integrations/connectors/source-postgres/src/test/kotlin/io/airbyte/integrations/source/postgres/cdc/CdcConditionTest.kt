/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.cdc

import io.airbyte.integrations.source.postgres.PostgresSourceJdbcConnectionFactory
import io.mockk.confirmVerified
import io.mockk.mockk
import io.mockk.verify
import org.junit.jupiter.api.Test

class StartupStateLazyInitTest {

    @Test
    fun `StartupState does not execute any query during construction`() {
        val connectionFactory = mockk<PostgresSourceJdbcConnectionFactory>(relaxed = true)

        // Construction must not trigger any database interaction.
        StartupState(connectionFactory)

        // Verify that getConnection (the entry-point for every query) was never called.
        verify(exactly = 0) { connectionFactory.get() }
        confirmVerified(connectionFactory)
    }
}
