/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.core

class IntegrationCommandException : Exception {

    constructor(message: String) : super(message)
    constructor(message: String, cause: Throwable) : super(message, cause)
}
