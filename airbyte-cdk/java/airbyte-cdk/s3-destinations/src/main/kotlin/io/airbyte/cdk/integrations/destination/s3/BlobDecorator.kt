/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.s3

import com.google.common.annotations.VisibleForTesting
import java.io.OutputStream

/**
 * Represents the ability to modify how a blob is stored, by modifying the data being written and/or
 * the blob's metadata.
 */
interface BlobDecorator {
    fun wrap(stream: OutputStream): OutputStream

    /**
     * Modifies the blob's metadata.
     *
     * In the most common case, BlobDecorator implementations will insert new entries into the
     * metadata map. These entries may be vendor-specific. The metadataKeyMapping parameter defines
     * a mapping from the "canonical" keys to the vendor-specific keys. See
     * [S3StorageOperations.getMetadataMapping] for an example.
     *
     * If a key is not defined in metadataKeyMapping, it will not be inserted into the metadata.
     *
     * @param metadata The blob's metadata
     * @param metadataKeyMapping The mapping from canonical to vendor-specific key names
     */
    fun updateMetadata(
        metadata: MutableMap<String, String>,
        metadataKeyMapping: Map<String, String>
    )

    companion object {
        /**
         * A convenience method for subclasses. Handles inserting new metadata entries according to
         * the metadataKeyMapping.
         */
        @VisibleForTesting
        fun insertMetadata(
            metadata: MutableMap<String, String>,
            metadataKeyMapping: Map<String, String>,
            key: String,
            value: String
        ) {
            if (metadataKeyMapping.containsKey(key)) {
                metadata[metadataKeyMapping.getValue(key)] = value
            }
        }
    }
}
