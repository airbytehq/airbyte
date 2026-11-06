/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.dynamodb

import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.command.FeatureFlag
import io.airbyte.cdk.spec.IdentitySpecificationExtender
import io.airbyte.cdk.spec.SpecificationExtender
import io.airbyte.protocol.models.v0.ConnectorSpecification
import io.micronaut.context.annotation.Replaces
import jakarta.inject.Singleton

/**
 * Makes the `spec` output deployment-aware.
 *
 * Concurrent scans (several parallel-scan segments of a table, and several tables, read at once)
 * are only offered on Airbyte Cloud, where the connector runs with `AIRBYTE_EDITION=CLOUD` (
 * [FeatureFlag.AIRBYTE_CLOUD_DEPLOYMENT]). On every other deployment the property which controls
 * them, `max_db_connections`, is shown disabled in the connection form: JSON Schema `readOnly`,
 * which the Airbyte form renders as a disabled control, with the pinned value as default and a
 * description saying so. [DynamoDbSourceConfigurationFactory] enforces the same value at runtime
 * and [DynamoDbSharedState] scans every table as one segment, so a configuration created through
 * the API can't switch the feature on either.
 *
 * The property stays in the spec so that a configuration saved on either edition keeps validating
 * on the other.
 */
@Singleton
@Replaces(IdentitySpecificationExtender::class)
class DynamoDbSourceSpecificationExtender(private val featureFlags: Set<FeatureFlag>) :
    SpecificationExtender {

    override fun invoke(specification: ConnectorSpecification): ConnectorSpecification {
        if (FeatureFlag.AIRBYTE_CLOUD_DEPLOYMENT in featureFlags) {
            return specification
        }
        val schema: ObjectNode = specification.connectionSpecification.deepCopy()
        val properties: ObjectNode = schema[PROPERTIES] as ObjectNode
        (properties[MAX_DB_CONNECTIONS] as ObjectNode).apply {
            put(READ_ONLY, true)
            put(ALWAYS_SHOW, true)
            put(DEFAULT, SELF_MANAGED_MAX_DB_CONNECTIONS)
            put(DESCRIPTION, SELF_MANAGED_MAX_DB_CONNECTIONS_DESCRIPTION)
        }
        return specification.withConnectionSpecification(schema)
    }

    companion object {
        const val MAX_DB_CONNECTIONS = "max_db_connections"

        /** Outside Airbyte Cloud, one Scan request at a time: tables and segments in sequence. */
        const val SELF_MANAGED_MAX_DB_CONNECTIONS = 1
        const val SELF_MANAGED_MAX_DB_CONNECTIONS_DESCRIPTION =
            "Not configurable on self-managed Airbyte, where tables are scanned one at a time. " +
                "Airbyte Cloud scans the segments of a large table, and several tables, " +
                "concurrently."

        private const val PROPERTIES = "properties"
        private const val DEFAULT = "default"
        private const val DESCRIPTION = "description"
        private const val READ_ONLY = "readOnly"
        private const val ALWAYS_SHOW = "always_show"
    }
}
