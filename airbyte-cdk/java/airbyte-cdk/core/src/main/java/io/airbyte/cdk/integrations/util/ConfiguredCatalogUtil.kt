package io.airbyte.cdk.integrations.util

import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import org.apache.commons.lang3.StringUtils

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
    for (stream in catalog.streams) {
        if (StringUtils.isEmpty(stream.stream.namespace)) {
            stream.stream.namespace = defaultNamespace
        }
    }
}
