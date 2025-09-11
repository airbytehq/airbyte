/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.hubspot

import io.airbyte.cdk.load.spec.DestinationSpecificationExtender
import io.airbyte.cdk.spec.SpecificationExtender
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.models.v0.AdvancedAuth
import io.airbyte.protocol.models.v0.AdvancedAuth.AuthFlowType
import io.airbyte.protocol.models.v0.ConnectorSpecification
import io.airbyte.protocol.models.v0.OAuthConfigSpecification
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton

private const val oauthConnectorInputSpecification: String =
    """{
    "consent_url": "https://app.hubspot.com/oauth/authorize?{{ client_id_key }}={{ client_id_value }}&{{ redirect_uri_key }}={{ redirect_uri_value | urlencode }}&{{ scope_key }}={{ scope_value | urlencode }}&optional_scope={{ optional_scope | urlencode }}&{{ state_key }}={{ state_value }}&code_challenge={{ state_value | codechallengeS256 }}",
    "scope": "crm.schemas.appointments.read crm.schemas.carts.read crm.schemas.commercepayments.read crm.schemas.companies.read crm.schemas.contacts.read crm.schemas.courses.read crm.schemas.custom.read crm.schemas.deals.read crm.schemas.invoices.read crm.schemas.listings.read crm.schemas.orders.read crm.schemas.services.read crm.schemas.subscriptions.read",
    "optional_scope": "crm.objects.appointments.write crm.objects.carts.write crm.objects.commercepayments.write crm.objects.companies.write crm.objects.contacts.write crm.objects.courses.write crm.objects.custom.write crm.objects.deals.write crm.objects.invoices.write crm.objects.listings.write crm.objects.orders.write crm.objects.products.write crm.objects.services.write crm.objects.subscriptions.write",
    "access_token_url": "https://api.hubapi.com/oauth/v1/token",
    "extract_output":  ["access_token", "refresh_token", "expires_in"],
    "access_token_headers": {
        "Content-Type": "application/x-www-form-urlencoded"
    },
    "access_token_params": {
      "client_id": "{{ client_id_value }}",
      "client_secret": "{{ client_secret_value }}",
      "code": "{{ auth_code_value }}",
      "grant_type": "authorization_code",
      "redirect_uri": "{{ redirect_uri_value }}"
    }
}"""

private const val completeOauthOutputSpecification: String =
    """{
    "type": "object",
    "additionalProperties": false,
    "properties": {
        "refresh_token": {
            "type": "string",
            "path_in_connector_config": [
                "credentials",
                "refresh_token"
            ],
            "path_in_oauth_response": ["refresh_token"]
        }
    }
}
"""

private const val completeOauthServerInputSpecification: String =
    """{
    "type": "object",
    "additionalProperties": false,
    "properties": {
        "client_id": {
            "type": "string"
        },
        "client_secret": {
            "type": "string"
        }
    }
}"""

private const val completeOauthServerOutputSpecification: String =
    """{
    "type": "object",
    "additionalProperties": false,
    "properties": {
        "client_id": {
            "type": "string",
            "path_in_connector_config": [
                "credentials",
                "client_id"
            ]
        },
        "client_secret": {
            "type": "string",
            "path_in_connector_config": [
                "credentials",
                "client_secret"
            ]
        }
    }
}"""

@Singleton
@Primary
class HubSpotSpecificationExtender(private val decorated: DestinationSpecificationExtender) :
    SpecificationExtender {
    override fun invoke(specification: ConnectorSpecification): ConnectorSpecification {
        val advancedAuth =
            AdvancedAuth()
                .withAuthFlowType(AuthFlowType.OAUTH_2_0)
                .withPredicateKey(listOf("credentials", "type"))
                .withPredicateValue("OAuth")
                .withOauthConfigSpecification(
                    OAuthConfigSpecification()
                        .withOauthConnectorInputSpecification(
                            Jsons.readTree(oauthConnectorInputSpecification)
                        )
                        .withCompleteOauthOutputSpecification(
                            Jsons.readTree(completeOauthOutputSpecification)
                        )
                        .withCompleteOauthServerInputSpecification(
                            Jsons.readTree(completeOauthServerInputSpecification)
                        )
                        .withCompleteOauthServerOutputSpecification(
                            Jsons.readTree(completeOauthServerOutputSpecification)
                        )
                )
        return decorated.invoke(specification).withAdvancedAuth(advancedAuth)
    }
}
