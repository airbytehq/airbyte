/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.cdc

import io.airbyte.integrations.source.postgres.config.CdcIncrementalConfiguration
import io.airbyte.integrations.source.postgres.config.PostgresSourceConfiguration
import io.micronaut.context.condition.Condition
import io.micronaut.context.condition.ConditionContext

class CdcCondition : Condition {
    override fun matches(context: ConditionContext<*>): Boolean {
        val config = context.beanContext.getBean(PostgresSourceConfiguration::class.java)
        return config.incrementalConfiguration is CdcIncrementalConfiguration
    }
}
