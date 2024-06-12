/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.commons.exceptions

/**
 * An exception that indicates that there is something wrong with the user's connector setup. This
 * exception is caught and emits an AirbyteTraceMessage.
 */
class ConfigErrorException : RuntimeException {
    val displayMessage: String

    constructor(displayMessage: String) : super(displayMessage) {
        this.displayMessage = displayMessage
    }

    constructor(displayMessage: String, exception: Throwable?) : super(displayMessage, exception) {
        this.displayMessage = displayMessage
    }
}
