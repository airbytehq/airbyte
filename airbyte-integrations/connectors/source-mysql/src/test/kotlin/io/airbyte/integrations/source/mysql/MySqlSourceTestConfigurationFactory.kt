/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mysql

import io.airbyte.cdk.command.FeatureFlag
import io.airbyte.cdk.command.SourceConfigurationFactory
import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Requires
import io.micronaut.context.env.Environment
import jakarta.inject.Singleton
import java.time.Duration

@Singleton
@Requires(env = [Environment.TEST])
@Primary
class MySqlSourceTestConfigurationFactory(val featureFlags: Set<FeatureFlag>) :
    SourceConfigurationFactory<MySqlSourceConfigurationSpecification, MySqlSourceConfiguration> {
    override fun makeWithoutExceptionHandling(
        pojo: MySqlSourceConfigurationSpecification,
    ): MySqlSourceConfiguration =
        MySqlSourceConfigurationFactory(featureFlags)
            .makeWithoutExceptionHandling(pojo)
            .copy(
                maxConcurrency = 1,
                checkpointTargetInterval = Duration.ofSeconds(3),
                debeziumHeartbeatInterval = Duration.ofMillis(100),
                debeziumKeepAliveInterval = Duration.ofSeconds(1),
            )
}
