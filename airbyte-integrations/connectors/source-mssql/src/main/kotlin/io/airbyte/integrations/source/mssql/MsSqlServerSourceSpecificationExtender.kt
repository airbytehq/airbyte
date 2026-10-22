/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mssql

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ArrayNode
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
 * Airbyte Cloud rejects `Unencrypted` connections unless an SSH tunnel is configured (see
 * [MsSqlServerSourceConfigurationFactory]), so on Airbyte Cloud, where the connector runs with
 * `AIRBYTE_EDITION=CLOUD` ([FeatureFlag.AIRBYTE_CLOUD_DEPLOYMENT]), the Encryption option defaults
 * to `encrypted_trust_server_certificate`. The connection form selects the `oneOf` option whose
 * discriminator equals the property's `default` and falls back to the first option otherwise, so
 * both the `default` and the option order are set. On every other deployment the spec is returned
 * unchanged: no `default`, `Unencrypted` first.
 */
@Singleton
@Replaces(IdentitySpecificationExtender::class)
class MsSqlServerSourceSpecificationExtender(private val featureFlags: Set<FeatureFlag>) :
    SpecificationExtender {

    override fun invoke(specification: ConnectorSpecification): ConnectorSpecification {
        if (FeatureFlag.AIRBYTE_CLOUD_DEPLOYMENT !in featureFlags) {
            return specification
        }
        val schema: ObjectNode = specification.connectionSpecification.deepCopy()
        val sslMode: ObjectNode = (schema[PROPERTIES] as ObjectNode)[SSL_MODE] as ObjectNode
        sslMode.put(DEFAULT, CLOUD_DEFAULT_SSL_MODE)
        val options: ArrayNode = sslMode[ONE_OF] as ArrayNode
        val index: Int =
            (0 until options.size()).first { modeOf(options[it]) == CLOUD_DEFAULT_SSL_MODE }
        val cloudDefault: JsonNode = options.remove(index)
        options.insert(0, cloudDefault)
        return specification.withConnectionSpecification(schema)
    }

    companion object {
        const val SSL_MODE = "ssl_mode"

        /** On Airbyte Cloud, the Encryption option the connection form preselects. */
        const val CLOUD_DEFAULT_SSL_MODE = "encrypted_trust_server_certificate"

        /** The discriminator of a `ssl_mode` option: a single-valued `enum` on `mode`. */
        fun modeOf(option: JsonNode): String? =
            option[PROPERTIES]?.get(MODE)?.get(ENUM)?.firstOrNull()?.asText()

        private const val PROPERTIES = "properties"
        private const val ONE_OF = "oneOf"
        private const val MODE = "mode"
        private const val ENUM = "enum"
        private const val DEFAULT = "default"
    }
}
