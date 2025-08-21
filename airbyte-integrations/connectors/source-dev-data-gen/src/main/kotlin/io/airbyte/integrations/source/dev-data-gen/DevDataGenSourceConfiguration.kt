/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mysql

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.command.CdcSourceConfiguration
import io.airbyte.cdk.command.ConfigurationSpecificationSupplier
import io.airbyte.cdk.command.FeatureFlag
import io.airbyte.cdk.command.JdbcSourceConfiguration
import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.command.SourceConfigurationFactory
import io.airbyte.cdk.jdbc.SSLCertificateUtils
import io.airbyte.cdk.output.DataChannelMedium
import io.airbyte.cdk.output.DataChannelMedium.SOCKET
import io.airbyte.cdk.output.DataChannelMedium.STDIO
import io.airbyte.cdk.output.sockets.DATA_CHANNEL_PROPERTY_PREFIX
import io.airbyte.cdk.ssh.SshConnectionOptions
import io.airbyte.cdk.ssh.SshNoTunnelMethod
import io.airbyte.cdk.ssh.SshTunnelMethodConfiguration
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Value
import jakarta.inject.Inject
import jakarta.inject.Singleton
import java.net.MalformedURLException
import java.net.URI
import java.net.URL
import java.net.URLDecoder
import java.nio.charset.StandardCharsets
import java.nio.file.FileSystems
import java.time.Duration
import java.util.UUID

private val log = KotlinLogging.logger {}

/** Dev data gen-specific implementation of [SourceConfiguration] */
data class DevDataGenSourceConfiguration(
    val maxMessages: Long = 1000,
    val testType: String = "continuous_feed",
    val messageIntervalMs: Long? = null,
    val seed: Long? = null
) : SourceConfiguration()

@Singleton
class DevDataGenSourceConfigurationFactory:
    SourceConfigurationFactory<DevDataGenSourceConfigurationSpecification, DevDataGenSourceConfiguration> {

    override fun makeWithoutExceptionHandling(pojo: DevDataGenSourceConfigurationSpecification):
        DevDataGenSourceConfiguration {

        return DevDataGenSourceConfiguration(
            maxMessages = pojo.maxMessages,
            testType = pojo.testType,
            messageIntervalMs = pojo.messageIntervalMs,
            seed = pojo.seed
        )
    }
}
