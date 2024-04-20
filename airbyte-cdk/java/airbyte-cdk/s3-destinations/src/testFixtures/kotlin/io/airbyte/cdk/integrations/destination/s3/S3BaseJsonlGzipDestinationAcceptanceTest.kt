/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.s3

import com.amazonaws.services.s3.model.S3Object
import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.integrations.destination.s3.util.Flattening
import io.airbyte.commons.json.Jsons
import java.io.BufferedReader
import java.io.IOException
import java.io.InputStreamReader
import java.nio.charset.StandardCharsets
import java.util.zip.GZIPInputStream

abstract class S3BaseJsonlGzipDestinationAcceptanceTest : S3BaseJsonlDestinationAcceptanceTest() {
    override val formatConfig: JsonNode?
        get() = // config without compression defaults to GZIP
        Jsons.jsonNode(mapOf("format_type" to outputFormat, "flattening" to Flattening.NO.value))

    @Throws(IOException::class)
    override fun getReader(s3Object: S3Object): BufferedReader {
        return BufferedReader(
            InputStreamReader(GZIPInputStream(s3Object.objectContent), StandardCharsets.UTF_8)
        )
    }
}
