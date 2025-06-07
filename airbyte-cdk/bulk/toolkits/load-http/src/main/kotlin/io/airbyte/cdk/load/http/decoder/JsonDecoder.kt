/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.http.decoder

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.load.http.Response
import io.airbyte.cdk.util.Jsons
import java.io.InputStreamReader

class JsonDecoder {
    fun decode(response: Response): JsonNode {
        return Jsons.readTree(
            response.body?.let { body ->
                InputStreamReader(body).use { reader -> reader.readText() }
            }
        )
    }
}
