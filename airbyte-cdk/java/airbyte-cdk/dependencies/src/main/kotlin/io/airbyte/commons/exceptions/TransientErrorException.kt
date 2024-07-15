/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.exceptions

/**
 * An exception that indicates a transient error was encountered. This exception is caught and emits
 * an AirbyteTraceMessage.
 */
class TransientErrorException : RuntimeException {
    val internalMessage: String?

    constructor(displayMessage: String, internalMessage: String? = null) : super(displayMessage) {
        this.internalMessage = internalMessage
    }

    constructor(
        displayMessage: String,
        exception: Throwable?,
        internalMessage: String? = null,
    ) : super(displayMessage, exception) {
        this.internalMessage = internalMessage
    }
}
