package io.airbyte.cdk.core.destination.async

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

    fun getException(): Exception {
        return exceptionAtomicReference.get()
    }
}
