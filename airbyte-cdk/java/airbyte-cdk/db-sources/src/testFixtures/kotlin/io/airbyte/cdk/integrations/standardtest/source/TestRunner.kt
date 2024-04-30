/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.standardtest.source

import java.io.PrintWriter
import java.nio.charset.StandardCharsets
import org.junit.platform.engine.discovery.DiscoverySelectors
import org.junit.platform.launcher.core.LauncherDiscoveryRequestBuilder
import org.junit.platform.launcher.core.LauncherFactory
import org.junit.platform.launcher.listeners.SummaryGeneratingListener

object TestRunner {
    fun runTestClass(testClass: Class<*>?) {
        val request =
            LauncherDiscoveryRequestBuilder.request()
                .selectors(DiscoverySelectors.selectClass(testClass))
                .build()

        val plan = LauncherFactory.create().discover(request)
        val launcher = LauncherFactory.create()

        // Register a listener of your choice
        val listener = SummaryGeneratingListener()

        launcher.execute(plan, listener)

        listener.summary.printFailuresTo(PrintWriter(System.out, false, StandardCharsets.UTF_8))
        listener.summary.printTo(PrintWriter(System.out, false, StandardCharsets.UTF_8))

        if (listener.summary.testsFailedCount > 0) {
            println(
                "There are failing tests. See https://docs.airbyte.io/contributing-to-airbyte/building-new-connector/standard-source-tests " +
                    "for more information about the standard source test suite."
            )
            System.exit(1)
        }
    }
}
