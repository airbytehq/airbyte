/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

import java.util.concurrent.Callable

/**
 * A [Callable] which performs a unit of work in a READ operation.
 *
 * This unit of work is bounded:
 * - by the [key],
 * - by the [input] state which specifies where to begin READing for this [key],
 * - by a soft timeout defined in the connector configuration, when elapsed [signalStop] is called.
 */
interface Worker<K : Key, I : State<K>> : Callable<WorkResult<K, out I, out State<K>>> {

    val input: I

    val key: K
        get() = input.key

    fun signalStop()
}
