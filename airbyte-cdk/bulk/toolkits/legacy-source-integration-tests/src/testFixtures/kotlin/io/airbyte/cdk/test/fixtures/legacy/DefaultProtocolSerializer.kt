/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.test.fixtures.legacy

import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog

class DefaultProtocolSerializer : ProtocolSerializer {
    override fun serialize(configuredAirbyteCatalog: ConfiguredAirbyteCatalog): String {
        return Jsons.serialize(configuredAirbyteCatalog)
    }
}
