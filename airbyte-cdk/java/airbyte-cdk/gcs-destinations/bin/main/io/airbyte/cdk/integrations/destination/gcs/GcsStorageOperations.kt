/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.gcs

import com.amazonaws.services.s3.AmazonS3
import com.amazonaws.services.s3.model.DeleteObjectsRequest
import io.airbyte.cdk.integrations.destination.NamingConventionTransformer
import io.airbyte.cdk.integrations.destination.s3.S3DestinationConfig
import io.airbyte.cdk.integrations.destination.s3.S3StorageOperations
import io.github.oshai.kotlinlogging.KotlinLogging

private val LOGGER = KotlinLogging.logger {}

class GcsStorageOperations(
    nameTransformer: NamingConventionTransformer,
    s3Client: AmazonS3,
    s3Config: S3DestinationConfig
) : S3StorageOperations(nameTransformer, s3Client, s3Config) {
    /** GCS only supports the legacy AmazonS3#doesBucketExist method. */
    override fun doesBucketExist(bucket: String?): Boolean {
        @Suppress("deprecation") return s3Client.doesBucketExist(bucket)
    }

    /**
     * This method is overridden because GCS doesn't accept request to delete multiple objects. The
     * only difference is that the AmazonS3#deleteObjects method is replaced with
     * AmazonS3#deleteObject.
     */
    override fun cleanUpObjects(
        bucket: String?,
        keysToDelete: List<DeleteObjectsRequest.KeyVersion>
    ) {
        for (keyToDelete in keysToDelete) {
            LOGGER.info { "Deleting object ${keyToDelete.key}" }
            s3Client.deleteObject(bucket, keyToDelete.key)
        }
    }

    override fun getMetadataMapping(): Map<String, String> {
        return HashMap()
    }

    companion object {}
}
