/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.commons.protocol

import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog

class DefaultProtocolSerializer : ProtocolSerializer {
    override fun serialize(configuredAirbyteCatalog: ConfiguredAirbyteCatalog): String {
        return Jsons.serialize(configuredAirbyteCatalog)
    }
}
