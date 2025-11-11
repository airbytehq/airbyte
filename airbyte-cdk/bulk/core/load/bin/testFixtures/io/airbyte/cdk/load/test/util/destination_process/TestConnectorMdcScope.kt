/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.test.util.destination_process

import org.slf4j.MDC

// As the name suggests, this is _heavily_ based on the old CDK's MdcScope.
// Like everything else related to running connectors/etc, it's also
// heavily simplified.
class TestConnectorMdcScope(logPrefix: String) : AutoCloseable {
    private val originalMdc = MDC.getCopyOfContextMap()

    init {
        MDC.put(LOG_PREFIX_KEY, logPrefix)
        // I'm sure there's some historical context here :shrug:
        // This toggles something in our log4j2-test.xml.
        // Without this key, the logger won't respect the log_source key.
        MDC.put("simple", "true")
    }

    override fun close() {
        MDC.setContextMap(originalMdc)
    }

    companion object {
        // This name is a historical artifact.
        // The previous CDK tests sometimes wanted to run different types of containers
        // (e.g. destination + normalization), so we would set a prefix like
        // "destination > " (with fancy coloring).
        // Nowadays it's easier to just set the test name + container ID as the prefix.
        const val LOG_PREFIX_KEY: String = "log_source"
    }
}
