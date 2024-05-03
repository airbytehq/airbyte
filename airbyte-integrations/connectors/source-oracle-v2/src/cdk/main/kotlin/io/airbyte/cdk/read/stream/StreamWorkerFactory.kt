/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read.stream

import io.airbyte.cdk.read.StreamKey
import io.airbyte.cdk.read.StreamState
import io.airbyte.cdk.read.Worker
import io.micronaut.context.annotation.DefaultImplementation

@DefaultImplementation(DefaultStreamWorkerFactory::class)
fun interface StreamWorkerFactory {

    fun make(input: StreamState): Worker<StreamKey, out StreamState>?
}
