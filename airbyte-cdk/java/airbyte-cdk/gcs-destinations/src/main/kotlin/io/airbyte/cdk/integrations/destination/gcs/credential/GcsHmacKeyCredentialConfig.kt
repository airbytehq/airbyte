/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.gcs.credential

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.integrations.destination.s3.credential.S3AccessKeyCredentialConfig
import io.airbyte.cdk.integrations.destination.s3.credential.S3CredentialConfig
import java.util.*

class GcsHmacKeyCredentialConfig : GcsCredentialConfig {
    val hmacKeyAccessId: String
    val hmacKeySecret: String

    constructor(credentialConfig: JsonNode) {
        this.hmacKeyAccessId = credentialConfig["hmac_key_access_id"].asText()
        this.hmacKeySecret = credentialConfig["hmac_key_secret"].asText()
    }

    constructor(hmacKeyAccessId: String, hmacKeySecret: String) {
        this.hmacKeyAccessId = hmacKeyAccessId
        this.hmacKeySecret = hmacKeySecret
    }

    override val credentialType: GcsCredentialType
        get() = GcsCredentialType.HMAC_KEY

    override val s3CredentialConfig: Optional<S3CredentialConfig>
        get() = Optional.of(S3AccessKeyCredentialConfig(hmacKeyAccessId, hmacKeySecret))
}
