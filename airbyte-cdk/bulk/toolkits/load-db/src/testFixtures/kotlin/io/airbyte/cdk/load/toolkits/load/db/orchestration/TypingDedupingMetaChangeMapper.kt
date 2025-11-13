/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.toolkits.load.db.orchestration

import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.test.util.ExpectedRecordMapper
import io.airbyte.cdk.load.test.util.OutputRecord
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Reason

/**
 * T+D generated different _airbyte_meta changes than what we do now, because we didn't have any way
 * to distinguish between e.g. size limitation vs invalid value. so we just map all the DESTINATION
 * reasons to DESTINATION_TYPECAST_ERROR.
 */
object TypingDedupingMetaChangeMapper : ExpectedRecordMapper {
    override fun mapRecord(expectedRecord: OutputRecord, schema: AirbyteType): OutputRecord {
        val modifiedMeta =
            expectedRecord.airbyteMeta?.let { meta ->
                meta.copy(
                    changes =
                        meta.changes.map { change ->
                            val newReason =
                                when (change.reason) {
                                    Reason.DESTINATION_RECORD_SIZE_LIMITATION,
                                    Reason.DESTINATION_FIELD_SIZE_LIMITATION,
                                    Reason.DESTINATION_SERIALIZATION_ERROR ->
                                        Reason.DESTINATION_TYPECAST_ERROR
                                    else -> change.reason
                                }
                            change.copy(reason = newReason)
                        }
                )
            }
        return expectedRecord.copy(airbyteMeta = modifiedMeta)
    }
}
