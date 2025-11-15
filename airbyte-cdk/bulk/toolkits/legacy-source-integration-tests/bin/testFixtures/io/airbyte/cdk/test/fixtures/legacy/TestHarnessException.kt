/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.test.fixtures.legacy

import io.airbyte.protocol.models.v0.AirbyteMessage

class TestHarnessException : Exception {
    val outputMessages: List<AirbyteMessage>?
    constructor(message: String?) : super(message) {
        outputMessages = null
    }

    constructor(message: String?, cause: Throwable?) : super(message, cause) {
        outputMessages = null
    }

    constructor(
        message: String?,
        cause: Throwable?,
        outputMessages: List<AirbyteMessage>
    ) : super(message, cause) {
        this.outputMessages = outputMessages
    }
}
