/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.async.state

import io.airbyte.cdk.core.context.env.ConnectorConfigurationPropertySource
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicReference

@Singleton
@Requires(
    property = ConnectorConfigurationPropertySource.CONNECTOR_OPERATION,
    value = "write",
)
@Requires(env = ["destination"])
class FlushFailure {
    private val isFailed = AtomicBoolean(false)

    private val exceptionAtomicReference = AtomicReference<Exception>()

    fun propagateException(e: Exception) {
        isFailed.set(true)
        exceptionAtomicReference.set(e)
    }

    fun isFailed(): Boolean {
        return isFailed.get()
    }

    val exception: Exception
        get() = exceptionAtomicReference.get()
}
