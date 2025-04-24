/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.test.fixtures.legacy

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.protocol.models.v0.ConnectorSpecification
import java.io.*
import java.util.*

object SshHelpers {
    @get:Throws(IOException::class)
    @JvmStatic
    val specAndInjectSsh: ConnectorSpecification
        get() = getSpecAndInjectSsh(Optional.empty())

    @Throws(IOException::class)
    @JvmStatic
    fun getSpecAndInjectSsh(group: Optional<String>): ConnectorSpecification {
        val originalSpec =
            Jsons.deserialize(
                MoreResources.readResource("spec.json"),
                ConnectorSpecification::class.java
            )
        return injectSshIntoSpec(originalSpec, group)
    }

    @JvmOverloads
    @Throws(IOException::class)
    @JvmStatic
    fun injectSshIntoSpec(
        connectorSpecification: ConnectorSpecification,
        group: Optional<String> = Optional.empty()
    ): ConnectorSpecification {
        val originalSpec = Jsons.clone(connectorSpecification)
        val propNode = originalSpec.connectionSpecification["properties"] as ObjectNode
        val tunnelMethod =
            Jsons.deserialize(MoreResources.readResource("ssh-tunnel-spec.json")) as ObjectNode
        if (group.isPresent) {
            tunnelMethod.put("group", group.get())
        }
        propNode.set<JsonNode>("tunnel_method", tunnelMethod)
        return originalSpec
    }
}
