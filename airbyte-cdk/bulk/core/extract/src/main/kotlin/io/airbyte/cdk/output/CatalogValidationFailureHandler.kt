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
    override val message = "Stream '$streamID' not found or not accessible in source."
}

data class MultipleStreamsFound(
    override val streamID: StreamIdentifier,
) : CatalogValidationFailure {
    override val message = "Multiple matching streams found for '$streamID' in source."
}

data class StreamHasNoFields(
    override val streamID: StreamIdentifier,
) : CatalogValidationFailure {
    override val message = "Stream '$streamID' has no accessible data fields."
}

data class FieldNotFound(
    override val streamID: StreamIdentifier,
    val fieldName: String,
) : CatalogValidationFailure {
    override val message = "Field '$fieldName' not found in stream '$streamID'."
}

data class FieldTypeMismatch(
    override val streamID: StreamIdentifier,
    val fieldName: String,
    val expected: AirbyteSchemaType,
    val actual: AirbyteSchemaType,
) : CatalogValidationFailure {
    override val message =
        "Field '$fieldName' in stream '$streamID' has type $actual in source but catalog expects $expected."
}

data class InvalidPrimaryKey(
    override val streamID: StreamIdentifier,
    val primaryKey: List<String>,
) : CatalogValidationFailure {
    override val message = "Primary key $primaryKey not found in stream '$streamID'."
}

data class InvalidCursor(
    override val streamID: StreamIdentifier,
    val cursor: String,
) : CatalogValidationFailure {
    override val message = "Cursor '$cursor' not found in stream '$streamID'."
}

data class InvalidIncrementalSyncMode(
    override val streamID: StreamIdentifier,
) : CatalogValidationFailure {
    override val message =
        "Stream '$streamID' has no cursor configured for incremental sync; falling back to full refresh."
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
