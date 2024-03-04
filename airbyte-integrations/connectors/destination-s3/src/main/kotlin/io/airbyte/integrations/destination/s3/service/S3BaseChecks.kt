/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.service

import com.amazonaws.services.s3.AmazonS3
import com.amazonaws.services.s3.model.ListObjectsRequest
import io.airbyte.cdk.core.context.env.ConnectorConfigurationPropertySource
import io.airbyte.cdk.integrations.destination.s3.util.StreamTransferManagerFactory
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton
import org.apache.commons.csv.CSVFormat
import org.apache.commons.csv.CSVPrinter
import java.io.IOException
import java.io.PrintWriter
import java.nio.charset.StandardCharsets

// TODO Ported from CDK
@Singleton
@Requires(
    property = ConnectorConfigurationPropertySource.CONNECTOR_OPERATION,
    value = "check",
)
class S3BaseChecks(private val s3Client: AmazonS3) {
    private val logger = KotlinLogging.logger {}

    /**
     * Checks that S3 custom endpoint uses a variant that only uses HTTPS
     *
     * @param endpoint URL string representing an accessible S3 bucket
     */
    fun testCustomEndpointSecured(endpoint: String?): Boolean {
        // if user does not use a custom endpoint, do not fail
        return if (endpoint.isNullOrEmpty()) {
            true
        } else {
            endpoint.startsWith("https://")
        }
    }

    fun testIAMUserHasListObjectPermission(bucketName: String) {
        logger.info { "Started testing if IAM user can call listObjects on the destination bucket '$bucketName'..." }
        val request = ListObjectsRequest().withBucketName(bucketName).withMaxKeys(1)
        s3Client.listObjects(request)
        logger.info { "Finished checking for listObjects permission" }
    }

    @Throws(IOException::class)
    fun testMultipartUpload(
        bucketName: String,
        bucketPath: String,
    ) {
        logger.info { "Started testing if all required credentials assigned to user for multipart upload" }
        val prefix = if (bucketPath.endsWith("/")) bucketPath else "$bucketPath/"
        val testFile = prefix + "test_" + System.currentTimeMillis()
        val manager = StreamTransferManagerFactory.create(bucketName, testFile, s3Client).get()
        var success = false
        try {
            manager.multiPartOutputStreams[0].use { outputStream ->
                CSVPrinter(
                    PrintWriter(outputStream, true, StandardCharsets.UTF_8),
                    CSVFormat.DEFAULT,
                ).use { csvPrinter ->
                    val oneMegaByteString = "a".repeat(500000)
                    // write a file larger than the 5 MB, which is the default part size, to make sure it is a multipart
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
        logger.info { "Finished verification for multipart upload mode" }
    }

    fun testSingleUpload(
        bucketName: String,
        bucketPath: String,
    ) {
        logger.info { "Started testing if all required credentials assigned to user for single file uploading" }
        val prefix = if (bucketPath.endsWith("/")) bucketPath else "$bucketPath/"
        val testFile = prefix + "test_" + System.currentTimeMillis()
        try {
            s3Client.putObject(bucketName, testFile, "this is a test file")
        } finally {
            s3Client.deleteObject(bucketName, testFile)
        }
        logger.info { "Finished checking for normal upload mode" }
    }
}
