/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.jdbc.copy.s3;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.doReturn;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.mockConstruction;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;

import com.amazonaws.services.s3.AmazonS3Client;
import com.google.common.collect.Lists;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.integrations.destination.s3.csv.CsvSheetGenerator;
import io.airbyte.integrations.destination.s3.csv.S3CsvFormatConfig;
import io.airbyte.integrations.destination.s3.csv.S3CsvWriter;
import io.airbyte.integrations.destination.s3.csv.StagingDatabaseCsvSheetGenerator;
import io.airbyte.integrations.destination.s3.util.CompressionType;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.SyncMode;
import java.sql.Timestamp;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import org.apache.commons.csv.CSVFormat;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.MockedConstruction;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class S3StreamCopierTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(S3StreamCopierTest.class);

  private static final S3DestinationConfig S3_CONFIG = S3DestinationConfig.create(
      "fake-bucket",
      "fake-bucketPath",
      "fake-region")
      .withEndpoint("fake-endpoint")
      .withAccessKeyCredential("fake-access-key-id", "fake-secret-access-key")
      .get();
  private static final ConfiguredAirbyteStream CONFIGURED_STREAM = new ConfiguredAirbyteStream()
      .withDestinationSyncMode(DestinationSyncMode.APPEND)
      .withStream(new AirbyteStream()
          .withName("fake-stream")
          .withNamespace("fake-namespace")
          .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH)));
  private static final int UPLOAD_THREADS = 10;
  private static final int QUEUE_CAPACITY = 10;
  // equivalent to Thu, 09 Dec 2021 19:17:54 GMT
  private static final Timestamp UPLOAD_TIME = Timestamp.from(Instant.ofEpochMilli(1639077474000L));
  private static final int MAX_PARTS_PER_FILE = 42;

  private AmazonS3Client s3Client;
  private JdbcDatabase db;
  private SqlOperations sqlOperations;
  private S3StreamCopier copier;

  private MockedConstruction<S3CsvWriter> csvWriterMockedConstruction;
  private List<S3CsvWriterArguments> csvWriterConstructorArguments;

  private List<CopyArguments> copyArguments;

  private record S3CsvWriterArguments(S3DestinationConfig config,
                                      ConfiguredAirbyteStream stream,
                                      Timestamp uploadTime,
                                      int uploadThreads,
                                      int queueCapacity,
                                      boolean writeHeader,
                                      CSVFormat csvSettings,
                                      CsvSheetGenerator csvSheetGenerator) {

  }

  private record CopyArguments(JdbcDatabase database,
                               String s3FileLocation,
                               String schema,
                               String tableName,
                               S3DestinationConfig s3Config) {

  }

  @BeforeEach
  public void setup() {
    s3Client = mock(AmazonS3Client.class);
    db = mock(JdbcDatabase.class);
    sqlOperations = mock(SqlOperations.class);

    csvWriterConstructorArguments = new ArrayList<>();
    copyArguments = new ArrayList<>();

    // This is basically RETURNS_SELF, except with getMultiPartOutputStreams configured correctly.
    // Other non-void methods (e.g. toString()) will return null.
    csvWriterMockedConstruction = mockConstruction(
        S3CsvWriter.class,
        (mock, context) -> {
          // Normally, the S3CsvWriter would return a path that ends in a UUID, but this mock will generate an
          // int ID to make our asserts easier.
          doReturn(String.format("fakeOutputPath-%05d", csvWriterConstructorArguments.size())).when(mock).getOutputPath();

          // Mockito doesn't seem to provide an easy way to actually retrieve these arguments later on, so
          // manually store them on construction.
          // _PowerMockito_ does, but I didn't want to set up that additional dependency.
          final List<?> arguments = context.arguments();
          csvWriterConstructorArguments.add(new S3CsvWriterArguments(
              (S3DestinationConfig) arguments.get(0),
              (ConfiguredAirbyteStream) arguments.get(2),
              (Timestamp) arguments.get(3),
              (int) arguments.get(4),
              (int) arguments.get(5),
              (boolean) arguments.get(6),
              (CSVFormat) arguments.get(7),
              (CsvSheetGenerator) arguments.get(8)));
        });

    copier = new S3StreamCopier(
        // In reality, this is normally a UUID - see CopyConsumerFactory#createWriteConfigs
        "fake-staging-folder",
        "fake-schema",
        s3Client,
        db,
        new S3CopyConfig(true, S3_CONFIG),
        new ExtendedNameTransformer(),
        sqlOperations,
        CONFIGURED_STREAM,
        UPLOAD_TIME,
        MAX_PARTS_PER_FILE) {

      @Override
      public void copyS3CsvFileIntoTable(
                                         final JdbcDatabase database,
                                         final String s3FileLocation,
                                         final String schema,
                                         final String tableName,
                                         final S3DestinationConfig s3Config) {
        copyArguments.add(new CopyArguments(database, s3FileLocation, schema, tableName, s3Config));
      }

    };
  }

  @AfterEach
  public void teardown() {
    csvWriterMockedConstruction.close();
  }

  @Test
  public void createSequentialStagingFiles_when_multipleFilesRequested() {
    // When we call prepareStagingFile() the first time, it should create exactly one S3CsvWriter. The
    // next (MAX_PARTS_PER_FILE - 1) invocations
    // should reuse that same writer.
    for (var i = 0; i < MAX_PARTS_PER_FILE; i++) {
      final String file = copier.prepareStagingFile();
      assertEquals("fakeOutputPath-00000", file, "preparing file number " + i);
      assertEquals(1, csvWriterMockedConstruction.constructed().size());
      checkCsvWriterArgs(csvWriterConstructorArguments.get(0));
    }

    // Now that we've hit the MAX_PARTS_PER_FILE, we should start a new writer
    final String secondFile = copier.prepareStagingFile();
    assertEquals("fakeOutputPath-00001", secondFile);
    final List<S3CsvWriter> secondManagers = csvWriterMockedConstruction.constructed();
    assertEquals(2, secondManagers.size());
    checkCsvWriterArgs(csvWriterConstructorArguments.get(1));
  }

  private void checkCsvWriterArgs(final S3CsvWriterArguments args) {
    final S3DestinationConfig s3Config = S3DestinationConfig.create(S3_CONFIG)
        .withFormatConfig(new S3CsvFormatConfig(null, CompressionType.NO_COMPRESSION))
        .get();
    assertEquals(s3Config, args.config);
    assertEquals(CONFIGURED_STREAM, args.stream);
    assertEquals(UPLOAD_TIME, args.uploadTime);
    assertEquals(UPLOAD_THREADS, args.uploadThreads);
    assertEquals(QUEUE_CAPACITY, args.queueCapacity);
    assertFalse(args.writeHeader);
    assertEquals(CSVFormat.DEFAULT, args.csvSettings);
    assertTrue(
        args.csvSheetGenerator instanceof StagingDatabaseCsvSheetGenerator,
        "Sheet generator was actually a " + args.csvSheetGenerator.getClass());
  }

  @Test
  public void closesS3Upload_when_stagingUploaderClosedSuccessfully() throws Exception {
    copier.prepareStagingFile();

    copier.closeStagingUploader(false);

    final List<S3CsvWriter> managers = csvWriterMockedConstruction.constructed();
    final S3CsvWriter manager = managers.get(0);
    verify(manager).close(false);
  }

  @Test
  public void closesS3Upload_when_stagingUploaderClosedFailingly() throws Exception {
    copier.prepareStagingFile();

    copier.closeStagingUploader(true);

    final List<S3CsvWriter> managers = csvWriterMockedConstruction.constructed();
    final S3CsvWriter manager = managers.get(0);
    verify(manager).close(true);
  }

  @Test
  public void deletesStagingFiles() throws Exception {
    copier.prepareStagingFile();
    doReturn(true).when(s3Client).doesObjectExist("fake-bucket", "fakeOutputPath-00000");

    copier.removeFileAndDropTmpTable();

    verify(s3Client).deleteObject("fake-bucket", "fakeOutputPath-00000");
  }

  @Test
  public void doesNotDeleteStagingFiles_if_purgeStagingDataDisabled() throws Exception {
    copier = new S3StreamCopier(
        "fake-staging-folder",
        "fake-schema",
        s3Client,
        db,
        // Explicitly disable purgeStagingData
        new S3CopyConfig(false, S3_CONFIG),
        new ExtendedNameTransformer(),
        sqlOperations,
        CONFIGURED_STREAM,
        UPLOAD_TIME,
        MAX_PARTS_PER_FILE) {

      @Override
      public void copyS3CsvFileIntoTable(
                                         final JdbcDatabase database,
                                         final String s3FileLocation,
                                         final String schema,
                                         final String tableName,
                                         final S3DestinationConfig s3Config) {
        copyArguments.add(new CopyArguments(database, s3FileLocation, schema, tableName, s3Config));
      }

    };

    copier.prepareStagingFile();
    doReturn(true).when(s3Client).doesObjectExist("fake-bucket", "fakeOutputPath-00000");

    copier.removeFileAndDropTmpTable();

    verify(s3Client, never()).deleteObject("fake-bucket", "fakeOutputPath-00000");
  }

  @Test
  public void copiesCorrectFilesToTable() throws Exception {
    // Generate two files
    for (int i = 0; i < MAX_PARTS_PER_FILE + 1; i++) {
      copier.prepareStagingFile();
    }

    copier.copyStagingFileToTemporaryTable();

    assertEquals(2, copyArguments.size(), "Number of invocations was actually " + copyArguments.size() + ". Arguments were " + copyArguments);

    // S3StreamCopier operates on these from a HashMap, so need to sort them in order to assert in a
    // sane way.
    final List<CopyArguments> sortedArgs = copyArguments.stream().sorted(Comparator.comparing(arg -> arg.s3FileLocation)).toList();
    for (int i = 0; i < sortedArgs.size(); i++) {
      LOGGER.info("Checking arguments for index {}", i);
      final CopyArguments args = sortedArgs.get(i);
      assertEquals(String.format("s3://fake-bucket/fakeOutputPath-%05d", i), args.s3FileLocation);
      assertEquals("fake-schema", args.schema);
      assertTrue(args.tableName.endsWith("fake_stream"), "Table name was actually " + args.tableName);
    }
  }

}
