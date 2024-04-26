/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.consumers

import io.airbyte.cdk.discover.ColumnType
import io.airbyte.cdk.discover.TableName
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

data class TableNotFound(override val streamName: String, override val streamNamespace: String?) :
    CatalogValidationFailure

data class MultipleTablesFound(
    override val streamName: String,
    override val streamNamespace: String?,
    val matches: List<TableName>
) : CatalogValidationFailure

data class ColumnNotFound(
    override val streamName: String,
    override val streamNamespace: String?,
    val columnName: String
) : CatalogValidationFailure

data class ColumnTypeMismatch(
    override val streamName: String,
    override val streamNamespace: String?,
    val columnName: String,
    val expected: ColumnType,
    val actual: ColumnType
) : CatalogValidationFailure

data class InvalidPrimaryKey(
    override val streamName: String,
    override val streamNamespace: String?,
    val primaryKey: List<String>
) : CatalogValidationFailure

data class InvalidCursor(
    override val streamName: String,
    override val streamNamespace: String?,
    val cursor: String
) : CatalogValidationFailure

data class ResetStream(override val streamName: String, override val streamNamespace: String?) :
    CatalogValidationFailure

private val log = KotlinLogging.logger {}

@Singleton
private class LoggingCatalogValidationFailureHandler : CatalogValidationFailureHandler {

    override fun accept(f: CatalogValidationFailure) {
        when (f) {
            is ColumnNotFound ->
                log.warn { "In table ${f.prettyName()}: column '${f.columnName}' not found." }
            is ColumnTypeMismatch ->
                log.warn {
                    "In table ${f.prettyName()}: " +
                        "column '${f.columnName}' is ${f.actual} but catalog expects ${f.expected}."
                }
            is InvalidCursor ->
                log.warn { "In table ${f.prettyName()}: invalid cursor '${f.cursor}'." }
            is InvalidPrimaryKey ->
                log.warn { "In table ${f.prettyName()}: invalid primary key '${f.primaryKey}'." }
            is MultipleTablesFound ->
                log.warn { "Multiple matching tables found for ${f.prettyName()}: ${f.matches}." }
            is ResetStream ->
                log.warn { "Resetting stream '${f.streamName}' in  ${f.prettyName()}." }
            is TableNotFound -> log.warn { "No matching table found for name ${f.prettyName()}." }
        }
    }

    private fun CatalogValidationFailure.prettyName(): String =
        if (streamNamespace == null) {
            "'${streamName}' in unspecified namespace"
        } else {
            "'${streamName}' in namespace '$streamNamespace'"
        }
}
