/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.core.command.option

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.commons.json.Jsons
import java.util.Optional

/** Interface that defines a typed connector configuration. */
interface ConnectorConfiguration {
    /*
     * N.B.: This method replaces the {@code getDefaultNamespace} and
     * {@code getRawNamespace} methods used through the source and
     * destination implementations, respectively
     */
    fun getDefaultNamespace(): Optional<String>

    fun toJson(): JsonNode {
        return Jsons.jsonNode(this)
    }
}

/**
 * Default implementation to be used by non-DI-able code. This class may be removed once all
 * connectors/CDK code uses dependency injection.
 */
class DefaultConnectorConfiguration(private val namespace: String?) : ConnectorConfiguration {
    override fun getDefaultNamespace(): Optional<String> {
        return Optional.ofNullable(namespace)
    }
}
