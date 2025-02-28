/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.oracle

import io.airbyte.cdk.command.SourceConfigurationFactory
import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Requires
import io.micronaut.context.env.Environment
import jakarta.inject.Singleton
import java.time.Duration

@Singleton
@Requires(env = [Environment.TEST])
@Primary
class OracleSourceTestConfigurationFactory :
    SourceConfigurationFactory<OracleSourceConfigurationSpecification, OracleSourceConfiguration> {
    override fun makeWithoutExceptionHandling(
        pojo: OracleSourceConfigurationSpecification,
    ): OracleSourceConfiguration =
        OracleSourceConfigurationFactory()
            .makeWithoutExceptionHandling(pojo)
            .copy(
                maxConcurrency = 1,
                checkpointTargetInterval = Duration.ofSeconds(3),
                debeziumHeartbeatInterval = Duration.ofMillis(100),
            )
}
