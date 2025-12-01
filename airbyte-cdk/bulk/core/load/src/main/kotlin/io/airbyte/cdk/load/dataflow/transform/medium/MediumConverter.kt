/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.transform.medium

import io.airbyte.cdk.load.dataflow.state.PartitionKey
import io.airbyte.cdk.load.message.DestinationRecordRaw

/**
 * Defines a contract for converting a given input into a structured map representation.
 *
 * This interface provides the blueprint for implementing a conversion process that transforms raw
 * destination record data, partitioning metadata, and optional source records into a map structure
 * with specific key-value pairs.
 */
interface MediumConverter {
    /**
     * Converts the given {@link ConversionInput} into a map representation containing transformed
     * data.
     *
     * @param input a {@link ConversionInput} object containing the raw destination record,
     * partition key,
     * ```
     *              and optionally the source record to be transformed.
     * @return
     * ```
     * a map where keys are string representations of the column names and values are the converted
     * values.
     */
    fun convert(input: ConversionInput): Map<String, Any>
}

/**
 * Represents the input required for a conversion process.
 *
 * This data class encapsulates a set of necessary attributes:
 * - A raw destination record containing data to be converted.
 * - A partition key to associate the record with a specific partition.
 * - An optional source specifying the record's protocol buffer source.
 *
 * @property msg The raw destination record containing the stream, data, and metadata.
 * @property partitionKey The partition key defining the record's association with a partition.
 */
data class ConversionInput(val msg: DestinationRecordRaw, val partitionKey: PartitionKey)
