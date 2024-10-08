/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.test.util

import kotlin.reflect.KClass

class CoroutineTestUtils {
    companion object {
        suspend fun <T : Throwable> assertThrows(clazz: KClass<T>, block: suspend () -> Unit) {
            try {
                block()
            } catch (t: Throwable) {
                if (t::class == clazz) {
                    return
                }
                throw AssertionError("Expected block to throw $clazz, but it threw ${t::class}.")
            }
            throw AssertionError("Expected block to throw $clazz, but it completed successfully.")
        }

        suspend fun assertDoesNotThrow(block: suspend () -> Unit) {
            try {
                block()
            } catch (t: Throwable) {
                throw AssertionError("Expected block to not throw, but it threw ${t::class}.")
            }
        }
    }
}
