/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.slackv2

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.spec.IdentitySpecificationExtender
import io.airbyte.cdk.spec.SpecificationExtender
import io.airbyte.cdk.util.Jsons
import io.airbyte.cdk.util.ResourceUtils
import io.airbyte.protocol.models.v0.AdvancedAuth
import io.airbyte.protocol.models.v0.ConnectorSpecification
import io.micronaut.context.annotation.Replaces
import jakarta.inject.Singleton

/**
 * Brings the generated spec to the shape of the legacy `source-slack` spec:
 * - the `advanced_auth` block (Slack OAuth 2.0 flow: consent URL, token URL, scopes, output paths)
 * is copied from `advanced-auth.json`, so that Airbyte's "Sign in via Slack" button keeps working;
 * - the `option_title` discriminator of each `credentials` variant is rendered as a `const`, the
 * way the legacy spec and the OAuth `predicate_value` expect it, instead of the generator's `enum`
 * + `default`;
 * - the variants of the `credentials` oneOf drop the generated `additionalProperties`, and the
 * `oneOf` gets `type: object` at the property level only, like the legacy spec.
 */
@Singleton
@Replaces(IdentitySpecificationExtender::class)
class SlackSpecificationExtender : SpecificationExtender {

    override fun invoke(specification: ConnectorSpecification): ConnectorSpecification {
        val root: ObjectNode = specification.connectionSpecification as ObjectNode
        val credentials: ObjectNode? = root.get("properties")?.get("credentials") as? ObjectNode
        credentials?.get("oneOf")?.forEach { variant: JsonNode ->
            variant as ObjectNode
            variant.remove("additionalProperties")
            val optionTitle: ObjectNode? =
                variant.get("properties")?.get(CredentialsSpecification.OPTION_TITLE) as? ObjectNode
            if (optionTitle != null) {
                val value: JsonNode? = optionTitle.get("enum")?.firstOrNull()
                optionTitle.remove("enum")
                optionTitle.remove("default")
                if (value != null) {
                    optionTitle.set<JsonNode>("const", value)
                }
            }
        }
        specification.advancedAuth = Jsons.readValue(ADVANCED_AUTH, AdvancedAuth::class.java)
        specification.supportsNormalization = false
        specification.supportsDBT = false
        return specification
    }

    companion object {
        /** The legacy connector's `advanced_auth`, verbatim. */
        val ADVANCED_AUTH: String by lazy { ResourceUtils.readResource("advanced-auth.json") }
    }
}
