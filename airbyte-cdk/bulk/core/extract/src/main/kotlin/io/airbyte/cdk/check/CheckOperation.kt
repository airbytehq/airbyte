/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.check

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.Operation
import io.airbyte.cdk.SystemErrorException
import io.airbyte.cdk.command.CONNECTOR_CONFIG_PREFIX
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.command.ConfigurationSpecificationSupplier
import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.command.SourceConfigurationFactory
import io.airbyte.cdk.discover.MetadataQuerier
import io.airbyte.cdk.output.ExceptionHandler
import io.airbyte.cdk.output.OutputConsumer
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Requires
import io.micronaut.context.annotation.Value
import jakarta.inject.Singleton

@Singleton
@Requires(property = Operation.PROPERTY, value = "check")
@Requires(env = ["source"])
class CheckOperation<T : ConfigurationSpecification>(
    val configJsonObjectSupplier: ConfigurationSpecificationSupplier<T>,
    val configFactory: SourceConfigurationFactory<T, out SourceConfiguration>,
    val metadataQuerierFactory: MetadataQuerier.Factory<SourceConfiguration>,
    val outputConsumer: OutputConsumer,
    val exceptionHandler: ExceptionHandler,
    /** Present only in connectors which support section checks, see [CheckSectionHandler]. */
    val checkSectionHandler: CheckSectionHandler<T>? = null,
    /** The configuration JSON object as given to the CLI, which is where [CHECK_SECTION_KEY] is. */
    @Value("\${$CONNECTOR_CONFIG_PREFIX.json}") val configJson: String? = null,
    /**
     * [CHECK_SECTION_KEY] as a Micronaut property, for unit tests which configure the connector
     * through `airbyte.connector.config.*` properties instead of a JSON object.
     */
    @Value("\${$CONNECTOR_CONFIG_PREFIX.$CHECK_SECTION_KEY}")
    val checkSectionProperty: String? = null,
) : Operation {
    private val log = KotlinLogging.logger {}

    /** Wraps all checks in exception handling because CHECK must always exit cleanly. */
    override fun execute() {
        try {
            log.info { "Parsing connector configuration JSON object." }
            val pojo: T = configJsonObjectSupplier.get()
            val section: String? = requestedSection()
            if (section == null) {
                fullCheck(pojo)
            } else {
                sectionCheck(section, pojo)
            }
        } catch (e: Exception) {
            log.debug(e) { "Exception while checking config." }
            val (errorTraceMessage, connectionStatusMessage) =
                exceptionHandler.handleCheckFailure(e)
            outputConsumer.accept(errorTraceMessage)
            outputConsumer.accept(connectionStatusMessage)
            log.info { "Config check failed." }
            return
        }
        log.info { "Config check completed successfully." }
        outputConsumer.accept(
            AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.SUCCEEDED),
        )
    }

    /** Checks the complete configuration: builds it, connects, and runs every check. */
    private fun fullCheck(pojo: T) {
        log.info { "Building internal connector configuration object." }
        val config: SourceConfiguration = configFactory.make(pojo)
        log.info { "Connecting for config check." }
        metadataQuerierFactory.session(config).use {
            connectionCheck(it)
            it.extraChecks()
        }
    }

    /**
     * Checks a partial configuration up to [section], one of the sections the specification
     * declares. The last section completes the configuration and gets the [fullCheck]; the others
     * are delegated to the connector's [CheckSectionHandler].
     */
    private fun sectionCheck(section: String, pojo: T) {
        val declared: List<String> = declaredSections()
        if (declared.isEmpty()) {
            throw ConfigErrorException(
                "'$CHECK_SECTION_KEY' is not supported: " +
                    "the connector specification declares no sections.",
            )
        }
        if (section !in declared) {
            throw ConfigErrorException(
                "Unknown $CHECK_SECTION_KEY '$section'; " +
                    "the connector specification declares: ${declared.joinToString(", ")}.",
            )
        }
        if (section == declared.last()) {
            log.info { "Section '$section' is the last one, running the full config check." }
            fullCheck(pojo)
            return
        }
        val handler: CheckSectionHandler<T> =
            checkSectionHandler
                ?: throw SystemErrorException(
                    "The connector specification declares sections " +
                        "but the connector has no ${CheckSectionHandler::class.simpleName}.",
                )
        log.info { "Checking configuration section '$section'." }
        handler.check(section, pojo)
    }

    /** The section named by [CHECK_SECTION_KEY] in the configuration; null for a full check. */
    private fun requestedSection(): String? {
        val fromJson: String? = configJson?.let { json: String ->
            val node: JsonNode = Jsons.readTree(json).path(CHECK_SECTION_KEY)
            when {
                node.isMissingNode || node.isNull -> null
                node.isTextual -> node.asText()
                else -> throw ConfigErrorException("'$CHECK_SECTION_KEY' must be a string.")
            }
        }
        return (fromJson ?: checkSectionProperty)?.takeIf { it.isNotBlank() }
    }

    /** The `sections[].id` values of the specification, in order; empty without `sections`. */
    private fun declaredSections(): List<String> =
        configJsonObjectSupplier.jsonSchema.path("sections").mapNotNull { section: JsonNode ->
            section.path("id").takeIf { it.isTextual }?.asText()
        }

    /**
     * Checks the validity of the provided config:
     * - by discovering the available tables,
     * - by querying at least one table successfully.
     */
    private fun connectionCheck(metadataQuerier: MetadataQuerier) {
        log.info { "Querying all stream names and namespaces." }
        var n = 0
        val namespaces: List<String?> = listOf<String?>(null) + metadataQuerier.streamNamespaces()
        for (namespace in namespaces) {
            for (streamID in metadataQuerier.streamNames(namespace)) {
                try {
                    metadataQuerier.fields(streamID)
                } catch (e: Exception) {
                    log.info(e) {
                        "Query failed on stream '${streamID.name}' in '${namespace ?: ""}': ${e.message}"
                    }
                    n++
                    continue
                }
                log.info {
                    "Query successful on stream '${streamID.name}' in '${namespace ?: ""}'."
                }
                return
            }
        }
        if (n == 0) {
            throw ConfigErrorException("Discovered zero tables.")
        } else {
            throw ConfigErrorException("Unable to query any of the $n discovered table(s).")
        }
    }

    companion object {
        const val COMMON_EXCEPTION_MESSAGE_TEMPLATE: String =
            "Could not connect with provided configuration. Error: %s"
    }
}
