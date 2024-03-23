/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.s3.util

import io.airbyte.cdk.integrations.destination.s3.S3DestinationConstants
import io.airbyte.protocol.models.v0.AirbyteStream
import java.util.*

object S3OutputPathHelper {
    @JvmStatic
    fun getOutputPrefix(bucketPath: String?, stream: AirbyteStream): String {
        return getOutputPrefix(bucketPath, stream.namespace, stream.name)
    }

    /** Prefix: &lt;bucket-path&gt;/&lt;source-namespace-if-present&gt;/&lt;stream-name&gt; */
    // Prefix: <bucket-path>/<source-namespace-if-present>/<stream-name>
    fun getOutputPrefix(bucketPath: String?, namespace: String?, streamName: String): String {
        val paths: MutableList<String> = LinkedList()

        if (bucketPath != null) {
            paths.add(bucketPath)
        }
        if (namespace != null) {
            paths.add(S3DestinationConstants.NAME_TRANSFORMER.convertStreamName(namespace))
        }
        paths.add(S3DestinationConstants.NAME_TRANSFORMER.convertStreamName(streamName))

        return java.lang.String.join("/", paths).replace("/+".toRegex(), "/")
    }
}
