/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.output

import io.airbyte.cdk.data.AirbyteType
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
    val streamName: String
    val streamNamespace: String?
}

data class StreamNotFound(
    override val streamName: String,
    override val streamNamespace: String?,
) : CatalogValidationFailure

data class MultipleStreamsFound(
    override val streamName: String,
    override val streamNamespace: String?,
) : CatalogValidationFailure

data class StreamHasNoFields(
    override val streamName: String,
    override val streamNamespace: String?,
) : CatalogValidationFailure

data class FieldNotFound(
    override val streamName: String,
    override val streamNamespace: String?,
    val fieldName: String,
) : CatalogValidationFailure

data class FieldTypeMismatch(
    override val streamName: String,
    override val streamNamespace: String?,
    val fieldName: String,
    val expected: AirbyteType,
    val actual: AirbyteType,
) : CatalogValidationFailure

data class InvalidPrimaryKey(
    override val streamName: String,
    override val streamNamespace: String?,
    val primaryKey: List<String>,
) : CatalogValidationFailure

data class InvalidCursor(
    override val streamName: String,
    override val streamNamespace: String?,
    val cursor: String,
) : CatalogValidationFailure

data class InvalidIncrementalSyncMode(
    override val streamName: String,
    override val streamNamespace: String?,
) : CatalogValidationFailure

data class ResetStream(
    override val streamName: String,
    override val streamNamespace: String?,
) : CatalogValidationFailure

private val log = KotlinLogging.logger {}

@Singleton
private class LoggingCatalogValidationFailureHandler : CatalogValidationFailureHandler {
    override fun accept(f: CatalogValidationFailure) {
        when (f) {
            is FieldNotFound ->
                log.warn { "In stream ${f.prettyName()}: field '${f.fieldName}' not found." }
            is FieldTypeMismatch ->
                log.warn {
                    "In stream ${f.prettyName()}: " +
                        "field '${f.fieldName}' is ${f.actual} but catalog expects ${f.expected}."
                }
            is StreamHasNoFields -> log.warn { "In stream ${f.prettyName()}: no data fields found" }
            is InvalidCursor ->
                log.warn { "In stream ${f.prettyName()}: invalid cursor '${f.cursor}'." }
            is InvalidPrimaryKey ->
                log.warn { "In stream ${f.prettyName()}: invalid primary key '${f.primaryKey}'." }
            is InvalidIncrementalSyncMode ->
                log.warn { "In stream ${f.prettyName()}: incremental sync not possible." }
            is MultipleStreamsFound ->
                log.warn { "Multiple matching streams found for ${f.prettyName()}." }
            is ResetStream -> log.warn { "Resetting stream ${f.prettyName()}." }
            is StreamNotFound -> log.warn { "No matching stream found for name ${f.prettyName()}." }
        }
    }

    private fun CatalogValidationFailure.prettyName(): String =
        if (streamNamespace == null) {
            "'$streamName' in unspecified namespace"
        } else {
            "'$streamName' in namespace '$streamNamespace'"
        }
}
