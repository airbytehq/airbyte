/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.gcs

import com.amazonaws.services.s3.model.S3Object
import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.cdk.integrations.destination.s3.FileUploadFormat
import io.airbyte.cdk.integrations.standardtest.destination.ProtocolVersion
import io.airbyte.commons.json.Jsons
import java.io.BufferedReader
import java.io.IOException
import java.io.InputStreamReader
import java.nio.charset.StandardCharsets
import java.util.*
import java.util.Map
import kotlin.collections.List
import kotlin.collections.MutableList

abstract class GcsBaseJsonlDestinationAcceptanceTest :
    GcsDestinationAcceptanceTest(FileUploadFormat.JSONL) {
    override fun getProtocolVersion() = ProtocolVersion.V1

    override val formatConfig: JsonNode?
        get() =
            Jsons.jsonNode(
                Map.of(
                    "format_type",
                    outputFormat,
                    "compression",
                    Jsons.jsonNode(Map.of("compression_type", "No Compression"))
                )
            )

    @Throws(IOException::class)
    override fun retrieveRecords(
        testEnv: TestDestinationEnv?,
        streamName: String,
        namespace: String,
        streamSchema: JsonNode
    ): List<JsonNode> {
        val objectSummaries = getAllSyncedObjects(streamName, namespace)
        val jsonRecords: MutableList<JsonNode> = LinkedList()

        for (objectSummary in objectSummaries!!) {
            val `object` = s3Client!!.getObject(objectSummary!!.bucketName, objectSummary.key)
            getReader(`object`).use { reader ->
                var line: String?
                while ((reader.readLine().also { line = it }) != null) {
                    jsonRecords.add(Jsons.deserialize(line)[JavaBaseConstants.COLUMN_NAME_DATA])
                }
            }
        }

        return jsonRecords
    }

    @Throws(IOException::class)
    protected open fun getReader(s3Object: S3Object): BufferedReader {
        return BufferedReader(InputStreamReader(s3Object.objectContent, StandardCharsets.UTF_8))
    }
}
