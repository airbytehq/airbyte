/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

import io.micronaut.context.annotation.Replaces
import java.util.concurrent.atomic.AtomicBoolean

@Singleton
@Replaces(GlobalLockResource::class)
class CdcGlobalLockResource : GlobalLockResource {

    private val isCdcComplete = AtomicBoolean()

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
