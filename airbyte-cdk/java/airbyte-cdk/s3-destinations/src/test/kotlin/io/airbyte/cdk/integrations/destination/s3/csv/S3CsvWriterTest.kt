/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.s3.csv

import alex.mojaki.s3upload.MultiPartOutputStream
import alex.mojaki.s3upload.StreamTransferManager
import com.amazonaws.services.s3.AmazonS3
import com.amazonaws.services.s3.AmazonS3Client
import com.fasterxml.jackson.databind.ObjectMapper
import io.airbyte.cdk.integrations.base.DestinationConfig.Companion.initialize
import io.airbyte.cdk.integrations.destination.s3.S3DestinationConfig.Companion.create
import io.airbyte.cdk.integrations.destination.s3.util.CompressionType
import io.airbyte.cdk.integrations.destination.s3.util.Flattening
import io.airbyte.cdk.integrations.destination.s3.util.StreamTransferManagerWithMetadata
import io.airbyte.commons.json.Jsons.emptyObject
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.airbyte.protocol.models.v0.DestinationSyncMode
import java.io.ByteArrayOutputStream
import java.io.IOException
import java.nio.charset.StandardCharsets
import java.sql.Timestamp
import java.time.Instant
import java.util.*
import java.util.concurrent.TimeUnit
import org.apache.commons.csv.CSVFormat
import org.junit.jupiter.api.*
import org.mockito.ArgumentMatchers
import org.mockito.MockedConstruction
import org.mockito.Mockito
import org.mockito.invocation.InvocationOnMock

@Timeout(value = 90, unit = TimeUnit.SECONDS)
internal class S3CsvWriterTest {
    private var s3Client: AmazonS3? = null

    private lateinit var streamTransferManagerMockedConstruction:
        MockedConstruction<StreamTransferManagerWithMetadata>
    private lateinit var streamTransferManagerConstructorArguments:
        MutableList<StreamTransferManagerArguments>
    private lateinit var outputStreams: MutableList<ByteArrayOutputStream>

    @JvmRecord
    private data class StreamTransferManagerArguments(val bucket: String, val `object`: String)

    @BeforeEach
    fun setup() {
        streamTransferManagerConstructorArguments = ArrayList()
        outputStreams = ArrayList()
        // This is basically RETURNS_SELF, except with getMultiPartOutputStreams configured
        // correctly.
        // Other non-void methods (e.g. toString()) will return null.
        streamTransferManagerMockedConstruction =
            Mockito.mockConstruction(StreamTransferManagerWithMetadata::class.java) {
                mock: StreamTransferManagerWithMetadata,
                context: MockedConstruction.Context ->
                // Mockito doesn't seem to provide an easy way to actually retrieve these arguments
                // later on, so
                // manually store them on construction.
                // _PowerMockito_ does, but I didn't want to set up that additional dependency.
                val arguments = context.arguments()
                streamTransferManagerConstructorArguments.add(
                    StreamTransferManagerArguments(arguments[0] as String, arguments[1] as String)
                )

                Mockito.doReturn(mock).`when`(mock).numUploadThreads(ArgumentMatchers.anyInt())
                Mockito.doReturn(mock).`when`(mock).numStreams(ArgumentMatchers.anyInt())
                Mockito.doReturn(mock).`when`(mock).queueCapacity(ArgumentMatchers.anyInt())
                Mockito.doReturn(mock).`when`(mock).partSize(ArgumentMatchers.anyLong())

                // We can't write a fake MultiPartOutputStream, because it doesn't have a public
                // constructor.
                // So instead, we'll build a mock that captures its data into a
                // ByteArrayOutputStream.
                val stream = Mockito.mock(MultiPartOutputStream::class.java)
                Mockito.doReturn(listOf(stream)).`when`(mock).multiPartOutputStreams
                val capturer = ByteArrayOutputStream()
                outputStreams.add(capturer)
                Mockito.doAnswer { invocation: InvocationOnMock ->
                        capturer.write(invocation.getArgument<Any>(0) as Int)
                        null
                    }
                    .`when`<MultiPartOutputStream>(stream)
                    .write(ArgumentMatchers.anyInt())
                Mockito.doAnswer { invocation: InvocationOnMock ->
                        capturer.write(invocation.getArgument<ByteArray>(0))
                        null
                    }
                    .`when`<MultiPartOutputStream>(stream)
                    .write(ArgumentMatchers.any<ByteArray>(ByteArray::class.java))
                Mockito.doAnswer { invocation: InvocationOnMock ->
                        capturer.write(
                            invocation.getArgument(0),
                            invocation.getArgument(1),
                            invocation.getArgument(2)
                        )
                        null
                    }
                    .`when`<MultiPartOutputStream>(stream)
                    .write(
                        ArgumentMatchers.any<ByteArray>(ByteArray::class.java),
                        ArgumentMatchers.anyInt(),
                        ArgumentMatchers.anyInt()
                    )
            }

        s3Client = Mockito.mock(AmazonS3Client::class.java)
    }

    private fun writer(): S3CsvWriter.Builder {
        return S3CsvWriter.Builder(CONFIG, s3Client!!, CONFIGURED_STREAM, UPLOAD_TIME)
            .uploadThreads(UPLOAD_THREADS)
            .queueCapacity(QUEUE_CAPACITY)
    }

    @AfterEach
    fun teardown() {
        streamTransferManagerMockedConstruction!!.close()
    }

    @Test
    @Throws(IOException::class)
    fun generatesCorrectObjectKey_when_created() {
        val writer = writer().build()

        val objectKey = writer.outputPath

        checkObjectName(objectKey)
    }

    @Test
    @Throws(IOException::class)
    fun createsExactlyOneUpload() {
        writer().build()

        Assertions.assertEquals(1, streamTransferManagerMockedConstruction!!.constructed().size)

        val manager: StreamTransferManager =
            streamTransferManagerMockedConstruction!!.constructed()[0]
        val args = streamTransferManagerConstructorArguments!![0]
        Mockito.verify(manager).numUploadThreads(UPLOAD_THREADS)
        Mockito.verify(manager).queueCapacity(QUEUE_CAPACITY)
        Assertions.assertEquals("fake-bucket", args.bucket)
        checkObjectName(args.`object`)
    }

    @Test
    @Throws(Exception::class)
    fun closesS3Upload_when_stagingUploaderClosedSuccessfully() {
        val writer = writer().build()

        writer.close(false)

        val managers = streamTransferManagerMockedConstruction!!.constructed()
        val manager: StreamTransferManager = managers[0]
        Mockito.verify(manager).complete()
    }

    @Test
    @Throws(Exception::class)
    fun closesS3Upload_when_stagingUploaderClosedFailingly() {
        val writer = writer().build()

        writer.close(true)

        val managers = streamTransferManagerMockedConstruction!!.constructed()
        val manager: StreamTransferManager = managers[0]
        Mockito.verify(manager).abort()
    }

    @Test
    @Throws(IOException::class)
    fun writesContentsCorrectly_when_headerEnabled() {
        val writer = writer().build()

        writer.write(
            UUID.fromString("f6767f7d-ce1e-45cc-92db-2ad3dfdd088e"),
            AirbyteRecordMessage()
                .withData(OBJECT_MAPPER.readTree("{\"foo\": 73}"))
                .withEmittedAt(1234L)
        )
        writer.write(
            UUID.fromString("2b95a13f-d54f-4370-a712-1c7bf2716190"),
            AirbyteRecordMessage()
                .withData(OBJECT_MAPPER.readTree("{\"bar\": 84}"))
                .withEmittedAt(2345L)
        )
        writer.close(false)

        // carriage returns are required b/c RFC4180 requires it :(
        Assertions.assertEquals(
            """
        "_airbyte_ab_id","_airbyte_emitted_at","_airbyte_data"
        "f6767f7d-ce1e-45cc-92db-2ad3dfdd088e","1234","{""foo"":73}"
        "2b95a13f-d54f-4370-a712-1c7bf2716190","2345","{""bar"":84}"
        
        """
                .trimIndent()
                .replace("\n", "\r\n"),
            outputStreams!![0].toString(StandardCharsets.UTF_8)
        )
    }

    @Test
    @Throws(IOException::class)
    fun writesContentsCorrectly_when_headerDisabled() {
        val writer = writer().withHeader(false).build()

        writer.write(
            UUID.fromString("f6767f7d-ce1e-45cc-92db-2ad3dfdd088e"),
            AirbyteRecordMessage()
                .withData(OBJECT_MAPPER.readTree("{\"foo\": 73}"))
                .withEmittedAt(1234L)
        )
        writer.write(
            UUID.fromString("2b95a13f-d54f-4370-a712-1c7bf2716190"),
            AirbyteRecordMessage()
                .withData(OBJECT_MAPPER.readTree("{\"bar\": 84}"))
                .withEmittedAt(2345L)
        )
        writer.close(false)

        // carriage returns are required b/c RFC4180 requires it :(
        Assertions.assertEquals(
            """
        "f6767f7d-ce1e-45cc-92db-2ad3dfdd088e","1234","{""foo"":73}"
        "2b95a13f-d54f-4370-a712-1c7bf2716190","2345","{""bar"":84}"
        
        """
                .trimIndent()
                .replace("\n", "\r\n"),
            outputStreams!![0].toString(StandardCharsets.UTF_8)
        )
    }

    /**
     * This test verifies that the S3StreamCopier usecase works. Specifically, the withHeader,
     * csvSettings, and csvSheetGenerator options were all added solely to support S3StreamCopier;
     * we want to verify that it outputs the exact same data as the previous implementation.
     */
    @Test
    @Throws(IOException::class)
    fun writesContentsCorrectly_when_stagingDatabaseConfig() {
        initialize(emptyObject())
        val s3Config =
            create("fake-bucket", "fake-bucketPath", "fake-region")
                .withEndpoint("fake-endpoint")
                .withAccessKeyCredential("fake-access-key-id", "fake-secret-access-key")
                .withFormatConfig(CSV_FORMAT_CONFIG)
                .get()
        val writer =
            S3CsvWriter.Builder(s3Config, s3Client!!, CONFIGURED_STREAM, UPLOAD_TIME)
                .uploadThreads(UPLOAD_THREADS)
                .queueCapacity(QUEUE_CAPACITY)
                .withHeader(false)
                .csvSettings(CSVFormat.DEFAULT)
                .csvSheetGenerator(StagingDatabaseCsvSheetGenerator())
                .build()

        writer.write(
            UUID.fromString("f6767f7d-ce1e-45cc-92db-2ad3dfdd088e"),
            AirbyteRecordMessage()
                .withData(OBJECT_MAPPER.readTree("{\"foo\": 73}"))
                .withEmittedAt(1234L)
        )
        writer.write(
            UUID.fromString("2b95a13f-d54f-4370-a712-1c7bf2716190"),
            AirbyteRecordMessage()
                .withData(OBJECT_MAPPER.readTree("{\"bar\": 84}"))
                .withEmittedAt(2345L)
        )
        writer.close(false)

        // carriage returns are required b/c RFC4180 requires it :(
        // Dynamically generate the timestamp because we generate in local time.
        Assertions.assertEquals(
            """
        f6767f7d-ce1e-45cc-92db-2ad3dfdd088e,"{""foo"":73}",1970-01-01T00:00:01.234Z
        2b95a13f-d54f-4370-a712-1c7bf2716190,"{""bar"":84}",1970-01-01T00:00:02.345Z
        
        """
                .trimIndent()
                .replace("\n", "\r\n"),
            outputStreams!![0].toString(StandardCharsets.UTF_8)
        )
    }

    companion object {
        val CONFIGURED_STREAM: ConfiguredAirbyteStream =
            ConfiguredAirbyteStream()
                .withDestinationSyncMode(DestinationSyncMode.APPEND)
                .withStream(AirbyteStream().withName("fake-stream").withNamespace("fake-namespace"))
        private val OBJECT_MAPPER = ObjectMapper()

        private val CSV_FORMAT_CONFIG =
            UploadCsvFormatConfig(Flattening.NO, CompressionType.NO_COMPRESSION)

        private val CONFIG =
            create("fake-bucket", "fake-bucketPath", "fake-region")
                .withEndpoint("fake-endpoint")
                .withAccessKeyCredential("fake-access-key-id", "fake-secret-access-key")
                .withFormatConfig(CSV_FORMAT_CONFIG)
                .get()

        // equivalent to Thu, 09 Dec 2021 19:17:54 GMT
        private val UPLOAD_TIME: Timestamp = Timestamp.from(Instant.ofEpochMilli(1639077474000L))
        private const val UPLOAD_THREADS = 8
        private const val QUEUE_CAPACITY = 9

        // The full path would be something like
        // "fake-bucketPath/fake-namespace/fake-stream/2021_12_09_1639077474000_e549e712-b89c-4272-9496-9690ba7f973e.csv"
        // 2021_12_09_1639077474000 is generated from the timestamp. It's followed by a random UUID,
        // in case
        // we need to create multiple files.
        private const val EXPECTED_OBJECT_BEGINNING =
            "fake-bucketPath/fake-namespace/fake-stream/2021_12_09_1639077474000_"
        private const val EXPECTED_OBJECT_ENDING = ".csv"

        /**
         * This test really just wants to validate that:
         *
         * * we're dumping into the correct directory (fake-bucketPath/fake_namespace/fake_stream)
         * and that the filename contains the upload time
         * * each S3CsvWriter generates a unique filename suffix (the UUID) so that they don't
         * overwrite each other
         * * we generate a .csv extension
         *
         * So the UUID check isn't strictly necessary.
         *
         * Eventually the output path generator should probably be injected into the S3CsvWriter
         * (and we would test the generator directly + test that the writer calls the generator)
         */
        private fun checkObjectName(objectName: String) {
            val errorMessage = "Object was actually $objectName"

            Assertions.assertTrue(objectName.startsWith(EXPECTED_OBJECT_BEGINNING), errorMessage)
            Assertions.assertTrue(objectName.endsWith(EXPECTED_OBJECT_ENDING), errorMessage)

            // Remove the beginning and ending, which _should_ leave us with just a UUID
            val uuidMaybe =
                objectName // "^" == start of string
                    .replaceFirst(
                        ("^" + EXPECTED_OBJECT_BEGINNING).toRegex(),
                        ""
                    ) // "$" == end of string
                    .replaceFirst((EXPECTED_OBJECT_ENDING + "$").toRegex(), "")
            Assertions.assertDoesNotThrow<UUID>({ UUID.fromString(uuidMaybe) }, errorMessage)
        }
    }
}
