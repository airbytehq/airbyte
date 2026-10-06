/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.test.util

import java.util.concurrent.atomic.AtomicInteger

fun AtomicInteger.rotate(limit: Int) =
    this.getAndUpdate {
        if (it + 1 == limit) {
            0
        } else {
            it + 1
        }
    }
