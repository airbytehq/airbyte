/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodb

import com.mongodb.MongoCommandException
import com.mongodb.MongoConnectionPoolClearedException
import com.mongodb.MongoException
import com.mongodb.MongoServerUnavailableException
import com.mongodb.MongoSocketException
import com.mongodb.MongoTimeoutException
import io.airbyte.cdk.output.ConnectorError
import io.airbyte.cdk.output.EXCEPTION_CLASSIFIER_PREFIX
import io.airbyte.cdk.output.ExceptionClassifier
import io.airbyte.cdk.output.TransientError
import io.micronaut.context.annotation.Value
import jakarta.inject.Singleton

/**
 * Driver failures a sync recovers from by retrying from its last checkpoint: replica-set elections
 * and shutdowns, network and server-selection timeouts, and cursors the server dropped. Runs before
 * the message rules of `application.yml`, which keep the configuration errors. CHECK reports every
 * failure as a configuration error regardless of classification.
 */
@Singleton
class MongoDbExceptionClassifier(
    @Value("\${$EXCEPTION_CLASSIFIER_PREFIX.mongodb.order:5}") override val orderValue: Int,
) : ExceptionClassifier {

    override fun classify(e: Throwable): ConnectorError? {
        val match: Throwable = ExceptionClassifier.unwind(e, ::isTransient) ?: return null
        return TransientError(match.message ?: match.toString())
    }

    private fun isTransient(e: Throwable): Boolean =
        when (e) {
            is MongoSocketException,
            is MongoTimeoutException,
            is MongoConnectionPoolClearedException,
            is MongoServerUnavailableException -> true
            is MongoCommandException ->
                e.hasErrorLabel(RESUMABLE_CHANGE_STREAM_ERROR) ||
                    e.errorCode in TRANSIENT_SERVER_ERROR_CODES
            is MongoException -> e.hasErrorLabel(RESUMABLE_CHANGE_STREAM_ERROR)
            else -> false
        }

    companion object {
        /**
         * The server errors the MongoDB retryable-reads specification retries — HostUnreachable,
         * HostNotFound, NetworkTimeout, ShutdownInProgress, PrimarySteppedDown, ExceededTimeLimit,
         * SocketException, NotWritablePrimary, InterruptedAtShutdown,
         * InterruptedDueToReplStateChange, NotPrimaryNoSecondaryOk, NotPrimaryOrSecondary — plus
         * FailedToSatisfyReadPreference and a cursor the server dropped (CursorNotFound,
         * CursorKilled).
         */
        val TRANSIENT_SERVER_ERROR_CODES: Set<Int> =
            setOf(
                6,
                7,
                89,
                91,
                189,
                262,
                9001,
                10107,
                11600,
                11602,
                13435,
                13436,
                133,
                43,
                237,
                // QueryPlanKilled: an index or collection dropped, or a replica-set state change,
                // under a running query; the retry continues from the checkpoint or reports the
                // dropped collection through catalog validation.
                175,
            )

        /** Label the server puts on change stream errors a resume from the last token recovers. */
        const val RESUMABLE_CHANGE_STREAM_ERROR = "ResumableChangeStreamError"
    }
}
