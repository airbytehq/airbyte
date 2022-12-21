/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.csv;

import static java.util.Collections.singletonList;
import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyInt;
import static org.mockito.ArgumentMatchers.anyLong;
import static org.mockito.Mockito.doAnswer;
import static org.mockito.Mockito.doReturn;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.mockConstruction;
import static org.mockito.Mockito.verify;

import alex.mojaki.s3upload.MultiPartOutputStream;
import alex.mojaki.s3upload.StreamTransferManager;
import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.AmazonS3Client;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.integrations.destination.s3.csv.S3CsvFormatConfig.Flattening;
import io.airbyte.integrations.destination.s3.csv.S3CsvWriter.Builder;
import io.airbyte.integrations.destination.s3.util.CompressionType;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.sql.Timestamp;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import org.apache.commons.csv.CSVFormat;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.MockedConstruction;

class S3CsvWriterTest {

  public static final ConfiguredAirbyteStream CONFIGURED_STREAM = new ConfiguredAirbyteStream()
      .withDestinationSyncMode(DestinationSyncMode.APPEND)
      .withStream(new AirbyteStream()
          .withName("fake-stream")
          .withNamespace("fake-namespace"));
  private static final ObjectMapper OBJECT_MAPPER = new ObjectMapper();

  private static final S3CsvFormatConfig CSV_FORMAT_CONFIG = new S3CsvFormatConfig(Flattening.NO, CompressionType.NO_COMPRESSION);

  private static final S3DestinationConfig CONFIG = S3DestinationConfig.create(
      "fake-bucket",
      "fake-bucketPath",
      "fake-region")
      .withEndpoint("fake-endpoint")
      .withAccessKeyCredential("fake-access-key-id", "fake-secret-access-key")
      .withFormatConfig(CSV_FORMAT_CONFIG)
      .get();

  // equivalent to Thu, 09 Dec 2021 19:17:54 GMT
  private static final Timestamp UPLOAD_TIME = Timestamp.from(Instant.ofEpochMilli(1639077474000L));
  private static final int UPLOAD_THREADS = 8;
  private static final int QUEUE_CAPACITY = 9;

  // The full path would be something like
  // "fake-bucketPath/fake-namespace/fake-stream/2021_12_09_1639077474000_e549e712-b89c-4272-9496-9690ba7f973e.csv"
  // 2021_12_09_1639077474000 is generated from the timestamp. It's followed by a random UUID, in case
  // we need to create multiple files.
  private static final String EXPECTED_OBJECT_BEGINNING = "fake-bucketPath/fake-namespace/fake-stream/2021_12_09_1639077474000_";
  private static final String EXPECTED_OBJECT_ENDING = ".csv";

  private AmazonS3 s3Client;

  private MockedConstruction<StreamTransferManager> streamTransferManagerMockedConstruction;
  private List<StreamTransferManagerArguments> streamTransferManagerConstructorArguments;
  private List<ByteArrayOutputStream> outputStreams;

  private record StreamTransferManagerArguments(String bucket, String object) {

  }

  @BeforeEach
  public void setup() {
    streamTransferManagerConstructorArguments = new ArrayList<>();
    outputStreams = new ArrayList<>();
    // This is basically RETURNS_SELF, except with getMultiPartOutputStreams configured correctly.
    // Other non-void methods (e.g. toString()) will return null.
    streamTransferManagerMockedConstruction = mockConstruction(
        StreamTransferManager.class,
        (mock, context) -> {
          // Mockito doesn't seem to provide an easy way to actually retrieve these arguments later on, so
          // manually store them on construction.
          // _PowerMockito_ does, but I didn't want to set up that additional dependency.
          final List<?> arguments = context.arguments();
          streamTransferManagerConstructorArguments.add(new StreamTransferManagerArguments((String) arguments.get(0), (String) arguments.get(1)));

          doReturn(mock).when(mock).numUploadThreads(anyInt());
          doReturn(mock).when(mock).numStreams(anyInt());
          doReturn(mock).when(mock).queueCapacity(anyInt());
          doReturn(mock).when(mock).partSize(anyLong());

          // We can't write a fake MultiPartOutputStream, because it doesn't have a public constructor.
          // So instead, we'll build a mock that captures its data into a ByteArrayOutputStream.
          final MultiPartOutputStream stream = mock(MultiPartOutputStream.class);
          doReturn(singletonList(stream)).when(mock).getMultiPartOutputStreams();
          final ByteArrayOutputStream capturer = new ByteArrayOutputStream();
          outputStreams.add(capturer);
          doAnswer(invocation -> {
            capturer.write((int) invocation.getArgument(0));
            return null;
          }).when(stream).write(anyInt());
          doAnswer(invocation -> {
            capturer.write(invocation.getArgument(0));
            return null;
          }).when(stream).write(any(byte[].class));
          doAnswer(invocation -> {
            capturer.write(invocation.getArgument(0), invocation.getArgument(1), invocation.getArgument(2));
            return null;
          }).when(stream).write(any(byte[].class), anyInt(), anyInt());
        });

    s3Client = mock(AmazonS3Client.class);
  }

  private Builder writer() {
    return new Builder(
        CONFIG,
        s3Client,
        CONFIGURED_STREAM,
        UPLOAD_TIME).uploadThreads(UPLOAD_THREADS)
            .queueCapacity(QUEUE_CAPACITY);
  }

  @AfterEach
  public void teardown() {
    streamTransferManagerMockedConstruction.close();
  }

  @Test
  public void generatesCorrectObjectKey_when_created() throws IOException {
    final S3CsvWriter writer = writer().build();

    final String objectKey = writer.getOutputPath();

    checkObjectName(objectKey);
  }

  @Test
  public void createsExactlyOneUpload() throws IOException {
    writer().build();

    assertEquals(1, streamTransferManagerMockedConstruction.constructed().size());

    final StreamTransferManager manager = streamTransferManagerMockedConstruction.constructed().get(0);
    final StreamTransferManagerArguments args = streamTransferManagerConstructorArguments.get(0);
    verify(manager).numUploadThreads(UPLOAD_THREADS);
    verify(manager).queueCapacity(QUEUE_CAPACITY);
    assertEquals("fake-bucket", args.bucket);
    checkObjectName(args.object);
  }

  @Test
  public void closesS3Upload_when_stagingUploaderClosedSuccessfully() throws Exception {
    final S3CsvWriter writer = writer().build();

    writer.close(false);

    final List<StreamTransferManager> managers = streamTransferManagerMockedConstruction.constructed();
    final StreamTransferManager manager = managers.get(0);
    verify(manager).complete();
  }

  @Test
  public void closesS3Upload_when_stagingUploaderClosedFailingly() throws Exception {
    final S3CsvWriter writer = writer().build();

    writer.close(true);

    final List<StreamTransferManager> managers = streamTransferManagerMockedConstruction.constructed();
    final StreamTransferManager manager = managers.get(0);
    verify(manager).abort();
  }

  @Test
  public void writesContentsCorrectly_when_headerEnabled() throws IOException {
    final S3CsvWriter writer = writer().build();

    writer.write(
        UUID.fromString("f6767f7d-ce1e-45cc-92db-2ad3dfdd088e"),
        new AirbyteRecordMessage()
            .withData(OBJECT_MAPPER.readTree("{\"foo\": 73}"))
            .withEmittedAt(1234L));
    writer.write(
        UUID.fromString("2b95a13f-d54f-4370-a712-1c7bf2716190"),
        new AirbyteRecordMessage()
            .withData(OBJECT_MAPPER.readTree("{\"bar\": 84}"))
            .withEmittedAt(2345L));
    writer.close(false);

    // carriage returns are required b/c RFC4180 requires it :(
    assertEquals(
        """
        "_airbyte_ab_id","_airbyte_emitted_at","_airbyte_data"\r
        "f6767f7d-ce1e-45cc-92db-2ad3dfdd088e","1234","{""foo"":73}"\r
        "2b95a13f-d54f-4370-a712-1c7bf2716190","2345","{""bar"":84}"\r
        """,
        outputStreams.get(0).toString(StandardCharsets.UTF_8));
  }

  @Test
  public void writesContentsCorrectly_when_headerDisabled() throws IOException {
    final S3CsvWriter writer = writer().withHeader(false).build();

    writer.write(
        UUID.fromString("f6767f7d-ce1e-45cc-92db-2ad3dfdd088e"),
        new AirbyteRecordMessage()
            .withData(OBJECT_MAPPER.readTree("{\"foo\": 73}"))
            .withEmittedAt(1234L));
    writer.write(
        UUID.fromString("2b95a13f-d54f-4370-a712-1c7bf2716190"),
        new AirbyteRecordMessage()
            .withData(OBJECT_MAPPER.readTree("{\"bar\": 84}"))
            .withEmittedAt(2345L));
    writer.close(false);

    // carriage returns are required b/c RFC4180 requires it :(
    assertEquals(
        """
        "f6767f7d-ce1e-45cc-92db-2ad3dfdd088e","1234","{""foo"":73}"\r
        "2b95a13f-d54f-4370-a712-1c7bf2716190","2345","{""bar"":84}"\r
        """,
        outputStreams.get(0).toString(StandardCharsets.UTF_8));
  }

  /**
   * This test verifies that the S3StreamCopier usecase works. Specifically, the withHeader,
   * csvSettings, and csvSheetGenerator options were all added solely to support S3StreamCopier; we
   * want to verify that it outputs the exact same data as the previous implementation.
   */
  @Test
  public void writesContentsCorrectly_when_stagingDatabaseConfig() throws IOException {
    final S3DestinationConfig s3Config = S3DestinationConfig.create(
        "fake-bucket",
        "fake-bucketPath",
        "fake-region")
        .withEndpoint("fake-endpoint")
        .withAccessKeyCredential("fake-access-key-id", "fake-secret-access-key")
        .withFormatConfig(CSV_FORMAT_CONFIG)
        .get();
    final S3CsvWriter writer = new Builder(
        s3Config,
        s3Client,
        CONFIGURED_STREAM,
        UPLOAD_TIME).uploadThreads(UPLOAD_THREADS)
            .queueCapacity(QUEUE_CAPACITY)
            .withHeader(false)
            .csvSettings(CSVFormat.DEFAULT)
            .csvSheetGenerator(new StagingDatabaseCsvSheetGenerator())
            .build();

    writer.write(
        UUID.fromString("f6767f7d-ce1e-45cc-92db-2ad3dfdd088e"),
        new AirbyteRecordMessage()
            .withData(OBJECT_MAPPER.readTree("{\"foo\": 73}"))
            .withEmittedAt(1234L));
    writer.write(
        UUID.fromString("2b95a13f-d54f-4370-a712-1c7bf2716190"),
        new AirbyteRecordMessage()
            .withData(OBJECT_MAPPER.readTree("{\"bar\": 84}"))
            .withEmittedAt(2345L));
    writer.close(false);

    // carriage returns are required b/c RFC4180 requires it :(
    // Dynamically generate the timestamp because we generate in local time.
    assertEquals(
        String.format(
            """
            f6767f7d-ce1e-45cc-92db-2ad3dfdd088e,"{""foo"":73}",%s\r
            2b95a13f-d54f-4370-a712-1c7bf2716190,"{""bar"":84}",%s\r
            """,
            Timestamp.from(Instant.ofEpochMilli(1234)),
            Timestamp.from(Instant.ofEpochMilli(2345))),
        outputStreams.get(0).toString(StandardCharsets.UTF_8));
  }

  /**
   * This test really just wants to validate that:
   * <ul>
   * <li>we're dumping into the correct directory (fake-bucketPath/fake_namespace/fake_stream) and
   * that the filename contains the upload time</li>
   * <li>each S3CsvWriter generates a unique filename suffix (the UUID) so that they don't overwrite
   * each other</li>
   * <li>we generate a .csv extension</li>
   * </ul>
   * So the UUID check isn't strictly necessary.
   * <p>
   * Eventually the output path generator should probably be injected into the S3CsvWriter (and we
   * would test the generator directly + test that the writer calls the generator)
   */
  private static void checkObjectName(final String objectName) {
    final String errorMessage = "Object was actually " + objectName;

    assertTrue(objectName.startsWith(EXPECTED_OBJECT_BEGINNING), errorMessage);
    assertTrue(objectName.endsWith(EXPECTED_OBJECT_ENDING), errorMessage);

    // Remove the beginning and ending, which _should_ leave us with just a UUID
    final String uuidMaybe = objectName
        // "^" == start of string
        .replaceFirst("^" + EXPECTED_OBJECT_BEGINNING, "")
        // "$" == end of string
        .replaceFirst(EXPECTED_OBJECT_ENDING + "$", "");
    assertDoesNotThrow(() -> UUID.fromString(uuidMaybe), errorMessage);
  }

}
