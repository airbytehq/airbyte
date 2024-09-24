/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

import jakarta.inject.Singleton
import org.apache.kafka.connect.source.SourceRecord

/** Encapsulates the logic for determining whether a cdc sync has reached its target position */
interface CdcPositionMapper {
    fun reachedTargetPosition(record: DebeziumRecord): Boolean

    /** Factory for [CdcPositionMapper] instances. */
    fun interface Factory {
        /** An implementation make a CdcPositionMapper [CdcPositionMapper] instance. */
        fun get(): CdcPositionMapper
    }
    fun reachedTargetPosition(record: SourceRecord): Boolean
}

class DefaultCdcPositionMapper : CdcPositionMapper {
    var counter = 0
    override fun reachedTargetPosition(record: DebeziumRecord): Boolean {
        if (counter < 1) {
            counter++
            return false
        }
        return true
    }

    override fun reachedTargetPosition(record: SourceRecord): Boolean {
        TODO("Not yet implemented")
    }
}

@Singleton
class Factory() : CdcPositionMapper.Factory {

    override fun get(): CdcPositionMapper {
        return DefaultCdcPositionMapper()
    }
}
