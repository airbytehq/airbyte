/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.write.bulk_loader

import com.fasterxml.jackson.dataformat.csv.CsvMapper
import com.fasterxml.jackson.dataformat.csv.CsvSchema
import java.io.OutputStream

class FastCsvWriter(outputStream: OutputStream, header: Array<String>) {
    private val mapper = CsvMapper()
    private val schema =
        CsvSchema.builder()
            .apply { header.forEach { columnName -> addColumn(columnName) } }
            .build()
            .withHeader()

    private val writer = mapper.writer(schema).writeValues(outputStream)

    fun writeRow(values: Array<Any>) {
        writer.write(values)
    }

    fun flush() {
        writer.flush()
    }

    fun close() {
        writer.close()
    }
}
