/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read.cdc

import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.read.*
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
                CdcPartitionsCreator(concurrencyResource, cdcContext, opaqueStateValue)
            }
            is Stream -> null
        }
    }
}
