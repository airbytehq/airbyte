/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.test.util

import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.export.DestinationReader
import io.airbyte.cdk.load.export.ExportedRecord

interface DestinationDataDumper {
    fun dumpRecords(spec: ConfigurationSpecification, stream: DestinationStream): List<OutputRecord>
    fun dumpFile(spec: ConfigurationSpecification, stream: DestinationStream): Map<String, String>
}

/**
 * Some integration tests don't need to actually read records from the destination, and can use this
 * implementation to satisfy the compiler.
 */
object FakeDataDumper : DestinationDataDumper {
    override fun dumpRecords(
        spec: ConfigurationSpecification,
        stream: DestinationStream
    ): List<OutputRecord> {
        throw NotImplementedError()
    }

    override fun dumpFile(
        spec: ConfigurationSpecification,
        stream: DestinationStream
    ): Map<String, String> {
        throw NotImplementedError()
    }
}

class DestinationDataDumperAdapter(
    private val dumper: DestinationDataDumper,
) : DestinationReader {
    override fun exportRecords(
        spec: ConfigurationSpecification,
        stream: DestinationStream,
    ): Sequence<ExportedRecord> =
        dumper.dumpRecords(spec, stream).asSequence().map { it.toExportedRecord() }

    override fun exportFile(
        spec: ConfigurationSpecification,
        stream: DestinationStream,
    ): Map<String, String> = dumper.dumpFile(spec, stream)
}

fun DestinationDataDumper.asReader(): DestinationReader = DestinationDataDumperAdapter(this)
