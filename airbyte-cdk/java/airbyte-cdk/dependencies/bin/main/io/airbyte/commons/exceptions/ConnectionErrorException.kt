/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.commons.exceptions

class ConnectionErrorException : RuntimeException {
    var stateCode: String? = null
        private set
    var errorCode: Int = 0
        private set
    var exceptionMessage: String? = null
        private set

    constructor(exceptionMessage: String?) : super(exceptionMessage)

    constructor(stateCode: String?, exception: Throwable) : super(exception) {
        this.stateCode = stateCode
        this.exceptionMessage = exception.message
    }

    constructor(
        stateCode: String?,
        exceptionMessage: String?,
        exception: Throwable?
    ) : super(exception) {
        this.stateCode = stateCode
        this.exceptionMessage = exceptionMessage
    }

    constructor(
        stateCode: String?,
        errorCode: Int,
        exceptionMessage: String?,
        exception: Throwable?
    ) : super(exception) {
        this.stateCode = stateCode
        this.errorCode = errorCode
        this.exceptionMessage = exceptionMessage
    }
}
