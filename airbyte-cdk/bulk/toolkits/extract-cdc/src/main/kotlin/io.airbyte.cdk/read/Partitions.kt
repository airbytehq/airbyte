/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

import java.util.concurrent.atomic.AtomicBoolean
import kotlinx.coroutines.sync.Semaphore

interface cdcAware {
    fun cdcResourceAcquire(): Boolean =
        cdcRan.get() || this is cdcResourceTaker && cdcResource.tryAcquire()

    companion object {
        val cdcResource: Semaphore = Semaphore(1)
        var cdcRan: AtomicBoolean = AtomicBoolean(false)
    }
}

interface cdcResourceTaker {}
