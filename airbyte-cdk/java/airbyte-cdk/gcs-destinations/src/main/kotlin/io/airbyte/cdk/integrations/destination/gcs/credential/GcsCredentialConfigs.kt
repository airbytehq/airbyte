/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.gcs.credential

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.commons.json.Jsons
import java.util.*

object GcsCredentialConfigs {
    fun getCredentialConfig(config: JsonNode): GcsCredentialConfig {
        val credentialConfig = config["credential"]
        val credentialType =
            GcsCredentialType.valueOf(
                credentialConfig["credential_type"].asText().uppercase(Locale.getDefault())
            )

        if (credentialType == GcsCredentialType.HMAC_KEY) {
            return GcsHmacKeyCredentialConfig(credentialConfig)
        }
        throw RuntimeException("Unexpected credential: " + Jsons.serialize(credentialConfig))
    }
}
