/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.test.fixtures.legacy

import java.util.concurrent.Callable

@FunctionalInterface
fun interface VoidCallable : Callable<Void> {
    @Throws(Exception::class)
    override fun call(): Void? {
        voidCall()
        return null
    }

    @Throws(Exception::class) fun voidCall()

    companion object {
        @JvmField val NOOP: VoidCallable = VoidCallable {}
    }
}
