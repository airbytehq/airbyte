package io.airbyte.integrations.destination.azure_blob_storage

import io.airbyte.cdk.load.util.Jsons
import java.nio.file.Files
import java.nio.file.Path

object AzureBlobStorageTestUtil {
    val configPath = Path.of("secrets/config.json")

    private val baseConfigContents = Jsons.readTree(Files.readString(configPath))

    fun getConfig(): String {
        // TODO accept params (csv vs jsonl, etc)
        return Jsons.writeValueAsString(baseConfigContents)
    }
}
