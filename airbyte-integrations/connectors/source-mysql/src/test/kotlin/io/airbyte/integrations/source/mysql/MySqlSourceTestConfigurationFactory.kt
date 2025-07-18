/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mysql

import io.airbyte.cdk.command.FeatureFlag
import io.airbyte.cdk.command.SourceConfigurationFactory
import io.airbyte.cdk.output.DataChannelMedium.STDIO
import io.airbyte.cdk.output.sockets.DATA_CHANNEL_PROPERTY_PREFIX
import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Requires
import io.micronaut.context.annotation.Value
import io.micronaut.context.env.Environment
import jakarta.inject.Singleton
import java.time.Duration

@Singleton
@Requires(env = [Environment.TEST])
@Primary
class MySqlSourceTestConfigurationFactory(
    val featureFlags: Set<FeatureFlag>,
    @Value("\${${DATA_CHANNEL_PROPERTY_PREFIX}.medium}") val dataChannelMedium: String = STDIO.name,
    @Value("\${${DATA_CHANNEL_PROPERTY_PREFIX}.socket-paths}")
    val socketPaths: List<String> = emptyList(),
) : SourceConfigurationFactory<MySqlSourceConfigurationSpecification, MySqlSourceConfiguration> {
    override fun makeWithoutExceptionHandling(
        pojo: MySqlSourceConfigurationSpecification,
    ): MySqlSourceConfiguration =
        MySqlSourceConfigurationFactory(featureFlags, dataChannelMedium, socketPaths)
            .makeWithoutExceptionHandling(pojo)
            .copy(
                checkpointTargetInterval = Duration.ofSeconds(3),
                debeziumHeartbeatInterval = Duration.ofMillis(100),
                debeziumKeepAliveInterval = Duration.ofSeconds(1),
            )
}
