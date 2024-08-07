/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.s3

import com.amazonaws.services.s3.AmazonS3
import com.amazonaws.services.s3.model.DeleteObjectsRequest
import com.amazonaws.services.s3.model.ListObjectsRequest
import com.amazonaws.services.s3.model.ObjectListing
import com.amazonaws.services.s3.model.S3ObjectSummary
import io.airbyte.cdk.integrations.destination.NamingConventionTransformer
import io.airbyte.cdk.integrations.destination.s3.util.S3NameTransformer
import java.util.concurrent.Executors
import java.util.concurrent.TimeUnit
import java.util.regex.Pattern
import org.joda.time.DateTime
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.mockito.ArgumentCaptor
import org.mockito.ArgumentMatchers
import org.mockito.Mockito

class S3StorageOperationsTest {

    companion object {
        private const val BUCKET_NAME = "fake-bucket"
        private const val FAKE_BUCKET_PATH = "fake-bucketPath"
        private const val NAMESPACE = "namespace"
        private const val STREAM_NAME = "stream_name1"
        private const val OBJECT_TO_DELETE = "$NAMESPACE/$STREAM_NAME/2022_04_04_123456789_0.csv.gz"
    }

    private lateinit var s3Client: AmazonS3
    private lateinit var s3StorageOperations: S3StorageOperations

    @BeforeEach
    internal fun setup() {
        val nameTransformer: NamingConventionTransformer = S3NameTransformer()
        s3Client = Mockito.mock(AmazonS3::class.java)

        val objectSummary1 =
            Mockito.mock(
                S3ObjectSummary::class.java,
            )
        val objectSummary2 =
            Mockito.mock(
                S3ObjectSummary::class.java,
            )
        val objectSummary3 =
            Mockito.mock(
                S3ObjectSummary::class.java,
            )
        Mockito.`when`(objectSummary1.key).thenReturn(OBJECT_TO_DELETE)
        Mockito.`when`(objectSummary2.key)
            .thenReturn("$NAMESPACE/stream_name2/2022_04_04_123456789_0.csv.gz")
        Mockito.`when`(objectSummary3.key).thenReturn("other_files.txt")

        val results =
            Mockito.mock(
                ObjectListing::class.java,
            )
        Mockito.`when`(results.isTruncated).thenReturn(false)
        Mockito.`when`(results.objectSummaries)
            .thenReturn(listOf(objectSummary1, objectSummary2, objectSummary3))
        Mockito.`when`(
                s3Client.listObjects(
                    ArgumentMatchers.any(
                        ListObjectsRequest::class.java,
                    ),
                ),
            )
            .thenReturn(results)

        val s3Config =
            S3DestinationConfig.create(BUCKET_NAME, FAKE_BUCKET_PATH, "fake-region")
                .withEndpoint("fake-endpoint")
                .withAccessKeyCredential("fake-accessKeyId", "fake-secretAccessKey")
                .withS3Client(s3Client)
                .get()
        s3StorageOperations = S3StorageOperations(nameTransformer, s3Client, s3Config)
    }

    @Test
    internal fun testRegexMatch() {
        val regexFormat =
            Pattern.compile(
                s3StorageOperations.getRegexFormat(
                    NAMESPACE,
                    STREAM_NAME,
                    S3DestinationConstants.DEFAULT_PATH_FORMAT,
                ),
            )
        assertTrue(regexFormat.matcher(OBJECT_TO_DELETE).matches())
        assertTrue(
            regexFormat
                .matcher(
                    s3StorageOperations.getBucketObjectPath(
                        NAMESPACE,
                        STREAM_NAME,
                        DateTime.now(),
                        S3DestinationConstants.DEFAULT_PATH_FORMAT,
                    ),
                )
                .matches(),
        )
        assertFalse(
            regexFormat.matcher("$NAMESPACE/$STREAM_NAME/some_random_file_0.doc").matches(),
        )
        assertFalse(
            regexFormat.matcher("$NAMESPACE/stream_name2/2022_04_04_123456789_0.csv.gz").matches(),
        )
    }

    @Test
    internal fun testCustomRegexMatch() {
        val customFormat =
            "\${NAMESPACE}_\${STREAM_NAME}_\${YEAR}-\${MONTH}-\${DAY}-\${HOUR}-\${MINUTE}-\${SECOND}-\${MILLISECOND}-\${EPOCH}-\${UUID}"
        assertTrue(
            Pattern.compile(
                    s3StorageOperations.getRegexFormat(NAMESPACE, STREAM_NAME, customFormat)
                )
                .matcher(
                    s3StorageOperations.getBucketObjectPath(
                        NAMESPACE,
                        STREAM_NAME,
                        DateTime.now(),
                        customFormat,
                    ),
                )
                .matches(),
        )
    }

    @Test
    internal fun testGetExtension() {
        assertEquals(".csv.gz", S3StorageOperations.getExtension("test.csv.gz"))
        assertEquals(".gz", S3StorageOperations.getExtension("test.gz"))
        assertEquals(".avro", S3StorageOperations.getExtension("test.avro"))
        assertEquals("", S3StorageOperations.getExtension("test-file"))
    }

    @Test
    internal fun testCleanUpBucketObject() {
        val pathFormat = S3DestinationConstants.DEFAULT_PATH_FORMAT
        s3StorageOperations.cleanUpBucketObject(
            NAMESPACE,
            STREAM_NAME,
            FAKE_BUCKET_PATH,
            pathFormat,
        )
        val deleteRequest =
            ArgumentCaptor.forClass(
                DeleteObjectsRequest::class.java,
            )
        Mockito.verify(s3Client).deleteObjects(deleteRequest.capture())
        assertEquals(1, deleteRequest.value.keys.size)
        assertEquals(OBJECT_TO_DELETE, deleteRequest.value.keys[0].key)
    }

    @Test
    internal fun testGetFilename() {
        assertEquals("filename", S3StorageOperations.getFilename("filename"))
        assertEquals("filename", S3StorageOperations.getFilename("/filename"))
        assertEquals("filename", S3StorageOperations.getFilename("/p1/p2/filename"))
        assertEquals("filename.csv", S3StorageOperations.getFilename("/p1/p2/filename.csv"))
    }

    @Test
    @Throws(InterruptedException::class)
    internal fun getPartId() {
        // Multithreaded utility class

        class PartIdGetter(val s3StorageOperations: S3StorageOperations) : Runnable {
            val responses: MutableList<String> = mutableListOf()

            override fun run() {
                responses.add(s3StorageOperations.getPartId(FAKE_BUCKET_PATH))
            }
        }

        val partIdGetter = PartIdGetter(s3StorageOperations)

        // single threaded
        partIdGetter.run() // 0
        partIdGetter.run() // 1
        partIdGetter.run() // 2

        // multithreaded
        val executor = Executors.newFixedThreadPool(3)
        for (i in 0..6) {
            executor.execute(partIdGetter)
        }
        executor.shutdown()
        executor.awaitTermination(5, TimeUnit.SECONDS)

        val responses = partIdGetter.responses
        assertEquals(10, responses.size)
        for (i in 0..9) {
            assertTrue(responses.contains(i.toString()))
        }
    }

    @Test
    internal fun getPartIdMultiplePaths() {
        assertEquals("0", s3StorageOperations.getPartId(FAKE_BUCKET_PATH))
        assertEquals("1", s3StorageOperations.getPartId(FAKE_BUCKET_PATH))
        assertEquals("0", s3StorageOperations.getPartId("other_path"))
    }
}
