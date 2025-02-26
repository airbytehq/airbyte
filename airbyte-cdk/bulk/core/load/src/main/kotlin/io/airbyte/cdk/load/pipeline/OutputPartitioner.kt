/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipeline

import io.airbyte.cdk.load.message.WithStream

/**
 * Used internally by the CDK to determine how to partition data passed between steps. The dev
 * should not implement this directly, but via specialized child classes provided for each loader
 * type.
 */
interface OutputPartitioner<K1 : WithStream, T, K2 : WithStream, U> {
    fun getOutputKey(inputKey: K1, output: U): K2
    fun getPart(outputKey: K2, numParts: Int): Int
}
