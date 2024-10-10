/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.dev_null

import io.airbyte.cdk.load.test.util.DestinationDataDumper
import io.airbyte.cdk.load.test.util.OutputRecord

object DevNullDestinationDataDumper : DestinationDataDumper {
    override fun dumpRecords(streamName: String, streamNamespace: String?): List<OutputRecord> {
        // E2e destination doesn't actually write records, so we shouldn't even
        // have tests that try to read back the records
        throw NotImplementedError()
    }
}
