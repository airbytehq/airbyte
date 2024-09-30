/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.test.util

import kotlin.reflect.KClass
import kotlinx.coroutines.runBlocking

class CoroutineTestUtils {
    companion object {
        fun <T : Throwable> assertThrows(clazz: KClass<T>, block: suspend () -> Unit) {
            try {
                runBlocking { block() }
            } catch (t: Throwable) {
                if (t::class == clazz) {
                    return
                }
                throw AssertionError("Expected block to throw $clazz, but it threw ${t::class}.")
            }
            throw AssertionError("Expected block to throw $clazz, but it completed successfully.")
        }
    }
}
