/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.config

import java.io.InputStream

/**
 * Micronaut work around - wraps the input streams to avoid injecting a List directly, and being
 * subject to Micronaut merging like beans into a single list leading to injecting unexpected extra
 * input streams.
 */
class ConnectorInputStreams(private val values: List<InputStream>) : List<InputStream> by values {
    fun closeAll() = values.forEach { it.close() }
}
