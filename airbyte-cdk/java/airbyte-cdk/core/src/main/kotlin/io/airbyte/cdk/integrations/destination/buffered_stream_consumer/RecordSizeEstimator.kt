/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.buffered_stream_consumer

import com.fasterxml.jackson.databind.JsonNode
import com.google.common.annotations.VisibleForTesting
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.v0.AirbyteRecordMessage

/**
 * This class estimate the byte size of the record message. To reduce memory footprint, 1) it
 * assumes that a character is always four bytes, and 2) it only performs a sampling every N
 * records. The size of the samples are averaged together to protect the estimation against
 * outliers.
 */
class RecordSizeEstimator
@JvmOverloads
constructor( // number of record messages
private val sampleBatchSize: Int = DEFAULT_SAMPLE_BATCH_SIZE) {
    // latest estimated record message size for each stream
    private val streamRecordSizeEstimation: MutableMap<String, Long> = HashMap()

    // number of record messages until next real sampling for each stream
    private val streamSampleCountdown: MutableMap<String, Int> = HashMap()

    fun getEstimatedByteSize(record: AirbyteRecordMessage): Long {
        val stream = record.stream
        val countdown = streamSampleCountdown[stream]

        // this is a new stream; initialize its estimation
        if (countdown == null) {
            val byteSize = getStringByteSize(record.data)
            streamRecordSizeEstimation[stream] = byteSize
            streamSampleCountdown[stream] = sampleBatchSize - 1
            return byteSize
        }

        // this stream needs update; compute a new estimation
        if (countdown <= 0) {
            val prevMeanByteSize = streamRecordSizeEstimation[stream]!!
            val currentByteSize = getStringByteSize(record.data)
            val newMeanByteSize = prevMeanByteSize / 2 + currentByteSize / 2
            streamRecordSizeEstimation[stream] = newMeanByteSize
            streamSampleCountdown[stream] = sampleBatchSize - 1
            return newMeanByteSize
        }

        // this stream does not need update; return current estimation
        streamSampleCountdown[stream] = countdown - 1
        return streamRecordSizeEstimation[stream]!!
    }

    companion object {
        // by default, perform one estimation for every 20 records
        private const val DEFAULT_SAMPLE_BATCH_SIZE = 20

        @VisibleForTesting
        fun getStringByteSize(data: JsonNode): Long {
            // assume UTF-8 encoding, and each char is 4 bytes long
            return Jsons.serialize(data).length * 4L
        }
    }
}
