/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.toolkits.iceberg.parquet.io

import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.ByteArrayOutputStream
import java.io.DataOutputStream
import java.nio.ByteBuffer
import java.nio.charset.StandardCharsets
import java.security.MessageDigest
import org.apache.commons.collections4.bloomfilter.EnhancedDoubleHasher
import org.apache.commons.collections4.bloomfilter.Shape
import org.apache.commons.collections4.bloomfilter.SimpleBloomFilter
import org.apache.iceberg.Schema
import org.apache.iceberg.data.Record

interface EqualityDeleteKeyTracker {
    fun shouldDelete(identifierRecord: Record): Boolean
    fun logSummary(reason: String)
}

class EqualityDeleteBloomFilter(
    private val streamName: String,
    private val deleteSchema: Schema,
    expectedItems: Int,
    numberOfBits: Int,
    numberOfHashFunctions: Int,
    private val logIntervalRecords: Long,
) : EqualityDeleteKeyTracker {
    private val log = KotlinLogging.logger {}
    private val shape = Shape.fromNMK(expectedItems, numberOfBits, numberOfHashFunctions)
    private val bloomFilter = SimpleBloomFilter(shape)
    private val digest = MessageDigest.getInstance("SHA-256")

    private var checkedKeys = 0L
    private var missesAdded = 0L
    private var probableHits = 0L
    private var equalityDeletesEmitted = 0L
    private var equalityDeletesSkipped = 0L

    init {
        log.info {
            "Enabled primary key Bloom filter for stream $streamName " +
                "(expectedItems=$expectedItems, numberOfBits=$numberOfBits, " +
                "numberOfHashFunctions=$numberOfHashFunctions, " +
                "configuredFalsePositiveProbability=${shape.getProbability(expectedItems)})"
        }
    }

    @Synchronized
    override fun shouldDelete(identifierRecord: Record): Boolean {
        checkedKeys += 1
        val hasher = EnhancedDoubleHasher(digest.digest(serializeIdentifierRecord(identifierRecord)))
        val probableHit = bloomFilter.contains(hasher)

        if (probableHit) {
            probableHits += 1
            equalityDeletesEmitted += 1
        } else {
            bloomFilter.merge(hasher)
            missesAdded += 1
            equalityDeletesSkipped += 1
        }

        if (logIntervalRecords > 0 && checkedKeys % logIntervalRecords == 0L) {
            logStats("periodic")
        }

        return probableHit
    }

    @Synchronized
    override fun logSummary(reason: String) {
        logStats(reason)
    }

    private fun logStats(reason: String) {
        val estimatedItems = bloomFilter.estimateN()
        log.info {
            "Primary key Bloom filter stats for stream $streamName ($reason): " +
                "checkedKeys=$checkedKeys, missesAdded=$missesAdded, " +
                "probableHits=$probableHits, equalityDeletesEmitted=$equalityDeletesEmitted, " +
                "equalityDeletesSkipped=$equalityDeletesSkipped, cardinality=${bloomFilter.cardinality()}, " +
                "estimatedItems=$estimatedItems, " +
                "estimatedFalsePositiveProbability=${shape.getProbability(estimatedItems)}, " +
                "numberOfBits=${shape.numberOfBits}, " +
                "numberOfHashFunctions=${shape.numberOfHashFunctions}"
        }
    }

    private fun serializeIdentifierRecord(identifierRecord: Record): ByteArray {
        val output = ByteArrayOutputStream()
        DataOutputStream(output).use { data ->
            data.writeInt(deleteSchema.columns().size)
            deleteSchema.columns().forEach { field ->
                val value = identifierRecord.getField(field.name())
                data.writeInt(field.fieldId())
                data.writeUTF(field.name())
                data.writeUTF(value.javaClass.name)
                val bytes = serializeValue(value)
                data.writeInt(bytes.size)
                data.write(bytes)
            }
        }
        return output.toByteArray()
    }

    private fun serializeValue(value: Any): ByteArray {
        return when (value) {
            is ByteArray -> value
            is ByteBuffer -> {
                val duplicate = value.duplicate()
                val bytes = ByteArray(duplicate.remaining())
                duplicate.get(bytes)
                bytes
            }
            else -> value.toString().toByteArray(StandardCharsets.UTF_8)
        }
    }
}
