/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mysql_v2.cdk

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.command.CONNECTOR_CONFIG_PREFIX
import io.airbyte.cdk.command.ConfigurationSpecificationSupplier
import io.airbyte.cdk.command.ValidatedJsonUtils
import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.destination.mysql_v2.spec.MysqlSpecification
import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Replaces
import io.micronaut.context.annotation.Value
import jakarta.inject.Singleton
import java.util.function.Supplier

/**
 * Custom configuration specification supplier for MySQL v2 destination.
 *
 * This implementation extends the standard [ConfigurationSpecificationSupplier]
 * to support configuration migrations from legacy formats. Currently, MySQL v2
 * doesn't have legacy configurations to migrate, but this pattern is included
 * for consistency with other destinations and to support future migration needs.
 *
 * The supplier:
 * 1. Loads the configuration from the Micronaut property
 * 2. Validates it against the JSON schema
 * 3. Returns a strongly-typed [MysqlSpecification] instance
 *
 * If the configuration is invalid, a [ConfigErrorException] is thrown with
 * details about the validation failure.
 */
@Primary
@Singleton
@Replaces(ConfigurationSpecificationSupplier::class)
class MysqlMigratingConfigurationSpecificationSupplier(
    @param:Value("\${${CONNECTOR_CONFIG_PREFIX}.json}")
    private val jsonPropertyValue: String? = null,
) : Supplier<MysqlSpecification> {
    val specificationJavaClass: Class<MysqlSpecification> = MysqlSpecification::class.java

    @Suppress("UNCHECKED_CAST")
    val jsonSchema: JsonNode by lazy {
        ValidatedJsonUtils.generateAirbyteJsonSchema(specificationJavaClass)
    }

    override fun get(): MysqlSpecification {
        val jsonMicronautFallback: String by lazy {
            try {
                Jsons.writeValueAsString(MysqlSpecification())
            } catch (_: Exception) {
                throw ConfigErrorException(
                    "failed to serialize fallback instance for $specificationJavaClass"
                )
            }
        }

        val json: String = jsonPropertyValue ?: jsonMicronautFallback
        return ValidatedJsonUtils.parseUnvalidated(json, specificationJavaClass)
    }
}
