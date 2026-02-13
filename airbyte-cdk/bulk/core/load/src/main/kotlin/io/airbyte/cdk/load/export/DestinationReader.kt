/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.export

import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.command.DestinationStream

interface DestinationReader {
    fun exportRecords(
        spec: ConfigurationSpecification,
        stream: DestinationStream,
    ): Sequence<ExportedRecord>

    fun exportFile(
        spec: ConfigurationSpecification,
        stream: DestinationStream,
    ): Map<String, String>
}
