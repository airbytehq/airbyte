/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.s3

import io.airbyte.protocol.models.v0.DestinationSyncMode

class WriteConfig
@JvmOverloads
constructor(
    val namespace: String?,
    val streamName: String,
    val outputBucketPath: String,
    val pathFormat: String,
    val fullOutputPath: String,
    val syncMode: DestinationSyncMode,
    val storedFiles: MutableList<String> = arrayListOf(),
) {

    fun addStoredFile(file: String) {
        storedFiles.add(file)
    }

    fun clearStoredFiles() {
        storedFiles.clear()
    }

    override fun toString(): String {
        return "WriteConfig{" +
            "streamName=$streamName" +
            ", namespace=$namespace" +
            ", outputBucketPath=$outputBucketPath" +
            ", pathFormat=$pathFormat" +
            ", fullOutputPath=$fullOutputPath" +
            ", syncMode=$syncMode" +
            '}'
    }
}
