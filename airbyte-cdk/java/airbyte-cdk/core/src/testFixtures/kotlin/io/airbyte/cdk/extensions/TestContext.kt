/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.extensions

object TestContext {
    val CURRENT_TEST_NAME: ThreadLocal<String?> = ThreadLocal()
}
