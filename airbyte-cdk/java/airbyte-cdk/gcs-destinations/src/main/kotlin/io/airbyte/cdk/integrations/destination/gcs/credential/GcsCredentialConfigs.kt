/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.gcs.credential

import com.fasterxml.jackson.databind.JsonNode
import java.util.*

object GcsCredentialConfigs {
    fun getCredentialConfig(config: JsonNode): GcsCredentialConfig {
        val credentialConfig = config["credential"]
        val credentialType =
            GcsCredentialType.valueOf(
                credentialConfig["credential_type"].asText().uppercase(Locale.getDefault())
            )

        return when (credentialType) {
            GcsCredentialType.HMAC_KEY -> GcsHmacKeyCredentialConfig(credentialConfig)
            GcsCredentialType.SERVICE_ACCOUNT -> GcsServiceAccountCredentialConfig(credentialConfig)
        }
    }
}
