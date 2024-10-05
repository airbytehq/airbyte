/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read.cdc

import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.read.GlobalLockResource
import io.micronaut.context.annotation.Replaces
import jakarta.inject.Singleton
import java.util.concurrent.atomic.AtomicBoolean

@Singleton
@Replaces(GlobalLockResource::class)
/**
 * [GlobalLockResource] implementation for CDC with Debezium.
 *
 * Holds the lock while CDC is ongoing.
 */
class CdcGlobalLockResource(configuration: SourceConfiguration) : GlobalLockResource {

    private val isCdcComplete = AtomicBoolean(configuration.global.not())

    /** Called when CDC is done to release the lock. */
    fun markCdcAsComplete() {
        isCdcComplete.set(true)
    }

    override fun tryAcquire(): GlobalLockResource.AcquiredGlobalLock? =
        if (isCdcComplete.get()) {
            GlobalLockResource.AcquiredGlobalLock {}
        } else {
            null
        }
}
