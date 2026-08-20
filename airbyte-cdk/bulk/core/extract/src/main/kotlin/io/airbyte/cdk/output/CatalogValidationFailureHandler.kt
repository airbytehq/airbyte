/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.output

import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.asProtocolStreamDescriptor
import io.airbyte.cdk.data.AirbyteSchemaType
import io.airbyte.protocol.models.v0.AirbyteErrorTraceMessage
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.DefaultImplementation
import jakarta.inject.Singleton
import java.util.function.Consumer

/**
 * At the start of the READ operation, the connector configuration, the configured catalog and the
 * input states are validated against each other. For instance, a catalog may have grown stale after
 * a schema change in the source database. All validation failures are passed to this interface. The
 * production implementation will log a message while the test implementation collects them in a
 * buffer for later inspection.
 */
@DefaultImplementation(LoggingCatalogValidationFailureHandler::class)
interface CatalogValidationFailureHandler : Consumer<CatalogValidationFailure>

/** Union type for all validation failures. */
sealed interface CatalogValidationFailure {
    val streamID: StreamIdentifier
    val message: String

    fun asErrorTrace(): AirbyteErrorTraceMessage? =
        AirbyteErrorTraceMessage()
            .withStreamDescriptor(streamID.asProtocolStreamDescriptor())
            .withFailureType(AirbyteErrorTraceMessage.FailureType.CONFIG_ERROR)
            .withMessage(message)
}

data class StreamNotFound(
    override val streamID: StreamIdentifier,
) : CatalogValidationFailure {
    override val message =
        "Stream '$streamID' not found or not accessible in source. To continue syncing this stream, restore access to it, or refresh the source schema to remove it."
}

data class MultipleStreamsFound(
    override val streamID: StreamIdentifier,
) : CatalogValidationFailure {
    override val message =
        "Multiple matching streams found for '$streamID' in source. To continue syncing this stream, refresh the source schema. If this doesn't work, contact Airbyte support."
}

data class StreamHasNoFields(
    override val streamID: StreamIdentifier,
) : CatalogValidationFailure {
    override val message =
        "Stream '$streamID' has no accessible data fields. To continue syncing this stream, grant read access to its fields, or refresh the source schema to remove the stream."
}

data class FieldNotFound(
    override val streamID: StreamIdentifier,
    val fieldName: String,
) : CatalogValidationFailure {
    override val message =
        "Field '$fieldName' not found in stream '$streamID'. To continue syncing this stream, restore access to the field or refresh the source schema to remove it."
}

data class FieldTypeMismatch(
    override val streamID: StreamIdentifier,
    val fieldName: String,
    val expected: AirbyteSchemaType,
    val actual: AirbyteSchemaType,
) : CatalogValidationFailure {
    override val message =
        "Field '$fieldName' in stream '$streamID' has type $actual in source but schema expects $expected. Refresh the source schema to continue syncing this stream."
}

data class InvalidPrimaryKey(
    override val streamID: StreamIdentifier,
    val primaryKey: List<String>,
) : CatalogValidationFailure {
    override val message =
        "Primary key $primaryKey not found in stream '$streamID'. To continue syncing this stream, refresh the source schema and reselect a primary key that exists in the stream."
}

data class InvalidCursor(
    override val streamID: StreamIdentifier,
    val cursor: String,
) : CatalogValidationFailure {
    override val message =
        "Cursor '$cursor' not found in stream '$streamID'. To continue syncing this stream, refresh the source schema and reselect a cursor field that exists in the stream, or use the full refresh sync mode."
}

data class InvalidIncrementalSyncMode(
    override val streamID: StreamIdentifier,
) : CatalogValidationFailure {
    override val message =
        "Stream '$streamID' has no cursor configured for incremental sync. To sync this stream incrementally, configure a cursor field, or switch the stream to the full refresh sync mode."
}

data class ResetStream(
    override val streamID: StreamIdentifier,
) : CatalogValidationFailure {
    override val message = "Resetting stream '$streamID'."
    override fun asErrorTrace(): AirbyteErrorTraceMessage? = null
}

private val log = KotlinLogging.logger {}

@Singleton
private class LoggingCatalogValidationFailureHandler(
    val outputConsumer: OutputConsumer,
) : CatalogValidationFailureHandler {
    override fun accept(f: CatalogValidationFailure) {
        log.warn { f.message }
        f.asErrorTrace()?.let { outputConsumer.accept(it) }
    }
}
