/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.dev_null

import io.airbyte.cdk.load.dataflow.config.AggregatePublishingConfig
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton

@Factory
class DevNullBeanFactory {
    @Singleton fun aggregatePublishingConfig() = AggregatePublishingConfig()
}
