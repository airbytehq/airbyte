/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.mysql

import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.db.jdbc.JdbcUtils
import io.airbyte.cdk.integrations.base.Destination
import io.airbyte.cdk.integrations.base.IntegrationRunner
import io.airbyte.cdk.integrations.base.spec_modification.SpecModifyingDestination
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.v0.ConnectorSpecification
import org.slf4j.Logger
import org.slf4j.LoggerFactory

class MySQLDestinationStrictEncrypt :
    SpecModifyingDestination(MySQLDestination.sshWrappedDestination()), Destination {
    override fun modifySpec(originalSpec: ConnectorSpecification): ConnectorSpecification {
        val spec: ConnectorSpecification = Jsons.clone(originalSpec)
        (spec.connectionSpecification["properties"] as ObjectNode).remove(JdbcUtils.SSL_KEY)
        return spec
    }

    companion object {
        private val LOGGER: Logger =
            LoggerFactory.getLogger(MySQLDestinationStrictEncrypt::class.java)

        @Throws(Exception::class)
        @JvmStatic
        fun main(args: Array<String>) {
            val destination: Destination = MySQLDestinationStrictEncrypt()
            LOGGER.info("starting destination: {}", MySQLDestinationStrictEncrypt::class.java)
            try {
                IntegrationRunner(destination).run(args)
            } catch (e: Exception) {
                MySQLDestination.handleException(e)
            }
            LOGGER.info("completed destination: {}", MySQLDestinationStrictEncrypt::class.java)
        }
    }
}
