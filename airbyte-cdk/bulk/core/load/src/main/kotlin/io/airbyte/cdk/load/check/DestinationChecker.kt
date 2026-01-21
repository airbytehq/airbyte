/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.check

/**
 * A check operation that is run before the destination is used.
 *
 * * Implementors must provide a [check] method that validates the configuration.
 * * Implementors may provide a [cleanup] method that is run after the check is complete.
 * * [check] should throw an exception if the configuration is invalid.
 * * [cleanup] should not throw exceptions.
 * * Implementors should inject configuration via the constructor.
 */
interface DestinationChecker {
    fun check()
    fun cleanup() {}
}
