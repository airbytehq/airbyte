/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.test.util

import io.airbyte.cdk.load.data.AirbyteType

fun interface ExpectedRecordMapper {
    fun mapRecord(expectedRecord: OutputRecord, schema: AirbyteType): OutputRecord
}

object NoopExpectedRecordMapper : ExpectedRecordMapper {
    override fun mapRecord(expectedRecord: OutputRecord, schema: AirbyteType): OutputRecord =
        expectedRecord
}
