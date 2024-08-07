/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.gcs.util

import java.io.IOException
import org.apache.hadoop.fs.s3a.Retries
import org.apache.hadoop.fs.s3a.S3AFileSystem

/** Patch [S3AFileSystem] to make it work for GCS. */
class GcsS3FileSystem : S3AFileSystem() {
    /**
     * Method `doesBucketExistV2` used in the [S3AFileSystem.verifyBucketExistsV2] does not work for
     * GCS.
     */
    @Retries.RetryTranslated
    @Throws(IOException::class)
    override fun verifyBucketExistsV2() {
        super.verifyBucketExists()
    }
}
