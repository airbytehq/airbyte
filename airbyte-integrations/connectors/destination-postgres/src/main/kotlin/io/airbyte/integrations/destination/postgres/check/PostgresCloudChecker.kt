/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.check

import io.airbyte.cdk.command.AIRBYTE_CLOUD_ENV
import io.airbyte.cdk.load.check.DestinationCheckerV2
import io.airbyte.cdk.ssh.SshNoTunnelMethod
import io.airbyte.integrations.destination.postgres.client.PostgresAirbyteClient
import io.airbyte.integrations.destination.postgres.spec.PostgresConfiguration
import io.airbyte.integrations.destination.postgres.spec.SslModeRequire
import io.airbyte.integrations.destination.postgres.spec.SslModeVerifyCa
import io.airbyte.integrations.destination.postgres.spec.SslModeVerifyFull
import io.micronaut.context.annotation.Requires
import jakarta.inject.Inject
import jakarta.inject.Singleton

@Singleton
@Requires(env = [AIRBYTE_CLOUD_ENV])
class PostgresCloudChecker(
    private val postgresConfiguration: PostgresConfiguration,
    private val postgresOssChecker: PostgresOssChecker,
) : DestinationCheckerV2 {

    @Inject
    constructor(
        postgresConfiguration: PostgresConfiguration,
        postgresAirbyteClient: PostgresAirbyteClient,
    ) : this(
        postgresConfiguration,
        PostgresOssChecker(postgresAirbyteClient, postgresConfiguration)
    )

    override fun check() {
        if (postgresConfiguration.tunnelMethod is SshNoTunnelMethod) {
            val sslMode = postgresConfiguration.sslMode
            require(
                sslMode is SslModeRequire ||
                    sslMode is SslModeVerifyCa ||
                    sslMode is SslModeVerifyFull
            ) {
                "Unsecured connection not allowed. If no SSH Tunnel set up, please use one of the following SSL modes: require, verify-ca, verify-full"
            }
        }

        postgresOssChecker.check()
    }
}
