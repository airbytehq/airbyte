/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

import io.airbyte.cdk.command.OpaqueStateValue
import io.micronaut.core.annotation.Order
import jakarta.inject.Singleton

@Singleton
@Order(10)
class CdcPartitionsCreatorFactory(
    val cdcContext: CdcContext,
    val concurrencyResource: ConcurrencyResource,
) : PartitionsCreatorFactory {

    override fun make(stateQuerier: StateQuerier, feed: Feed): PartitionsCreator? {
        val opaqueStateValue: OpaqueStateValue? = stateQuerier.current(feed)
        return when (feed) {
            is Global -> {
                // TODO: remove the following if-block
                if (opaqueStateValue != null) {
                    // For the time being, only do one round
                    return null
                }

                CdcPartitionCreator(concurrencyResource, cdcContext, opaqueStateValue)
            }
            is Stream -> null
        }
    }
}
