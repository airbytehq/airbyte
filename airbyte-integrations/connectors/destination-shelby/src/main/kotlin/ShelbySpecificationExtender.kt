package io.airbyte.integrations.destination.shelby

import io.airbyte.cdk.load.spec.DestinationSpecificationExtender
import io.airbyte.cdk.spec.SpecificationExtender
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.models.v0.AdvancedAuth
import io.airbyte.protocol.models.v0.AdvancedAuth.AuthFlowType
import io.airbyte.protocol.models.v0.ConnectorSpecification
import io.airbyte.protocol.models.v0.OAuthConfigSpecification
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton

private const val oauthUserInputFromConnectorConfigSpecification: String = """{
  "type": "object",
  "additionalProperties": false,
  "properties": {
    "is_sandbox": {
      "type": "boolean",
      "path_in_connector_config": [
        "is_sandbox"
      ]
    }
  }
}
"""

private const val completeOauthOutputSpecification: String = """{
  "type": "object",
  "additionalProperties": false,
  "properties": {
    "refresh_token": {
      "type": "string",
      "path_in_connector_config": [
        "refresh_token"
      ]
    }
  }
}
"""

private const val completeOauthServerInputSpecification: String = """{
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

private const val completeOauthServerOutputSpecification: String = """{
  "type": "object",
  "additionalProperties": false,
  "properties": {
    "client_id": {
      "type": "string",
      "path_in_connector_config": [
        "client_id"
      ]
    },
    "client_secret": {
      "type": "string",
      "path_in_connector_config": [
        "client_secret"
      ]
    }
  }
}"""

@Singleton
@Primary
class ShelbySpecificationExtender(private val decorated: DestinationSpecificationExtender) : SpecificationExtender {
    override fun invoke(specification: ConnectorSpecification): ConnectorSpecification {
        val advancedAuth = AdvancedAuth()
            .withAuthFlowType(AuthFlowType.OAUTH_2_0)
            .withPredicateKey(listOf("auth_type"))
            .withPredicateValue("Client")
            .withOauthConfigSpecification(
                OAuthConfigSpecification()
                    .withOauthUserInputFromConnectorConfigSpecification(Jsons.readTree(oauthUserInputFromConnectorConfigSpecification))
                    .withCompleteOauthOutputSpecification(Jsons.readTree(completeOauthOutputSpecification))
                    .withCompleteOauthServerInputSpecification(Jsons.readTree(completeOauthServerInputSpecification))
                    .withCompleteOauthServerOutputSpecification(Jsons.readTree(completeOauthServerOutputSpecification))
            )
        return decorated.invoke(specification).withAdvancedAuth(advancedAuth)
    }

}
