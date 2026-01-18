/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.gcs.credential

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.integrations.destination.s3.credential.S3CredentialConfig
import java.util.*

class GcsServiceAccountCredentialConfig : GcsCredentialConfig {
    val serviceAccountJson: String

    constructor(credentialConfig: JsonNode) {
        this.serviceAccountJson = credentialConfig["service_account"].asText()
    }

    constructor(serviceAccountJson: String) {
        this.serviceAccountJson = serviceAccountJson
    }

    override val credentialType: GcsCredentialType
        get() = GcsCredentialType.SERVICE_ACCOUNT

    override val s3CredentialConfig: Optional<S3CredentialConfig>
        get() = Optional.empty()
}
