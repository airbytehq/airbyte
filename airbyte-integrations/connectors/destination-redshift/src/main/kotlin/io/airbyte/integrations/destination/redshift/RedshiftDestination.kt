/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.redshift

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.integrations.base.Destination
import io.airbyte.cdk.integrations.base.IntegrationRunner
import io.airbyte.cdk.integrations.destination.jdbc.copy.SwitchingDestination
import io.airbyte.commons.json.Jsons.deserialize
import io.airbyte.commons.resources.MoreResources.readResource
import io.airbyte.integrations.destination.redshift.util.RedshiftUtil
import io.airbyte.protocol.models.v0.ConnectorSpecification
import java.util.function.Function
import org.slf4j.Logger
import org.slf4j.LoggerFactory

/**
 * The Redshift Destination offers two replication strategies. The first inserts via a typical SQL
 * Insert statement. Although less efficient, this requires less user set up. See
 * [RedshiftInsertDestination] for more detail. The second inserts via streaming the data to an S3
 * bucket, and Cop-ing the date into Redshift. This is more efficient, and recommended for
 * production workloads, but does require users to set up an S3 bucket and pass in additional
 * credentials. See [RedshiftStagingS3Destination] for more detail. This class inspect the given
 * arguments to determine which strategy to use.
 */
class RedshiftDestination :
    SwitchingDestination<RedshiftDestination.DestinationType>(
        DestinationType::class.java,
        Function<JsonNode, DestinationType> { config: JsonNode -> getTypeFromConfig(config) },
        destinationMap
    ) {
    enum class DestinationType {
        STANDARD,
        COPY_S3
    }

    @Throws(Exception::class)
    override fun spec(): ConnectorSpecification {
        // inject the standard ssh configuration into the spec.
        val originalSpec = super.spec()
        val propNode = originalSpec.connectionSpecification["properties"] as ObjectNode
        propNode.set<JsonNode>("tunnel_method", deserialize(readResource("ssh-tunnel-spec.json")))
        return originalSpec
    }

    override val isV2Destination: Boolean
        get() = true

    companion object {
        private val LOGGER: Logger = LoggerFactory.getLogger(RedshiftDestination::class.java)

        private val destinationMap: Map<DestinationType, Destination> =
            java.util.Map.of<DestinationType, Destination>(
                DestinationType.STANDARD,
                RedshiftInsertDestination.Companion.sshWrappedDestination(),
                DestinationType.COPY_S3,
                RedshiftStagingS3Destination.Companion.sshWrappedDestination()
            )

        private fun getTypeFromConfig(config: JsonNode): DestinationType {
            return determineUploadMode(config)
        }

        @JvmStatic
        fun determineUploadMode(config: JsonNode): DestinationType {
            val jsonNode = RedshiftUtil.findS3Options(config)

            if (RedshiftUtil.anyOfS3FieldsAreNullOrEmpty(jsonNode)) {
                LOGGER.warn(
                    "The \"standard\" upload mode is not performant, and is not recommended for production. " +
                        "Please use the Amazon S3 upload mode if you are syncing a large amount of data."
                )
                return DestinationType.STANDARD
            }
            return DestinationType.COPY_S3
        }

        @Throws(Exception::class)
        @JvmStatic
        fun main(args: Array<String>) {
            val destination: Destination = RedshiftDestination()
            LOGGER.info("starting destination: {}", RedshiftDestination::class.java)
            IntegrationRunner(destination).run(args)
            LOGGER.info("completed destination: {}", RedshiftDestination::class.java)
        }
    }
}
