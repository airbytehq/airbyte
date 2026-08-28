/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.cdk

import io.airbyte.cdk.spec.ConfigurationSupplierSpecificationFactory
import io.airbyte.cdk.spec.SpecificationExtender
import io.airbyte.cdk.spec.SpecificationFactory
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.models.v0.AdvancedAuth
import io.airbyte.protocol.models.v0.AdvancedAuth.AuthFlowType
import io.airbyte.protocol.models.v0.ConnectorSpecification
import io.airbyte.protocol.models.v0.OAuthConfigSpecification
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
        val advancedAuth =
            AdvancedAuth()
                .withAuthFlowType(AuthFlowType.OAUTH_2_0)
                .withPredicateKey(listOf("credentials", "auth_type"))
                .withPredicateValue("OAuth2.0")
                .withOauthConfigSpecification(
                    OAuthConfigSpecification()
                        .withOauthUserInputFromConnectorConfigSpecification(
                            Jsons.readTree(
                                """{"type":"object","properties":{"host":{"type":"string","path_in_connector_config":["host"]}}}"""
                            )
                        )
                        .withCompleteOauthOutputSpecification(
                            Jsons.readTree(
                                """{"type":"object","properties":{"access_token":{"type":"string","path_in_connector_config":["credentials","access_token"]},"refresh_token":{"type":"string","path_in_connector_config":["credentials","refresh_token"]}}}"""
                            )
                        )
                        .withCompleteOauthServerInputSpecification(
                            Jsons.readTree(
                                """{"type":"object","properties":{"client_id":{"type":"string"},"client_secret":{"type":"string"}}}"""
                            )
                        )
                        .withCompleteOauthServerOutputSpecification(
                            Jsons.readTree(
                                """{"type":"object","properties":{"client_id":{"type":"string","path_in_connector_config":["credentials","client_id"]},"client_secret":{"type":"string","path_in_connector_config":["credentials","client_secret"]}}}"""
                            )
                        )
                )
        return extendSpecification(
            ConnectorSpecification()
                .withConnectionSpecification(configJsonObjectSupplier.jsonSchema)
        ).withAdvancedAuth(advancedAuth)
    }
}
