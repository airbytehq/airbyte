/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.test.util

fun interface DestinationCleaner {
    /**
     * Search the test destination for old test data and delete it. This should leave recent data
     * (e.g. from the last week) untouched, to avoid causing failures in actively-running tests.
     */
    fun cleanup()
}

object NoopDestinationCleaner : DestinationCleaner {
    override fun cleanup() {}
}
