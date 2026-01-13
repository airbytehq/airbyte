/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.spec

import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.spec.IdentitySpecificationExtender
import io.airbyte.cdk.spec.SpecificationExtender
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.models.v0.ConnectorSpecification
import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.micronaut.context.annotation.Replaces
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton

@Singleton
@Replaces(IdentitySpecificationExtender::class)
@Requires(env = ["destination"])
class DestinationSpecificationExtender(private val spec: DestinationSpecificationExtension) :
    SpecificationExtender {
    override fun invoke(specification: ConnectorSpecification): ConnectorSpecification {
        if (spec.groups.isNotEmpty()) {
            val schema = specification.connectionSpecification as ObjectNode
            schema.set<ObjectNode>(
                "groups",
                Jsons.arrayNode().apply {
                    spec.groups.forEach { group ->
                        add(
                            Jsons.objectNode().apply {
                                put("id", group.id)
                                put("title", group.title)
                            }
                        )
                    }
                }
            )
        }

        return specification
            .withSupportedDestinationSyncModes(spec.supportedSyncModes)
            .withSupportsIncremental(spec.supportsIncremental)
    }
}

interface DestinationSpecificationExtension {
    /**
     * A connector's spec can specify "groups", which the UI will use to put related spec options in
     * the same place. To do this, you should:
     * * add a [Group] to the [groups] list (e.g. `Group(id = "foo", title = "Foo")`
     * * inject `{"group": "foo"}` to the generated JSONSchema for the relevant spec options
     * (`@JsonSchemaInject(json = """{"group": "foo"}""") val theOption: String`
     * * note that this should be the id of the group, not the title.
     */
    data class Group(
        /** A computer-friendly ID for the group */
        val id: String,
        /** A human-readable name for the group */
        val title: String
    )

    val supportedSyncModes: List<DestinationSyncMode>
    val supportsIncremental: Boolean
    val groups: List<Group>
        get() = emptyList()
}
