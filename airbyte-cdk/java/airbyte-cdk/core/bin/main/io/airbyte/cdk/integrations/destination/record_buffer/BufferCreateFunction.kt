/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.record_buffer

import io.airbyte.commons.functional.CheckedBiFunction
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog

fun interface BufferCreateFunction :
    CheckedBiFunction<
        AirbyteStreamNameNamespacePair, ConfiguredAirbyteCatalog, SerializableBuffer, Exception> {
    @Throws(Exception::class)
    override fun apply(
        stream: AirbyteStreamNameNamespacePair,
        configuredCatalog: ConfiguredAirbyteCatalog
    ): SerializableBuffer?
}
