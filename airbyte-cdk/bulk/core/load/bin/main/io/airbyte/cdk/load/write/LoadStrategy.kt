/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.write

interface LoadStrategy {
    val inputPartitions: Int
        get() = 1
}
