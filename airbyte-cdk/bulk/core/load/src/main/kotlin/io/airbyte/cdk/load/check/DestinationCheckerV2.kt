/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.check

import io.airbyte.cdk.load.command.DestinationStream

/**
 * A check operation that is run before the destination is used.
 *
 * * Implementors must provide a [check] method that validates the configuration.
 * * Implementors may provide a [cleanup] method that is run after the check is complete.
 * * [check] should throw an exception if the configuration is invalid.
 * * [cleanup] should not throw exceptions.
 * * Implementors should not perform any side effects in the constructor.
 * * Implementors should not throw exceptions in the constructor.
 * * Implementors should not inject configuration; only use the config passed in [check].
 */
interface DestinationCheckerV2 {
    fun check()
    fun cleanup() {}
}

// TODO the cleaner maybe should also be looking for old test tables, a la DestinationCleaner??
fun interface CheckCleanerV2 {
    fun cleanup(stream: DestinationStream)
}
