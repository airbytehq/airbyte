/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mysql

import io.airbyte.cdk.command.SourceConfigurationFactory
import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Requires
import io.micronaut.context.env.Environment
import jakarta.inject.Singleton
import java.time.Duration

@Singleton
@Requires(env = [Environment.TEST])
@Primary
class MysqlSourceTestConfigurationFactory :
    SourceConfigurationFactory<MysqlSourceConfigurationJsonObject, MysqlSourceConfiguration> {
    override fun makeWithoutExceptionHandling(
        pojo: MysqlSourceConfigurationJsonObject,
    ): MysqlSourceConfiguration =
        MysqlSourceConfigurationFactory()
            .makeWithoutExceptionHandling(pojo)
            .copy(maxConcurrency = 1, checkpointTargetInterval = Duration.ofSeconds(3))
}
