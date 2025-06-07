/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.http.decoder

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.ObjectMapper
import io.airbyte.cdk.load.http.Response
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

    fun decode(response: Response): Stream<JsonNode> {
        val parser =
            CSVParser(
                response.body?.let { InputStreamReader(it, StandardCharsets.UTF_8) },
                csvFormat
            )
        return parser.stream().map { csvRecord ->
            mapper.convertValue(csvRecord.toMap(), JsonNode::class.java)
        }
    }
}
