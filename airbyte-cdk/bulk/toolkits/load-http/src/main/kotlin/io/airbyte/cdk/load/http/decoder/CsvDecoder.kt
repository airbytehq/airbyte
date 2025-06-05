package io.airbyte.cdk.load.http.decoder

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.ObjectMapper
import io.airbyte.cdk.load.http.Response
import java.io.InputStreamReader
import java.nio.charset.StandardCharsets
import org.apache.commons.csv.CSVFormat
import org.apache.commons.csv.CSVParser

class CsvDecoder(private val csvFormat: CSVFormat = CSVFormat.Builder.create().setRecordSeparator("\n").setHeader().build()) {
    private val mapper: ObjectMapper  = ObjectMapper()

    fun decode(response: Response): Sequence<JsonNode> {
        val parser = CSVParser(InputStreamReader(response.body!!.inputStream(), StandardCharsets.UTF_8),
            csvFormat
        )
        return parser.use { it.asSequence().map { csvRecord -> mapper.convertValue(csvRecord.toMap(), JsonNode::class.java) } }
    }
}
