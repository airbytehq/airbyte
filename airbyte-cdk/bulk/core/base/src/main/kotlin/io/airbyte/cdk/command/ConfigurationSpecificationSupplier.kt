/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.command

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.util.Jsons
import io.micronaut.context.annotation.Requires
import io.micronaut.context.annotation.Value
import jakarta.inject.Singleton
import java.util.function.Supplier

interface ConfigurationSpecificationSupplier<T : ConfigurationSpecification> : Supplier<T> {
    val jsonSchema: JsonNode
}

fun <T : ConfigurationSpecification> buildJsonSchema(klazz: Class<T>): JsonNode {
    return ValidatedJsonUtils.generateAirbyteJsonSchema(klazz)
}

@Singleton
@Requires(property = "$CONNECTOR_CONFIG_PREFIX.json")
class JsonConfigurationSpecificationProvider<T : ConfigurationSpecification>(
    private val micronautPropertiesFallback: T,
    @Value("\${${CONNECTOR_CONFIG_PREFIX}.json}") private val jsonPropertyValue: String,
) : ConfigurationSpecificationSupplier<T> {

    override val jsonSchema: JsonNode by lazy {
        buildJsonSchema(micronautPropertiesFallback.javaClass)
    }

    override fun get(): T {
        return ValidatedJsonUtils.parseUnvalidated(
            jsonPropertyValue,
            micronautPropertiesFallback.javaClass
        )
    }
}

/**
 * This class is used during testing. The goal is to be able to create configuration without
 * actually providing a JSON. In order to do so, you need to:
 * * Add `@ConfigurationProperties(CONNECTOR_CONFIG_PREFIX)` annotation to your spec class
 * * Add `@Property(name = "airbyte.connector.config.<key>", value = <value>)` annotation to your
 * test or test class
 *
 * Note that during tests, you could still use `@Property(name = "$CONNECTOR_CONFIG_PREFIX.json",
 * value = CONFIG_JSON)` in order to use the normal production flow with
 * JsonConfigurationSpecificationProvider.
 */
@Singleton
@Requires(missingProperty = "$CONNECTOR_CONFIG_PREFIX.json")
class MicronautTestConfigurationSpecificationProvider<T : ConfigurationSpecification>(
    private val micronautPropertiesFallback: T,
) : ConfigurationSpecificationSupplier<T> {

    override val jsonSchema: JsonNode by lazy {
        ValidatedJsonUtils.generateAirbyteJsonSchema(micronautPropertiesFallback.javaClass)
    }

    override fun get(): T {
        val jsonMicronautSpec: String by lazy {
            try {
                Jsons.writeValueAsString(micronautPropertiesFallback)
            } catch (_: Exception) {
                throw ConfigErrorException("failed to serialize fallback instance for $javaClass")
            }
        }
        return ValidatedJsonUtils.parseUnvalidated(
            jsonMicronautSpec,
            micronautPropertiesFallback.javaClass
        )
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
