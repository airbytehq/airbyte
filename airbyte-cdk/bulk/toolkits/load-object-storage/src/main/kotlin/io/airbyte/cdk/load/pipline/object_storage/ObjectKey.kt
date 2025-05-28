/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipline.object_storage

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.WithStream

data class ObjectKey(
    override val stream: DestinationStream.Descriptor,
    val objectKey: String,
    // optional string id to differentiate between uploads with the same key
    val uploadId: String? = null,
) : WithStream
