/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.jdbc.copy.gcs

import com.fasterxml.jackson.databind.JsonNode

class GcsConfig(val projectId: String, val bucketName: String, val credentialsJson: String) {
    companion object {
        fun getGcsConfig(config: JsonNode): GcsConfig {
            return GcsConfig(
                config["loading_method"]["project_id"].asText(),
                config["loading_method"]["bucket_name"].asText(),
                config["loading_method"]["credentials_json"].asText()
            )
        }
    }
}
