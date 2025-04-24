/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.s3

import com.amazonaws.services.s3.AmazonS3
import com.amazonaws.services.s3.model.ListObjectsRequest
import com.google.common.annotations.VisibleForTesting
import com.google.common.base.Strings
import io.airbyte.cdk.integrations.destination.s3.util.StreamTransferManagerFactory.create
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.IOException
import java.io.PrintWriter
import java.nio.charset.StandardCharsets
import java.util.*
import org.apache.commons.csv.CSVFormat
import org.apache.commons.csv.CSVPrinter

private val LOGGER = KotlinLogging.logger {}

object S3BaseChecks {

    /**
     * Note that this method completely ignores s3Config.getBucketPath(), in favor of the bucketPath
     * parameter.
     */
    @JvmStatic
    fun attemptS3WriteAndDelete(
        storageOperations: S3StorageOperations,
        s3Config: S3DestinationConfig,
        bucketPath: String?
    ) {
        attemptS3WriteAndDelete(storageOperations, s3Config, bucketPath, s3Config.getS3Client())
    }

    @JvmStatic
    fun testSingleUpload(s3Client: AmazonS3, bucketName: String?, bucketPath: String) {
        LOGGER.info {
            "Started testing if all required credentials assigned to user for single file uploading"
        }
        val prefix = if (bucketPath.endsWith("/")) bucketPath else "$bucketPath/"
        val testFile = prefix + "test_" + System.currentTimeMillis()
        try {
            s3Client.putObject(bucketName, testFile, "this is a test file")
        } finally {
            s3Client.deleteObject(bucketName, testFile)
        }
        LOGGER.info { "Finished checking for normal upload mode" }
    }

    @JvmStatic
    @Throws(IOException::class)
    fun testMultipartUpload(s3Client: AmazonS3, bucketName: String?, bucketPath: String) {
        LOGGER.info {
            "Started testing if all required credentials assigned to user for multipart upload"
        }
        val prefix = if (bucketPath.endsWith("/")) bucketPath else "$bucketPath/"
        val testFile = prefix + "test_" + System.currentTimeMillis()
        val manager = create(bucketName, testFile, s3Client).get()
        var success = false
        try {
            manager.multiPartOutputStreams[0].use { outputStream ->
                CSVPrinter(
                        PrintWriter(outputStream, true, StandardCharsets.UTF_8),
                        CSVFormat.DEFAULT
                    )
                    .use { csvPrinter ->
                        val oneMegaByteString = "a".repeat(500000)
                        // write a file larger than the 5 MB, which is the default part size, to
                        // make sure it is a multipart
                        // upload
                        for (i in 0..6) {
                            csvPrinter.printRecord(System.currentTimeMillis(), oneMegaByteString)
                        }
                        success = true
                    }
            }
        } finally {
            if (success) {
                manager.complete()
            } else {
                manager.abort()
            }
            s3Client.deleteObject(bucketName, testFile)
        }
        LOGGER.info { "Finished verification for multipart upload mode" }
    }

    /**
     * Checks that S3 custom endpoint uses a variant that only uses HTTPS
     *
     * @param endpoint URL string representing an accessible S3 bucket
     */
    @JvmStatic
    fun testCustomEndpointSecured(endpoint: String?): Boolean {
        // if user does not use a custom endpoint, do not fail
        return if (endpoint == null || endpoint.length == 0) {
            true
        } else {
            endpoint.startsWith("https://")
        }
    }

    @VisibleForTesting
    fun attemptS3WriteAndDelete(
        storageOperations: S3StorageOperations,
        s3Config: S3DestinationConfig,
        bucketPath: String?,
        s3: AmazonS3
    ) {
        val prefix =
            if (bucketPath.isNullOrEmpty()) {
                ""
            } else if (bucketPath.endsWith("/")) {
                bucketPath
            } else {
                "$bucketPath/"
            }

        val outputTableName =
            prefix +
                "_airbyte_connection_test_" +
                UUID.randomUUID().toString().replace("-".toRegex(), "")
        attemptWriteAndDeleteS3Object(storageOperations, s3Config, outputTableName, s3)
    }

    /**
     * Runs some permissions checks: 1. Check whether the bucket exists; create it if not 2. Check
     * whether s3://bucketName/bucketPath/ exists; create it (with empty contents) if not. (if
     * bucketPath is null/empty-string, then skip this step) 3. Attempt to create and delete
     * s3://bucketName/outputTableName 4. Attempt to list all objects in the bucket
     */
    private fun attemptWriteAndDeleteS3Object(
        storageOperations: S3StorageOperations,
        s3Config: S3DestinationConfig,
        outputTableName: String,
        s3: AmazonS3?
    ) {
        val s3Bucket = s3Config.bucketName
        val bucketPath = s3Config.bucketPath

        if (!Strings.isNullOrEmpty(bucketPath)) {
            storageOperations.createBucketIfNotExists()
        }
        s3!!.putObject(s3Bucket, outputTableName, "check-content")
        testIAMUserHasListObjectPermission(s3, s3Bucket)
        s3.deleteObject(s3Bucket, outputTableName)
    }

    fun testIAMUserHasListObjectPermission(s3: AmazonS3, bucketName: String?) {
        LOGGER.info { "Started testing if IAM user can call listObjects on the destination bucket" }
        val request = ListObjectsRequest().withBucketName(bucketName).withMaxKeys(1)
        s3.listObjects(request)
        LOGGER.info { "Finished checking for listObjects permission" }
    }
}
