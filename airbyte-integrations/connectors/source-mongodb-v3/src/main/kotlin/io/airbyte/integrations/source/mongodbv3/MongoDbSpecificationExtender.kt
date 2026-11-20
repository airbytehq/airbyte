/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodbv3

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ArrayNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.spec.IdentitySpecificationExtender
import io.airbyte.cdk.spec.SpecificationExtender
import io.airbyte.protocol.models.v0.ConnectorSpecification
import io.micronaut.context.annotation.Replaces
import io.micronaut.context.annotation.Value
import jakarta.inject.Singleton
import java.net.URI

/**
 * Makes the generated `spec` identical to the hand-written `spec.json` of the legacy
 * `source-mongodb-v2` connector:
 * - the legacy spec advertises a `changelogUrl` (same value as `documentationUrl`);
 * - the legacy `oneOf` variants have no `"type": "object"` entry, whereas the CDK's schema
 * generator always emits one;
 * - the legacy `cluster_type` discriminator is `{"type": "string", "const": ..., "order": 1}`,
 * whereas the generator emits `{"type": "string", "enum": [...], "default": ...}` and ignores any
 * annotation placed on an explicitly declared discriminator property.
 *
 * Everything else (property names, titles, ordering, defaults) is expressed with annotations on
 * [MongoDbSourceConfigurationSpecification]. This class can be deleted once byte-for-byte parity
 * with the legacy spec is no longer required.
 */
@Singleton
@Replaces(IdentitySpecificationExtender::class)
class MongoDbSpecificationExtender(
    @Value("\${airbyte.connector.metadata.documentation-url}") private val documentationUrl: String,
) : SpecificationExtender {

    override fun invoke(specification: ConnectorSpecification): ConnectorSpecification {
        specification.changelogUrl = URI.create(documentationUrl)
        renderOneOfVariantsLikeLegacySpec(specification.connectionSpecification)
        return specification
    }

    private fun renderOneOfVariantsLikeLegacySpec(node: JsonNode) {
        when (node) {
            is ObjectNode -> {
                (node.get("oneOf") as? ArrayNode)?.forEach { variant: JsonNode ->
                    if (variant is ObjectNode) {
                        variant.remove("type")
                        (variant.get("properties") as? ObjectNode)
                            ?.get(DatabaseConfigSpecification.CLUSTER_TYPE)
                            ?.let { renderDiscriminatorAsConst(it as ObjectNode) }
                    }
                }
                node.forEach(::renderOneOfVariantsLikeLegacySpec)
            }
            is ArrayNode -> node.forEach(::renderOneOfVariantsLikeLegacySpec)
            else -> Unit
        }
    }

    /** `{"enum": ["X"], "default": "X"}` becomes `{"const": "X", "order": 1}`. */
    private fun renderDiscriminatorAsConst(discriminator: ObjectNode) {
        val values: ArrayNode = discriminator.get("enum") as? ArrayNode ?: return
        if (values.size() != 1) return
        discriminator.remove("enum")
        discriminator.remove("default")
        discriminator.set<JsonNode>("const", values.get(0))
        discriminator.put("order", DISCRIMINATOR_ORDER)
    }

    companion object {
        /** Position of `cluster_type` within each variant, as in the legacy spec. */
        const val DISCRIMINATOR_ORDER = 1
    }
}
