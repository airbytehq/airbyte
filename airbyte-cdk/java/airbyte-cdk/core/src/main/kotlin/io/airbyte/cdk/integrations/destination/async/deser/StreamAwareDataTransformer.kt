/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.async.deser

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMeta
import io.airbyte.protocol.models.v0.StreamDescriptor

interface StreamAwareDataTransformer {
    /**
     * Transforms the input data by applying destination limitations and populating
     * [AirbyteRecordMessageMeta]. The returned pair contains the transformed data and the merged
     * meta information from upstream.
     *
     * @param streamDescriptor
     * @param data
     * @param meta
     * @return
     */
    fun transform(
        streamDescriptor: StreamDescriptor?,
        data: JsonNode?,
        meta: AirbyteRecordMessageMeta?,
    ): Pair<JsonNode?, AirbyteRecordMessageMeta?>
}
