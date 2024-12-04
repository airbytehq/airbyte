/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.s3

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.integrations.destination.s3.S3BaseAvroDestinationAcceptanceTest
import io.airbyte.cdk.integrations.standardtest.destination.ProtocolVersion
import io.airbyte.cdk.integrations.standardtest.destination.comparator.TestDataComparator
import org.junit.jupiter.api.Disabled
import org.junit.jupiter.api.Test

class S3V2AvroDestinationAcceptanceTest : S3BaseAvroDestinationAcceptanceTest() {
    override val imageName: String = "airbyte/destination-s3-v2:dev"

    override fun getProtocolVersion(): ProtocolVersion {
        return ProtocolVersion.V1
    }

    override fun getTestDataComparator(): TestDataComparator {
        return S3V2AvroParquetTestDataComparator()
    }

    override val baseConfigJson: JsonNode
        get() = S3V2DestinationTestUtils.baseConfigJsonFilePath

    @Test
    @Disabled("Pending FILE TRANSFER S3V2")
    override fun testFakeFileTransfer() {
        super.testFakeFileTransfer()
    }
}
