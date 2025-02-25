/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipeline

import io.airbyte.cdk.load.message.WithStream

/**
 * [BatchAccumulator] is used internally by the CDK to implement RecordLoaders. Connector devs
 * should never need to implement this interface.
 */
interface BatchAccumulator<S, K : WithStream, T, U> {
    fun start(key: K, part: Int): S
    fun accept(record: T, state: S): Pair<S, U?>
    fun finish(state: S): U
}
