/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

import io.airbyte.cdk.load.integrationTest.DlqStateFactory
import io.airbyte.cdk.load.integrationTest.DlqTestState
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.StreamKey

class DlqStateWithSampleAndEmptyList : DlqStateWithRecordSample() {
    override fun flush(): List<DestinationRecordRaw>? {
        return super.flush() ?: listOf()
    }

    class Factory : DlqStateFactory {
        override fun create(key: StreamKey, part: Int): DlqTestState =
            DlqStateWithSampleAndEmptyList()
    }
}
