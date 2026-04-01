/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.cdc

import io.airbyte.integrations.source.postgres.config.CdcIncrementalConfiguration
import io.airbyte.integrations.source.postgres.config.PostgresSourceConfiguration
import io.micronaut.context.condition.Condition
import io.micronaut.context.condition.ConditionContext

/**
 * Micronaut [Condition] that evaluates to `true` only when the connector is configured for CDC
 * (logical replication). Used with `@Requires(condition = CdcCondition::class)` to prevent
 * CDC-specific beans from being instantiated for non-CDC connections.
 */
class CdcCondition : Condition {
    override fun matches(context: ConditionContext<*>): Boolean {
        val config = context.beanContext.getBean(PostgresSourceConfiguration::class.java)
        return config.incrementalConfiguration is CdcIncrementalConfiguration
    }
}
