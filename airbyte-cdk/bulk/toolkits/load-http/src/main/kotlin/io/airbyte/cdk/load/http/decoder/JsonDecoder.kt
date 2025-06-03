package io.airbyte.cdk.load.http.decoder

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.load.http.Response
import io.airbyte.cdk.util.Jsons

class JsonDecoder {
    fun decode(response: Response): JsonNode {
        return Jsons.readTree(response.body?.use { it.readByteArray() })
    }
}
