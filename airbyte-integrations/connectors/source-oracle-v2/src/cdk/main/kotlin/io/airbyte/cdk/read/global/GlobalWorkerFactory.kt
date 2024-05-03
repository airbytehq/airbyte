/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read.global

import io.airbyte.cdk.read.GlobalKey
import io.airbyte.cdk.read.GlobalState
import io.airbyte.cdk.read.Worker
import io.micronaut.context.annotation.DefaultImplementation

@DefaultImplementation(DefaultGlobalWorkerFactory::class)
fun interface GlobalWorkerFactory {

    fun make(input: GlobalState): Worker<GlobalKey, out GlobalState>?
}
