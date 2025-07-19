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
    val invalidConfig = Path.of("src/test-integration/resources/check/invalid-config.json")
    val sasConfigPath = Path.of("secrets/config_sas.json")

    fun getAccountKeyConfig(format: ObjectStorageFormatSpecification): String {
        return getConfig(configPath, format)
    }

    fun getSasConfig(format: ObjectStorageFormatSpecification): String {
        return getConfig(sasConfigPath, format)
    }

    fun getInvalidConfig(format: ObjectStorageFormatSpecification): String {
        return getConfig(invalidConfig, format)
    }

    fun getConfig(path: Path, format: ObjectStorageFormatSpecification): String {
        // slightly annoying - we can't easily _edit_ AzureBlobStorageSpecification objects
        // so we just work on raw jsonnode here
        val config = Jsons.readTree(Files.readString(path)) as ObjectNode
        config.set<JsonNode>("format", Jsons.valueToTree(format))
        return Jsons.writeValueAsString(config)
    }
}
