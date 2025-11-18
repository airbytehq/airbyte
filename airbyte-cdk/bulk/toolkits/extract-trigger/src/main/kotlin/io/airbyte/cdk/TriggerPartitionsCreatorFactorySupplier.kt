/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk

import io.airbyte.cdk.read.JdbcPartition
import io.airbyte.cdk.read.JdbcSharedState
import io.airbyte.cdk.read.JdbcStreamState
import io.airbyte.cdk.read.MODE_PROPERTY
import io.airbyte.cdk.read.PartitionsCreatorFactorySupplier
import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton

@Singleton
@Primary
@Requires(property = MODE_PROPERTY, value = "concurrent_with_cdc")
class TriggerPartitionsCreatorFactorySupplier<
    A : JdbcSharedState,
    S : JdbcStreamState<A>,
    P : JdbcPartition<S>,
>(private val factory: TriggerPartitionsCreatorFactory<A, S, P>) :
    PartitionsCreatorFactorySupplier<TriggerPartitionsCreatorFactory<A, S, P>> {

    override fun get(): TriggerPartitionsCreatorFactory<A, S, P> {
        return factory
    }
}
