/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.cdc

import io.airbyte.integrations.source.postgres.config.CdcIncrementalConfiguration
import io.airbyte.integrations.source.postgres.config.PostgresSourceConfiguration
import io.airbyte.integrations.source.postgres.config.UserDefinedCursorIncrementalConfiguration
import io.micronaut.context.ApplicationContext
import io.micronaut.context.condition.ConditionContext
import io.mockk.every
import io.mockk.mockk
import java.time.Duration
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class CdcConditionTest {

    @Test
    fun `CdcCondition matches when configuration uses CDC`() {
        val cdcConfig =
            CdcIncrementalConfiguration(
                initialLoadTimeout = Duration.ofHours(8),
                invalidCdcCursorPositionBehavior =
                    io.airbyte.integrations.source.postgres.config.InvalidCdcCursorPositionBehavior
                        .FAIL_SYNC,
                shutdownTimeout = Duration.ofSeconds(60),
                replicationSlot = "test_slot",
                publication = "test_pub",
                debeziumCommitsLsn = false,
                heartbeatActionQuery = null,
                airbyteHeartbeatTimeout = Duration.ofSeconds(1200),
            )
        val config = mockk<PostgresSourceConfiguration>()
        every { config.incrementalConfiguration } returns cdcConfig

        val appContext = mockk<ApplicationContext>()
        every { appContext.getBean(PostgresSourceConfiguration::class.java) } returns config

        val conditionContext = mockk<ConditionContext<*>>()
        every { conditionContext.beanContext } returns appContext

        assertTrue(CdcCondition().matches(conditionContext))
    }

    @Test
    fun `CdcCondition does not match when configuration uses cursor-based replication`() {
        val config = mockk<PostgresSourceConfiguration>()
        every { config.incrementalConfiguration } returns UserDefinedCursorIncrementalConfiguration

        val appContext = mockk<ApplicationContext>()
        every { appContext.getBean(PostgresSourceConfiguration::class.java) } returns config

        val conditionContext = mockk<ConditionContext<*>>()
        every { conditionContext.beanContext } returns appContext

        assertFalse(CdcCondition().matches(conditionContext))
    }
}
