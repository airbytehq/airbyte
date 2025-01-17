/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk

import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair
import io.airbyte.protocol.models.v0.StreamDescriptor

/**
 * [StreamIdentifier] is equivalent to [AirbyteStreamNameNamespacePair].
 *
 * This exists to avoid coupling the Bulk CDK code too closely to the Airbyte Protocol objects.
 */
data class StreamIdentifier
constructor(
    val namespace: String?,
    val name: String,
) {
    companion object {
        fun from(desc: StreamDescriptor): StreamIdentifier =
            StreamIdentifier(desc.namespace, desc.name)

        fun from(stream: AirbyteStream): StreamIdentifier =
            StreamIdentifier(stream.namespace, stream.name)
    }

    override fun toString(): String {
        return if (namespace == null) name else "${namespace}.${name}"
    }
}

fun StreamIdentifier.asProtocolStreamDescriptor(): StreamDescriptor =
    StreamDescriptor().withName(name).withNamespace(namespace)
