/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.spec

import io.airbyte.protocol.models.v0.ConnectorSpecification
import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.micronaut.context.annotation.Replaces
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton

@Singleton
@Replaces(IdentitySpecificationExtender::class)
@Requires(env = ["destination"])
class DestinationSpecificationExtender(private val spec: DestinationSpecification) :
    SpecificationExtender {
    override fun invoke(specification: ConnectorSpecification): ConnectorSpecification {
        return specification
            .withSupportedDestinationSyncModes(spec.supportedSyncModes)
            .withSupportsIncremental(spec.supportsIncremental)
    }
}

interface DestinationSpecification {
    val supportedSyncModes: List<DestinationSyncMode>
    val supportsIncremental: Boolean
}
