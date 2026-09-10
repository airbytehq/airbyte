/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.destination.bigquery.copy

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.state.DestinationFailure
import io.airbyte.cdk.load.write.DestinationWriter
import io.airbyte.cdk.load.write.StreamLoader
import io.github.oshai.kotlinlogging.KotlinLogging

/** Publishes run metadata before the task launcher can start any stream loader. */
class BigqueryCopyWriter(
    private val delegate: DestinationWriter,
    private val catalog: DestinationCatalog,
    private val archive: BigqueryS3Copy,
) : DestinationWriter {
    override suspend fun setup() {
        try {
            archive.validate(catalog)
            delegate.setup()
            archive.prepare(catalog)
        } catch (t: Throwable) {
            try {
                archive.close()
            } catch (cleanup: Throwable) {
                t.addSuppressed(cleanup)
            }
            throw t
        }
    }

    override fun createStreamLoader(stream: DestinationStream): StreamLoader =
        delegate.createStreamLoader(stream)

    override suspend fun teardown(destinationFailure: DestinationFailure?) {
        var failure: Exception? = null
        try {
            delegate.teardown(destinationFailure)
        } catch (e: Exception) {
            failure = e
        } finally {
            try {
                archive.close()
            } catch (e: Exception) {
                if (failure == null) failure = e else failure.addSuppressed(e)
            }
        }
        failure?.let {
            if (destinationFailure == null) throw it
            // Legacy FailSyncTask must reach handleTeardownComplete(false). The original failure
            // is already recorded; a second cleanup failure must not leave the launcher waiting.
            KotlinLogging.logger {}
                .error(it) { "Fusion BigQuery failed-sync teardown encountered a cleanup error" }
        }
    }
}
