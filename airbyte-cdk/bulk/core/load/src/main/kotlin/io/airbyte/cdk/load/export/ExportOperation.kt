/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.export

import io.airbyte.cdk.Operation
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.command.DestinationCatalog
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton

@Singleton
@Requires(property = Operation.PROPERTY, value = "export-data")
class ExportOperation(
    private val catalog: DestinationCatalog,
    private val spec: ConfigurationSpecification,
    private val destinationReader: DestinationReader,
) : Operation {
    private val log = KotlinLogging.logger {}

    override fun execute() {
        log.info { "Running destination data export..." }
        for (stream in catalog.streams) {
            log.info { "Exporting records for stream: ${stream.mappedDescriptor}" }
            val records = destinationReader.exportRecords(spec, stream)
            records.forEach { record -> println(record.toJsonLine()) }
        }
        log.info { "Destination data export complete." }
    }
}
