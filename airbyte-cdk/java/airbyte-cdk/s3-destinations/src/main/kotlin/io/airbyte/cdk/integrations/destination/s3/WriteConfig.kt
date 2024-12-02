/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.s3

import io.airbyte.protocol.models.v0.DestinationSyncMode

open class WriteConfig
@JvmOverloads
constructor(
    val namespace: String?,
    val streamName: String,
    val outputBucketPath: String,
    val pathFormat: String,
    val fullOutputPath: String,
    val syncMode: DestinationSyncMode,
    val generationId: Long,
    val minimumGenerationId: Long,
    val storedFiles: MutableList<String> = arrayListOf(),
    val objectsFromOldGeneration: MutableList<String> = arrayListOf()
) {

    fun addStoredFile(file: String) {
        storedFiles.add(file)
    }

    fun clearStoredFiles() {
        storedFiles.clear()
    }

    override fun toString(): String {
        return "WriteConfig(namespace=$namespace, streamName='$streamName', outputBucketPath='$outputBucketPath', pathFormat='$pathFormat', fullOutputPath='$fullOutputPath', syncMode=$syncMode, generationId=$generationId, minimumGenerationId=$minimumGenerationId)"
    }
}
