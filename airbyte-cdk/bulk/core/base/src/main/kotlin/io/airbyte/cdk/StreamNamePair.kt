/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk

import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair
import io.airbyte.protocol.models.v0.StreamDescriptor

/**
 * [StreamNamePair] is equivalent to [AirbyteStreamNameNamespacePair].
 *
 * This exists to avoid coupling the Bulk CDK code too closely to the Airbyte Protocol objects.
 */
data class StreamNamePair(val name: String, val namespace: String?) {
    override fun toString(): String {
        return if (namespace == null) name else "${namespace}_${name}"
    }
}

fun StreamNamePair.asProtocolStreamDescriptor(): StreamDescriptor =
    StreamDescriptor().withName(name).withNamespace(namespace)

fun StreamDescriptor.asStreamNamePair(): StreamNamePair = StreamNamePair(name, namespace)
