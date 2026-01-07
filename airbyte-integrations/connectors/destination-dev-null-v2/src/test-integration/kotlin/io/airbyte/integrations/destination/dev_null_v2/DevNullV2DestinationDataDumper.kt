/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.dev_null_v2

import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.test.util.DestinationDataDumper
import io.airbyte.cdk.load.test.util.OutputRecord

/**
 * Dev-null doesn't actually store data, so this dumper returns empty results.
 * This is used by tests to verify that data was "written" (even though it was discarded).
 */
object DevNullV2DestinationDataDumper : DestinationDataDumper {
    override fun dumpRecords(
        spec: ConfigurationSpecification,
        stream: DestinationStream
    ): List<OutputRecord> {
        // Dev-null doesn't store data, so always return empty list
        return emptyList()
    }
    
    override fun dumpFile(
        spec: ConfigurationSpecification,
        stream: DestinationStream
    ): Map<String, String> {
        // Dev-null doesn't support file transfer
        return emptyMap()
    }
}