/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.s3

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.integrations.destination.s3.S3BaseCsvDestinationAcceptanceTest
import io.airbyte.cdk.integrations.standardtest.destination.ProtocolVersion

class S3CsvDestinationAcceptanceTest : S3BaseCsvDestinationAcceptanceTest() {
    override fun getProtocolVersion(): ProtocolVersion {
        return ProtocolVersion.V1
    }

    override val baseConfigJson: JsonNode
        get() = S3DestinationTestUtils.baseConfigJsonFilePath
}
