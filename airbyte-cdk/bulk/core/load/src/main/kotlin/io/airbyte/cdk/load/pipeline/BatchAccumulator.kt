/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipeline

import io.airbyte.cdk.load.message.WithStream

/**
 * [BatchAccumulator] is used internally by the CDK to implement
 * [io.airbyte.cdk.load.write.LoadStrategy]s. Connector devs should never need to implement this
 * interface.
 *
 * It is the glue that connects a specific step in a specific pipeline to the generic pipeline on
 * the back end. (For example, in a three-stage pipeline like bulk load, step 1 is to create a part,
 * step 2 is to upload it, and step 3 is to load it from object storage into a table.)
 *
 * - [S] is a state type that will be threaded through accumulator calls.
 * - [K] is a key type associated the input data. (NOTE: Currently, there is no support for
 * key-mapping, so the key is always [io.airbyte.cdk.load.message.StreamKey]). Specifically, state
 * will always be managed per-key.
 * - [T] is the input data type
 * - [U] is the output data type
 *
 * The first time data is seen for a given key, [start] is called (with the partition number). The
 * state returned by [start] will be passed per input to [accept].
 *
 * If [accept] returns a non-null output, that output will be forwarded to the next stage (if
 * applicable) and/or trigger bookkeeping (iff the output type implements
 * [io.airbyte.cdk.load.message.WithBatchState]).
 *
 * If [accept] returns a non-null state, that state will be passed to the next call to [accept]. If
 * [accept] returns a null state, the state will be discarded and a new one will be created on the
 * next input by a new call to [start].
 *
 * When the input stream is exhausted, [finish] will be called with any remaining state iff at least
 * one input was seen for that key. This means that [finish] will not be called on empty keys or on
 * keys where the last call to [accept] yielded a null (finished) state.
 */
interface BatchAccumulator<S, K : WithStream, T, U> {
    suspend fun start(key: K, part: Int): S
    suspend fun accept(input: T, state: S): Pair<S?, U?>
    suspend fun finish(state: S): U
}
