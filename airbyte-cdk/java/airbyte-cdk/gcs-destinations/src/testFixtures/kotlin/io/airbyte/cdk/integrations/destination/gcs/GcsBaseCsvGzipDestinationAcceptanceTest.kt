/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.gcs

import com.amazonaws.services.s3.model.S3Object
import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.integrations.destination.s3.util.Flattening
import io.airbyte.cdk.integrations.standardtest.destination.ProtocolVersion
import io.airbyte.commons.json.Jsons
import java.io.IOException
import java.io.InputStreamReader
import java.io.Reader
import java.nio.charset.StandardCharsets
import java.util.Map
import java.util.zip.GZIPInputStream

abstract class GcsBaseCsvGzipDestinationAcceptanceTest : GcsBaseCsvDestinationAcceptanceTest() {
    override fun getProtocolVersion() = ProtocolVersion.V1

    override val formatConfig: JsonNode?
        get() = // config without compression defaults to GZIP
        Jsons.jsonNode(
                Map.of("format_type", outputFormat, "flattening", Flattening.ROOT_LEVEL.value)
            )

    @Throws(IOException::class)
    override fun getReader(s3Object: S3Object): Reader {
        return InputStreamReader(GZIPInputStream(s3Object.objectContent), StandardCharsets.UTF_8)
    }
}
