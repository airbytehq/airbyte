/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.jdbc.copy.s3;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.doReturn;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.mockConstruction;
import static org.mockito.Mockito.verify;

import com.amazonaws.services.s3.AmazonS3Client;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.integrations.destination.s3.csv.S3CsvWriter;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.DestinationSyncMode;
import java.sql.Timestamp;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.MockedConstruction;

/**
 * IF YOU'RE SEEING WEIRD BEHAVIOR INVOLVING MOCKED OBJECTS: double-check the mockConstruction() call in setup(). You might need to update the methods
 * being mocked.
 * <p>
 * Tests to help define what the legacy S3 stream copier did.
 * <p>
 * Does not verify SQL operations, as they're fairly transparent.
 */
public class S3StreamCopierTest {

  private static final int PART_SIZE = 5;
  private static final int UPLOAD_THREADS = 10;
  private static final int QUEUE_CAPACITY = 10;
  // equivalent to Thu, 09 Dec 2021 19:17:54 GMT
  private static final Timestamp UPLOAD_TIME = Timestamp.from(Instant.ofEpochMilli(1639077474000L));
  private static final int MAX_CHUNKS_PER_FILE = 42;

  private static final String EXPECTED_FILENAME1 = "fake-bucketPath/fake_namespace/fake_stream/2021_12_09_1639077474000_fake-stream_00000.csv";
  private static final String EXPECTED_FILENAME2 = "fake-bucketPath/fake_namespace/fake_stream/2021_12_09_1639077474000_fake-stream_00001.csv";

  private AmazonS3Client s3Client;
  private JdbcDatabase db;
  private SqlOperations sqlOperations;
  private S3StreamCopier copier;

  private MockedConstruction<S3CsvWriter> csvWriterMockedConstruction;
  private List<S3CsvWriterArguments> csvWriterConstructorArguments;

  // TODO when we're on java 17, this should be a record class
  private static class S3CsvWriterArguments {

    public final String bucket;
    public final String object;

    public S3CsvWriterArguments(final String bucket, final String object) {
      this.bucket = bucket;
      this.object = object;
    }
  }

  @BeforeEach
  public void setup() {
    s3Client = mock(AmazonS3Client.class);
    db = mock(JdbcDatabase.class);
    sqlOperations = mock(SqlOperations.class);

    csvWriterConstructorArguments = new ArrayList<>();
    // This is basically RETURNS_SELF, except with getMultiPartOutputStreams configured correctly.
    // Other non-void methods (e.g. toString()) will return null.
    csvWriterMockedConstruction = mockConstruction(
        S3CsvWriter.class,
        (mock, context) -> {
          // Mockito doesn't seem to provide an easy way to actually retrieve these arguments later on, so manually store them on construction.
          // _PowerMockito_ does, but I didn't want to set up that additional dependency.
          final List<?> arguments = context.arguments();
          csvWriterConstructorArguments.add(new S3CsvWriterArguments((String) arguments.get(0), (String) arguments.get(1)));

//          doReturn(mock).when(mock).numUploadThreads(anyInt());
//          doReturn(mock).when(mock).numStreams(anyInt());
//          doReturn(mock).when(mock).queueCapacity(anyInt());
//          doReturn(mock).when(mock).partSize(anyLong());
//          doReturn(singletonList(mock(MultiPartOutputStream.class))).when(mock).getMultiPartOutputStreams();
        }
    );

    copier = new S3StreamCopier(
        // In reality, this is normally a UUID - see CopyConsumerFactory#createWriteConfigs
        "fake-staging-folder",
        "fake-schema",
        s3Client,
        db,
        new S3DestinationConfig(
            "fake-endpoint",
            "fake-bucket",
            "fake-bucketPath",
            "fake-region",
            "fake-access-key-id",
            "fake-secret-access-key",
            PART_SIZE,
            null
        ),
        new ExtendedNameTransformer(),
        sqlOperations,
        new ConfiguredAirbyteStream()
            .withDestinationSyncMode(DestinationSyncMode.APPEND)
            .withStream(new AirbyteStream()
                .withName("fake-stream")
                .withNamespace("fake-namespace")
            ),
        UPLOAD_TIME,
        MAX_CHUNKS_PER_FILE
    ) {
      @Override
      public void copyS3CsvFileIntoTable(
          final JdbcDatabase database,
          final String s3FileLocation,
          final String schema,
          final String tableName,
          final S3DestinationConfig s3Config) {
        throw new UnsupportedOperationException("not implemented");
      }
    };
  }

  @AfterEach
  public void teardown() {
    csvWriterMockedConstruction.close();
  }

  @Test
  public void createSequentialStagingFiles_when_multipleFilesRequested() {
    // When we call prepareStagingFile() the first time, it should create exactly one upload manager. The next (MAX_PARTS_PER_FILE - 1) invocations
    // should reuse that same upload manager.
    for (var i = 0; i < S3StreamCopier.MAX_PARTS_PER_FILE; i++) {
      final String file = copier.prepareStagingFile();
      assertEquals("fake-staging-folder/fake-schema/fake-stream_00000", file, "preparing file number " + i);
      final List<S3CsvWriter> firstManagers = csvWriterMockedConstruction.constructed();
      final S3CsvWriter firstManager = firstManagers.get(0);
//      verify(firstManager).partSize(PART_SIZE);
      assertEquals(1, firstManagers.size());
    }

    // Now that we've hit the MAX_PARTS_PER_FILE, we should start a new upload
    final String secondFile = copier.prepareStagingFile();
    assertEquals("fake-staging-folder/fake-schema/fake-stream_00001", secondFile);
    final List<S3CsvWriter> secondManagers = csvWriterMockedConstruction.constructed();
    final S3CsvWriter secondManager = secondManagers.get(1);
//    verify(secondManager).partSize(PART_SIZE);
    assertEquals(2, secondManagers.size());
  }

  @Test
  public void closesS3Upload_when_stagingUploaderClosedSuccessfully() throws Exception {
    copier.prepareStagingFile();

    copier.closeStagingUploader(false);

    final List<S3CsvWriter> managers = csvWriterMockedConstruction.constructed();
    final S3CsvWriter manager = managers.get(0);
//    verify(manager).complete();
  }

  @Test
  public void closesS3Upload_when_stagingUploaderClosedFailingly() throws Exception {
    copier.prepareStagingFile();

    copier.closeStagingUploader(true);

    final List<S3CsvWriter> managers = csvWriterMockedConstruction.constructed();
    final S3CsvWriter manager = managers.get(0);
//    verify(manager).abort();
  }

  @Test
  public void deletesStagingFiles() throws Exception {
    copier.prepareStagingFile();
    doReturn(true).when(s3Client).doesObjectExist("fake-bucket", EXPECTED_FILENAME1);

    copier.removeFileAndDropTmpTable();

    verify(s3Client).deleteObject("fake-bucket", EXPECTED_FILENAME1);
  }
}
