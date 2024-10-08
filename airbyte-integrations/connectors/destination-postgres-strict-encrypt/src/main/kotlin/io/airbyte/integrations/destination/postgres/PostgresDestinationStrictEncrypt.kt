/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.postgres

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.db.jdbc.JdbcUtils
import io.airbyte.cdk.integrations.base.AirbyteExceptionHandler
import io.airbyte.cdk.integrations.base.Destination
import io.airbyte.cdk.integrations.base.IntegrationRunner
import io.airbyte.cdk.integrations.base.spec_modification.SpecModifyingDestination
import io.airbyte.commons.json.Jsons
import io.airbyte.integrations.destination.postgres.PostgresDestination.Companion.sshWrappedDestination
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
import io.airbyte.protocol.models.v0.ConnectorSpecification
import org.postgresql.util.PSQLException
import org.slf4j.Logger
import org.slf4j.LoggerFactory

class PostgresDestinationStrictEncrypt :
    SpecModifyingDestination(sshWrappedDestination()), Destination {
    override fun modifySpec(originalSpec: ConnectorSpecification): ConnectorSpecification {
        val spec: ConnectorSpecification = Jsons.clone<ConnectorSpecification>(originalSpec)
        (spec.connectionSpecification[PROPERTIES] as ObjectNode).remove(JdbcUtils.SSL_KEY)
        return spec
    }

    @Throws(Exception::class)
    override fun check(config: JsonNode): AirbyteConnectionStatus? {
        if (
            (config.has(TUNNEL_METHOD) && config[TUNNEL_METHOD].has(TUNNEL_METHOD)) &&
                config[TUNNEL_METHOD][TUNNEL_METHOD].asText() == NO_TUNNEL
        ) {
            // If no SSH tunnel
            if (config.has(SSL_MODE) && config[SSL_MODE].has(MODE)) {
                if (
                    setOf(SSL_MODE_DISABLE, SSL_MODE_ALLOW, SSL_MODE_PREFER)
                        .contains(config[SSL_MODE][MODE].asText())
                ) {
                    // Fail in case SSL mode is disable, allow or prefer
                    return AirbyteConnectionStatus()
                        .withStatus(AirbyteConnectionStatus.Status.FAILED)
                        .withMessage(
                            "Unsecured connection not allowed. If no SSH Tunnel set up, please use one of the following SSL modes: require, verify-ca, verify-full"
                        )
                }
            }
        }
        return super.check(config)
    }

    override val isV2Destination: Boolean
        get() = true

    companion object {
        private val LOGGER: Logger =
            LoggerFactory.getLogger(PostgresDestinationStrictEncrypt::class.java)
        private const val PROPERTIES = "properties"
        const val TUNNEL_METHOD: String = "tunnel_method"
        const val NO_TUNNEL: String = "NO_TUNNEL"
        const val SSL_MODE: String = "ssl_mode"
        const val MODE: String = "mode"
        const val SSL_MODE_ALLOW: String = "allow"
        const val SSL_MODE_PREFER: String = "prefer"
        const val SSL_MODE_DISABLE: String = "disable"

        @Throws(Exception::class)
        @JvmStatic
        fun main(args: Array<String>) {
            AirbyteExceptionHandler.addThrowableForDeinterpolation(PSQLException::class.java)
            val destination: Destination = PostgresDestinationStrictEncrypt()
            LOGGER.info("starting destination: {}", PostgresDestinationStrictEncrypt::class.java)
            IntegrationRunner(destination).run(args)
            LOGGER.info("completed destination: {}", PostgresDestinationStrictEncrypt::class.java)
        }
    }
}
