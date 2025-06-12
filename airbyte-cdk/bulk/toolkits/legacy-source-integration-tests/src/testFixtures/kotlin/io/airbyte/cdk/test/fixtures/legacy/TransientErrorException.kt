/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.test.fixtures.legacy

/**
 * An exception that indicates a transient error was encountered. This exception is caught and emits
 * an AirbyteTraceMessage.
 */
class TransientErrorException : RuntimeException {
    val internalMessage: String

    @JvmOverloads
    constructor(displayMessage: String, internalMessage: String = "") : super(displayMessage) {
        this.internalMessage = internalMessage
    }

    @JvmOverloads
    constructor(
        displayMessage: String,
        exception: Throwable?,
        internalMessage: String = "",
    ) : super(displayMessage, exception) {
        this.internalMessage = internalMessage
    }
}
