/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file.csv

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.ObjectMapper
import java.io.InputStream
import java.io.InputStreamReader
import java.nio.charset.StandardCharsets
import java.util.stream.Stream
import org.apache.commons.csv.CSVFormat
import org.apache.commons.csv.CSVParser

class CsvDecoder(
    private val csvFormat: CSVFormat =
        CSVFormat.Builder.create().setRecordSeparator("\n").setHeader().build()
) {
    private val mapper: ObjectMapper = ObjectMapper()

    fun decode(input: InputStream): Stream<JsonNode> {
        val parser = CSVParser(InputStreamReader(input, StandardCharsets.UTF_8), csvFormat)
        return parser.stream().map { csvRecord ->
            mapper.convertValue(csvRecord.toMap(), JsonNode::class.java)
        }
    }
}
