/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.exceptions

/**
 * An exception that indicates that there is something wrong with the user's connector setup. This
 * exception is caught and emits an AirbyteTraceMessage.
 */
class ConfigErrorException(
    displayMessage: String,
    exception: Throwable? = null,
) : RuntimeException(displayMessage, exception) {
    companion object {
        @JvmStatic
        fun unwind(e: Throwable?): ConfigErrorException? =
            when (e) {
                null -> null
                is ConfigErrorException -> e
                else -> unwind(e.cause)
            }
    }
}
