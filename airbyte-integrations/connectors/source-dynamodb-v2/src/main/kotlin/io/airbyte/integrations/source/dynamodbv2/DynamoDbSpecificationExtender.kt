/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.dynamodbv2

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ArrayNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.spec.IdentitySpecificationExtender
import io.airbyte.cdk.spec.SpecificationExtender
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.models.v0.ConnectorSpecification
import io.micronaut.context.annotation.Replaces
import jakarta.inject.Singleton

/**
 * Makes the generated `spec` identical to the hand-written `spec.json` of the legacy
 * `source-dynamodb` connector:
 * - the legacy root schema has `additionalProperties: false`, the generator emits `true`;
 * - the legacy `auth_type` discriminator is `{"type": "string", "const": ..., "order": 0}` and is
 * not listed in the variant's `required`, whereas the generator emits `{"type": "string", "enum":
 * [...], "default": ...}` and requires it.
 *
 * Everything else (property names, titles, ordering, defaults) is expressed with annotations on
 * [DynamoDbSourceConfigurationSpecification]. This class can be deleted once byte-for-byte parity
 * with the legacy spec is no longer required.
 */
@Singleton
@Replaces(IdentitySpecificationExtender::class)
class DynamoDbSpecificationExtender : SpecificationExtender {

    override fun invoke(specification: ConnectorSpecification): ConnectorSpecification {
        val root: ObjectNode = specification.connectionSpecification as ObjectNode
        root.put("additionalProperties", false)
        renderOneOfVariantsLikeLegacySpec(root)
        return specification
    }

    private fun renderOneOfVariantsLikeLegacySpec(node: JsonNode) {
        when (node) {
            is ObjectNode -> {
                (node.get("oneOf") as? ArrayNode)?.forEach { variant: JsonNode ->
                    if (variant is ObjectNode) {
                        renderDiscriminatorAsConst(variant)
                    }
                }
                node.forEach(::renderOneOfVariantsLikeLegacySpec)
            }
            is ArrayNode -> node.forEach(::renderOneOfVariantsLikeLegacySpec)
            else -> Unit
        }
    }

    /**
     * `{"enum": ["X"], "default": "X"}` becomes `{"const": "X", "order": 0}` and the discriminator
     * leaves the variant's `required` list (dropped altogether when it becomes empty).
     */
    private fun renderDiscriminatorAsConst(variant: ObjectNode) {
        val discriminator: ObjectNode =
            (variant.get("properties") as? ObjectNode)?.get(CredentialsSpecification.AUTH_TYPE)
                as? ObjectNode
                ?: return
        val values: ArrayNode = discriminator.get("enum") as? ArrayNode ?: return
        if (values.size() != 1) return
        discriminator.remove("enum")
        discriminator.remove("default")
        discriminator.set<JsonNode>("const", values.get(0))
        discriminator.put("order", DISCRIMINATOR_ORDER)
        (variant.get("required") as? ArrayNode)?.let { required: ArrayNode ->
            val remaining: List<JsonNode> =
                required.filter { it.asText() != CredentialsSpecification.AUTH_TYPE }
            if (remaining.isEmpty()) {
                variant.remove("required")
            } else {
                variant.set<JsonNode>("required", Jsons.arrayNode().addAll(remaining))
            }
        }
    }

    companion object {
        /** Position of `auth_type` within each variant, as in the legacy spec. */
        const val DISCRIMINATOR_ORDER = 0
    }
}
