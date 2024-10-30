/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.test.util

fun interface ExpectedRecordMapper {
    fun mapRecord(expectedRecord: OutputRecord): OutputRecord
}

object NoopExpectedRecordMapper : ExpectedRecordMapper {
    override fun mapRecord(expectedRecord: OutputRecord): OutputRecord = expectedRecord
}
