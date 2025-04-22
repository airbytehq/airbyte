/* Copyright (c) 2025 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.db2.config

import io.airbyte.cdk.command.SourceConfigurationFactory
import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Requires
import io.micronaut.context.env.Environment
import jakarta.inject.Singleton
import java.time.Duration

@Singleton
@Requires(env = [Environment.TEST])
@Primary
class Db2SourceTestConfigurationFactory :
    SourceConfigurationFactory<Db2SourceConfigurationSpecification, Db2SourceConfiguration> {
    override fun makeWithoutExceptionHandling(
        pojo: Db2SourceConfigurationSpecification,
    ): Db2SourceConfiguration =
        Db2SourceConfigurationFactory()
            .makeWithoutExceptionHandling(pojo)
            .copy(
                maxConcurrency = 1,
                checkpointTargetInterval = Duration.ofSeconds(3),
            )
}
