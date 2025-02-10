/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.test.util

fun interface DestinationCleaner {
    /**
     * Search the test destination for old test data and delete it. This should leave recent data
     * (e.g. from the last week) untouched, to avoid causing failures in actively-running tests.
     *
     * Implementers should generally list all namespaces in the destination, filter for namespace
     * which match [IntegrationTest.randomizedNamespaceRegex], and then use
     * [IntegrationTest.isNamespaceOld] to filter down to namespaces which can be deleted.
     */
    fun cleanup()
}

object NoopDestinationCleaner : DestinationCleaner {
    override fun cleanup() {}
}
