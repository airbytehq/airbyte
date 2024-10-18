/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.spec

import io.airbyte.cdk.spec.IdentitySpecificationExtender
import io.airbyte.cdk.spec.SpecificationExtender
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
        return specification
            .withSupportedDestinationSyncModes(spec.supportedSyncModes)
            .withSupportsIncremental(spec.supportsIncremental)
    }
}

interface DestinationSpecificationExtension {
    val supportedSyncModes: List<DestinationSyncMode>
    val supportsIncremental: Boolean
}
