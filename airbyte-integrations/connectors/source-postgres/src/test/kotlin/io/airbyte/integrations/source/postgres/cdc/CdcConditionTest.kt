/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.cdc

import io.airbyte.integrations.source.postgres.config.CdcIncrementalConfiguration
import io.airbyte.integrations.source.postgres.config.PostgresSourceConfiguration
import io.airbyte.integrations.source.postgres.config.UserDefinedCursorIncrementalConfiguration
import io.airbyte.integrations.source.postgres.config.XminIncrementalConfiguration
import io.micronaut.context.ApplicationContext
import io.micronaut.context.condition.ConditionContext
import io.mockk.every
import io.mockk.mockk
import java.time.Duration
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class CdcConditionTest {

    private val condition = CdcCondition()

    private fun mockConditionContext(config: PostgresSourceConfiguration): ConditionContext<*> {
        val beanContext = mockk<ApplicationContext>()
        every { beanContext.getBean(PostgresSourceConfiguration::class.java) } returns config
        val conditionContext = mockk<ConditionContext<*>>()
        every { conditionContext.beanContext } returns beanContext
        return conditionContext
    }

    private fun makeConfig(
        incrementalConfiguration:
            io.airbyte.integrations.source.postgres.config.IncrementalConfiguration
    ): PostgresSourceConfiguration =
        PostgresSourceConfiguration(
            realHost = "localhost",
            realPort = 5432,
            sshTunnel = null,
            sshConnectionOptions = io.airbyte.cdk.ssh.SshConnectionOptions(),
            jdbcUrlFmt = "jdbc:postgresql://%s:%d/test",
            jdbcProperties = mapOf("user" to "test"),
            database = "test",
            namespaces = setOf("public"),
            incrementalConfiguration = incrementalConfiguration,
            maxConcurrency = 1,
            checkpointTargetInterval = Duration.ofSeconds(60),
            checkPrivileges = true,
        )

    @Test
    fun `matches returns true when CDC is configured`() {
        val config =
            makeConfig(
                CdcIncrementalConfiguration(
                    initialLoadTimeout = Duration.ofHours(8),
                    invalidCdcCursorPositionBehavior =
                        io.airbyte.integrations.source.postgres.config
                            .InvalidCdcCursorPositionBehavior
                            .FAIL_SYNC,
                    shutdownTimeout = Duration.ofSeconds(60),
                    replicationSlot = "airbyte_slot",
                    publication = "airbyte_publication",
                    debeziumCommitsLsn = false,
                    heartbeatActionQuery = null,
                    airbyteHeartbeatTimeout = Duration.ofSeconds(1200),
                )
            )
        assertTrue(condition.matches(mockConditionContext(config)))
    }

    @Test
    fun `matches returns false when UserDefinedCursor is configured`() {
        val config = makeConfig(UserDefinedCursorIncrementalConfiguration)
        assertFalse(condition.matches(mockConditionContext(config)))
    }

    @Test
    fun `matches returns false when Xmin is configured`() {
        val config = makeConfig(XminIncrementalConfiguration)
        assertFalse(condition.matches(mockConditionContext(config)))
    }
}
