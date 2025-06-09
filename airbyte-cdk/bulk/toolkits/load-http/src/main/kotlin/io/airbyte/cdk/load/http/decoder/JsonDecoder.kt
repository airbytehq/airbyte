/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.http.decoder

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.util.Jsons
import java.io.InputStream
import java.io.InputStreamReader

/**
 * In the long run, we think this should be moved to a `load-json` package but there were
 * discussions about changing the Jsons implementation which would impact this. We will therefore
 * wait for this change to happen amd migrate JsonDecoder to it.
 */
class JsonDecoder {
    fun decode(input: InputStream): JsonNode {
        return Jsons.readTree(InputStreamReader(input).use { reader -> reader.readText() })
    }
}
