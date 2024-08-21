/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.s3

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.integrations.destination.s3.S3BaseCsvDestinationAcceptanceTest

class S3CsvAssumeRoleDestinationAcceptanceTest : S3BaseCsvDestinationAcceptanceTest() {
    override val baseConfigJson: JsonNode
        get() = S3DestinationTestUtils.assumeRoleConfig

    override fun getConnectorEnv(): Map<String, String> {
        return S3DestinationTestUtils.assumeRoleInternalCredentials
    }
}
