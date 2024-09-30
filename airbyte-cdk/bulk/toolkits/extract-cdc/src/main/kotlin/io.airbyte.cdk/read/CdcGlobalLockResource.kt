/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

import io.airbyte.cdk.command.SourceConfiguration
import io.micronaut.context.annotation.Replaces
import jakarta.inject.Singleton
import java.util.concurrent.atomic.AtomicBoolean

@Singleton
@Replaces(GlobalLockResource::class)
class CdcGlobalLockResource(configuration: SourceConfiguration) : GlobalLockResource {

    private val isCdcComplete = AtomicBoolean(configuration.global.not())

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
