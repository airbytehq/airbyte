/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.s3

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.integrations.destination.record_buffer.SerializableBuffer
import org.joda.time.DateTime

abstract class BlobStorageOperations protected constructor() {
    protected val blobDecorators: MutableList<BlobDecorator> = ArrayList()

    abstract fun getBucketObjectPath(
        namespace: String?,
        streamName: String,
        writeDatetime: DateTime,
        customFormat: String
    ): String?

    /** Ensure that the bucket specified in the config exists */
    @Throws(Exception::class) abstract fun createBucketIfNotExists()

    /**
     * Upload the data files into the storage area.
     *
     * @return the name of the file that was uploaded.
     */
    @Throws(Exception::class)
    abstract fun uploadRecordsToBucket(
        recordsData: SerializableBuffer,
        namespace: String?,
        objectPath: String
    ): String?

    /** Remove files that were just stored in the bucket */
    @Throws(Exception::class)
    abstract fun cleanUpBucketObject(objectPath: String, stagedFiles: List<String>)

    /**
     * Deletes all the bucket objects for the specified bucket path
     *
     * @param namespace Optional source-defined namespace name
     * @param streamName Name of the stream
     * @param objectPath file path to where staging files are stored
     * @param pathFormat formatted string for the path
     */
    abstract fun cleanUpBucketObject(
        namespace: String?,
        streamName: String,
        objectPath: String,
        pathFormat: String
    )

    abstract fun dropBucketObject(objectPath: String)

    abstract fun isValidData(jsonNode: JsonNode): Boolean

    abstract fun getMetadataMapping(): Map<String, String>

    fun addBlobDecorator(blobDecorator: BlobDecorator) {
        blobDecorators.add(blobDecorator)
    }
}
