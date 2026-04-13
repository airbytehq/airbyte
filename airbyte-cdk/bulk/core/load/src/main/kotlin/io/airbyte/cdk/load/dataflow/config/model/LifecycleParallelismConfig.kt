/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.config.model

data class LifecycleParallelismConfig(
    val streamInitParallelism: Int = 10,
    val streamFinalizeParallelism: Int = 10,
    val finalFlushParallelism: Int = 10,
)
