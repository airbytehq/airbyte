/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.cdk

import io.airbyte.cdk.spec.ConfigurationSupplierSpecificationFactory
import io.airbyte.cdk.spec.SpecificationExtender
import io.airbyte.cdk.spec.SpecificationFactory
import io.airbyte.protocol.models.v0.ConnectorSpecification
import io.micronaut.context.annotation.Replaces
import jakarta.inject.Singleton

/**
 * This is a custom override of the [ConfigurationSupplierSpecificationFactory] from the CDK in
 * order to leverage the custom [SnowflakeMigratingConfigurationSpecificationSupplier]
 * implementation.
 */
@Singleton
@Replaces(ConfigurationSupplierSpecificationFactory::class)
class SnowflakeConfigurationSupplierSpecificationFactory(
    val configJsonObjectSupplier: SnowflakeMigratingConfigurationSpecificationSupplier,
    val extendSpecification: SpecificationExtender,
) : SpecificationFactory {
    override fun create(): ConnectorSpecification {
        return extendSpecification(
            ConnectorSpecification()
                .withConnectionSpecification(configJsonObjectSupplier.jsonSchema)
        )
    }
}
