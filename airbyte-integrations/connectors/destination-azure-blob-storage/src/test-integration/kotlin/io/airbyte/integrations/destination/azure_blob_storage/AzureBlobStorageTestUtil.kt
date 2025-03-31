/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_blob_storage

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.load.command.object_storage.ObjectStorageFormatSpecification
import io.airbyte.cdk.load.util.Jsons
import java.nio.file.Files
import java.nio.file.Path

object AzureBlobStorageTestUtil {
    val configPath = Path.of("secrets/config.json")

    fun getConfig(format: ObjectStorageFormatSpecification): String {
        // slightly annoying - we can't easily _edit_ AzureBlobStorageSpecification objects
        // so we just work on raw jsonnode here
        val config = Jsons.readTree(Files.readString(configPath)) as ObjectNode
        config.set<JsonNode>("format", Jsons.valueToTree(format))
        return Jsons.writeValueAsString(config)
    }
}
