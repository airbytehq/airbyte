/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.util

import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog

/**
 * For streams in [catalog] which do not have a namespace specified, explicitly set their namespace
 * to the [defaultNamespace]
 */
fun addDefaultNamespaceToStreams(catalog: ConfiguredAirbyteCatalog, defaultNamespace: String?) {
    if (defaultNamespace == null) {
        return
    }
    // TODO: This logic exists in all V2 destinations.
    // This is sad that if we forget to add this, there will be a null pointer during parseCatalog
    for (catalogStream in catalog.streams) {
        if (catalogStream.stream.namespace.isNullOrEmpty()) {
            catalogStream.stream.namespace = defaultNamespace
        }
    }
}
