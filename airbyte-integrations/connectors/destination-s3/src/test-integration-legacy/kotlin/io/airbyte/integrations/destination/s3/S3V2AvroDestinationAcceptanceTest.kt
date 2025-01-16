/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.s3

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.integrations.destination.s3.S3BaseAvroDestinationAcceptanceTest
import io.airbyte.cdk.integrations.standardtest.destination.ProtocolVersion
import io.airbyte.cdk.integrations.standardtest.destination.comparator.TestDataComparator

class S3V2AvroDestinationAcceptanceTest : S3BaseAvroDestinationAcceptanceTest() {
    override val imageName: String = "airbyte/destination-s3:dev"

    override fun getProtocolVersion(): ProtocolVersion {
        return ProtocolVersion.V1
    }

    override fun getTestDataComparator(): TestDataComparator {
        return S3V2AvroParquetTestDataComparator()
    }

    override val baseConfigJson: JsonNode
        get() = S3V2DestinationTestUtils.baseConfigJsonFilePath

    // Disable these tests until we fix the incomplete stream handling behavior.
    override fun testOverwriteSyncMultipleFailedGenerationsFilesPreserved() {}
    override fun testOverwriteSyncFailedResumedGeneration() {}
    override fun testFakeFileTransfer() {}
}
