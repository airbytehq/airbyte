/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.exceptions

/**
 * An exception that indicates a transient error was encountered. This exception is caught and emits
 * an AirbyteTraceMessage.
 */
class TransientErrorException : RuntimeException {

    constructor(displayMessage: String) : super(displayMessage)

    constructor(displayMessage: String, exception: Throwable?) : super(displayMessage, exception)
}
