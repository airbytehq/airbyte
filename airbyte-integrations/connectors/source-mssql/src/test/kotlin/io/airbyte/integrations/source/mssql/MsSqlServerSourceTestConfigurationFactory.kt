/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mssql

import io.airbyte.cdk.command.FeatureFlag
import io.airbyte.cdk.command.SourceConfigurationFactory
import io.airbyte.integrations.source.mssql.config_spec.MsSqlServerSourceConfigurationSpecification
import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Requires
import io.micronaut.context.env.Environment
import jakarta.inject.Singleton

@Singleton
@Requires(env = [Environment.TEST])
@Primary
class MsSqlServerSourceTestConfigurationFactory(val featureFlags: Set<FeatureFlag>) :
    SourceConfigurationFactory<
        MsSqlServerSourceConfigurationSpecification, MsSqlServerSourceConfiguration> {
    override fun makeWithoutExceptionHandling(
        pojo: MsSqlServerSourceConfigurationSpecification,
    ): MsSqlServerSourceConfiguration =
        MsSqlServerSourceConfigurationFactory(featureFlags).makeWithoutExceptionHandling(pojo)
    /*.copy(
        maxConcurrency = 1,
        checkpointTargetInterval = Duration.ofSeconds(3),
        debeziumHeartbeatInterval = Duration.ofMillis(100),
        debeziumKeepAliveInterval = Duration.ofSeconds(1),
    )*/
}
