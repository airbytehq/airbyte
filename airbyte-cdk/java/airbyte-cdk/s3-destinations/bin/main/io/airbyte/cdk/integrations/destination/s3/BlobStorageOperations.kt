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
        objectPath: String,
        generationId: Long,
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

    /** Clean up all the objects matching the provided [keysToDelete] */
    abstract fun cleanUpObjects(keysToDelete: List<String>)

    /**
     * List all the existing bucket objects for a given [namespace], [streamName], [objectPath] and
     * an optional [currentGenerationId] which matches the [pathFormat] regex. The returned objects
     * will be filtered with generationId metadata strictly less than [currentGenerationId]
     * @return List of keys of the objects
     */
    abstract fun listExistingObjects(
        namespace: String?,
        streamName: String,
        objectPath: String,
        pathFormat: String,
        currentGenerationId: Long? = null // Sentinel default
    ): List<String>

    abstract fun dropBucketObject(objectPath: String)

    abstract fun isValidData(jsonNode: JsonNode): Boolean

    abstract fun getMetadataMapping(): Map<String, String>

    fun addBlobDecorator(blobDecorator: BlobDecorator) {
        blobDecorators.add(blobDecorator)
    }

    /**
     * Provides the generationId from the last written object's metadata. If there are no objects in
     * the given path format, returns nullå
     */
    open fun getStageGeneration(
        namespace: String?,
        streamName: String,
        objectPath: String,
        pathFormat: String
    ): Long? {
        return null
    }
}
