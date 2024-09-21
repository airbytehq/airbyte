/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.extensions

object TestContext {
    const val NO_RUNNING_TEST = "NONE"
    val CURRENT_TEST_NAME: ThreadLocal<String> =
        object : ThreadLocal<String>() {
            override fun initialValue(): String {
                return NO_RUNNING_TEST
            }
        }
}
