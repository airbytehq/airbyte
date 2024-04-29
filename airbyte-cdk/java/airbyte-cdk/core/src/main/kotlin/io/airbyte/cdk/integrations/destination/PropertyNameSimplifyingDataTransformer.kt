/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.integrations.destination.async.deser.StreamAwareDataTransformer
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMeta
import io.airbyte.protocol.models.v0.StreamDescriptor

/** @see StandardNameTransformer.formatJsonPath for details on what this class does. */
class PropertyNameSimplifyingDataTransformer : StreamAwareDataTransformer {
    override fun transform(
        streamDescriptor: StreamDescriptor?,
        data: JsonNode?,
        meta: AirbyteRecordMessageMeta?,
    ): Pair<JsonNode?, AirbyteRecordMessageMeta?> {
        if (data == null) {
            return Pair(null, meta)
        }
        return Pair(StandardNameTransformer.formatJsonPath(data), meta)
    }
}
