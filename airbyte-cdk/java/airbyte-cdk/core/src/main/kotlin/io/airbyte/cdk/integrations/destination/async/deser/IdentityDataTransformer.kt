/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.async.deser

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMeta
import io.airbyte.protocol.models.v0.StreamDescriptor

/** Identity transformer which echoes back the original data and meta. */
class IdentityDataTransformer : StreamAwareDataTransformer {
    override fun transform(
        streamDescriptor: StreamDescriptor?,
        data: JsonNode?,
        meta: AirbyteRecordMessageMeta?,
    ): Pair<JsonNode?, AirbyteRecordMessageMeta?> {
        return Pair(data, meta)
    }
}
