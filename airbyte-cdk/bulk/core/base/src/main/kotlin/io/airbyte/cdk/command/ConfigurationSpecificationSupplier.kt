/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.command

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.util.Jsons
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Value
import jakarta.inject.Singleton
import java.util.function.Supplier

private val logger = KotlinLogging.logger {}

/**
 * Supplies a valid [T] configuration POJO instance, based on the `airbyte.connector.config`
 * Micronaut property values:
 * - either `airbyte.connector.config.json` if it is set (typically by the CLI)
 * - or the other, nested `airbyte.connector.config.*` properties (typically in unit tests)
 *
 * One may wonder why we need to inject this [Supplier] instead of injecting the POJO directly. The
 * reason is that injecting the POJO only works if the configuration values are set via the nested
 * Micronaut properties (i.e. in unit tests). We could make direct injection work the same way as
 * the [ConfiguredCatalogFactory] or the [InputStateFactory] (via a @Factory) but then we'd lose the
 * ability to set values via the nested properties. This current design caters to both use cases.
 * Furthermore, by deferring the parsing and validation of the configuration, we don't need to worry
 * about exception handling edge cases when implementing the CHECK operation.
 *
 * The object is also validated against its [jsonSchema] JSON schema, derived from [javaClass].
 */
@Singleton
class ConfigurationSpecificationSupplier<T : ConfigurationSpecification>(
    private val micronautPropertiesFallback: T,
    @Value("\${${CONNECTOR_CONFIG_PREFIX}.json}") private val jsonPropertyValue: String? = null,
) : Supplier<T> {
    @Suppress("UNCHECKED_CAST")
    val javaClass: Class<T> = micronautPropertiesFallback::class.java as Class<T>

    val jsonSchema: JsonNode by lazy { ValidatedJsonUtils.generateAirbyteJsonSchema(javaClass) }

    override fun get(): T {
        val jsonMicronautFallback: String by lazy {
            try {
                Jsons.writeValueAsString(micronautPropertiesFallback)
            } catch (e: Exception) {
                throw ConfigErrorException("failed to serialize fallback instance for $javaClass", e)
            }
        }
        val json: String = jsonPropertyValue ?: jsonMicronautFallback
        logger.info{"SGX jsonPropertyValue=$jsonPropertyValue micronautPropertiesFallback=$micronautPropertiesFallback"}
        logger.info{"SGX jsonMicronautFallback=$jsonMicronautFallback"}
        val retVal = ValidatedJsonUtils.parseOne(javaClass, json)
        logger.info{"SGX retVal=$retVal"}
        return retVal
    }
}

/**
 * Connector configuration POJO supertype.
 *
 * This dummy base class is required by Micronaut. Without it, thanks to Java's type erasure, it
 * thinks that the [ConfigurationSpecificationSupplier] requires a constructor argument of type
 * [Any].
 *
 * Strictly speaking, its subclasses are not really POJOs anymore, but who cares.
 */
abstract class ConfigurationSpecification

abstract class DbConfigurationSpecification(): ConfigurationSpecification() {
    abstract var databaseName: String
}
