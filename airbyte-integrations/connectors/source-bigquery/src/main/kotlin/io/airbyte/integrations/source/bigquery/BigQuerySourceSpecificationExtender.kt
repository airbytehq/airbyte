/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.bigquery

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
 * The Storage Read API read path and concurrent reads are only offered on Airbyte Cloud, where the
 * connector runs with `AIRBYTE_EDITION=CLOUD` ([FeatureFlag.AIRBYTE_CLOUD_DEPLOYMENT]). On every
 * other deployment the two properties which control them, `max_db_connections` and
 * `use_storage_read_api`, are shown disabled in the connection form: JSON Schema `readOnly`, which
 * the Airbyte form renders as a disabled control, with the pinned values as defaults and a
 * description saying so. [BigQuerySourceConfigurationFactory] enforces the same values at runtime,
 * so a configuration created through the API can't switch the features on either.
 *
 * The properties stay in the spec so that a configuration saved on either edition keeps validating
 * on the other.
 */
@Singleton
@Replaces(IdentitySpecificationExtender::class)
class BigQuerySourceSpecificationExtender(private val featureFlags: Set<FeatureFlag>) :
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
        (properties[USE_STORAGE_READ_API] as ObjectNode).apply {
            put(READ_ONLY, true)
            put(ALWAYS_SHOW, true)
            put(DEFAULT, SELF_MANAGED_USE_STORAGE_READ_API)
            put(DESCRIPTION, SELF_MANAGED_USE_STORAGE_READ_API_DESCRIPTION)
        }
        return specification.withConnectionSpecification(schema)
    }

    companion object {
        const val MAX_DB_CONNECTIONS = "max_db_connections"
        const val USE_STORAGE_READ_API = "use_storage_read_api"

        /** Outside Airbyte Cloud, streams are read one at a time. */
        const val SELF_MANAGED_MAX_DB_CONNECTIONS = 1
        const val SELF_MANAGED_MAX_DB_CONNECTIONS_DESCRIPTION =
            "Not configurable on self-managed Airbyte, where streams are read one at a time. " +
                "Airbyte Cloud reads several streams concurrently."
        /** Outside Airbyte Cloud, every table is read through the query API. */
        const val SELF_MANAGED_USE_STORAGE_READ_API = false
        const val SELF_MANAGED_USE_STORAGE_READ_API_DESCRIPTION =
            "Not available on self-managed Airbyte, where tables are read through the standard " +
                "query API. Airbyte Cloud reads tables through the BigQuery Storage Read API for " +
                "high throughput."

        private const val PROPERTIES = "properties"
        private const val DEFAULT = "default"
        private const val DESCRIPTION = "description"
        private const val READ_ONLY = "readOnly"
        private const val ALWAYS_SHOW = "always_show"
    }
}
