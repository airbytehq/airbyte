package io.airbyte.cdk.load.http.decoder

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.ObjectMapper
import io.airbyte.cdk.load.http.Response
import java.io.InputStreamReader
import java.nio.charset.StandardCharsets
import org.apache.commons.csv.CSVFormat
import org.apache.commons.csv.CSVParser


class CsvDecoder {  // FIXME not used yet but should be eventually for shelby
    private val mapper: ObjectMapper  = ObjectMapper()

    fun decode(response: Response): Iterable<JsonNode> {
        val parser = CSVParser(InputStreamReader(response.body!!.inputStream(), StandardCharsets.UTF_8), CSVFormat.DEFAULT)
        return parser.map { mapper.convertValue(it.toMap(), JsonNode::class.java) }  // FIXME validate if we close the buffer here
    }
}
