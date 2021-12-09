/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.jdbc.copy.s3;

import static java.util.Collections.singletonList;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.anyInt;
import static org.mockito.ArgumentMatchers.anyLong;
import static org.mockito.Mockito.doReturn;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.mockConstruction;
import static org.mockito.Mockito.verify;

import alex.mojaki.s3upload.MultiPartOutputStream;
import alex.mojaki.s3upload.StreamTransferManager;
import com.amazonaws.services.s3.AmazonS3Client;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
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

  private AmazonS3Client s3Client;
  private JdbcDatabase db;
  private SqlOperations sqlOperations;
  private S3StreamCopier copier;

  private MockedConstruction<StreamTransferManager> streamTransferManagerMockedConstruction;
  private List<StreamTransferManagerArguments> streamTransferManagerConstructorArguments;

  // TODO when we're on java 17, this should be a record class
  private static class StreamTransferManagerArguments {

    public final String bucket;
    public final String object;

    public StreamTransferManagerArguments(final String bucket, final String object) {
      this.bucket = bucket;
      this.object = object;
    }
  }

  @BeforeEach
  public void setup() {
    s3Client = mock(AmazonS3Client.class);
    db = mock(JdbcDatabase.class);
    sqlOperations = mock(SqlOperations.class);

    streamTransferManagerConstructorArguments = new ArrayList<>();
    // This is basically RETURNS_SELF, except with getMultiPartOutputStreams configured correctly.
    // Other non-void methods (e.g. toString()) will return null.
    streamTransferManagerMockedConstruction = mockConstruction(
        StreamTransferManager.class,
        (mock, context) -> {
          // Mockito doesn't seem to provide an easy way to actually retrieve these arguments later on, so manually store them on construction.
          // _PowerMockito_ does, but I didn't want to set up that additional dependency.
          final List<?> arguments = context.arguments();
          streamTransferManagerConstructorArguments.add(new StreamTransferManagerArguments((String) arguments.get(0), (String) arguments.get(1)));

          doReturn(mock).when(mock).numUploadThreads(anyInt());
          doReturn(mock).when(mock).numStreams(anyInt());
          doReturn(mock).when(mock).queueCapacity(anyInt());
          doReturn(mock).when(mock).partSize(anyLong());
          doReturn(singletonList(mock(MultiPartOutputStream.class))).when(mock).getMultiPartOutputStreams();
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
        Timestamp.from(Instant.now())
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
    streamTransferManagerMockedConstruction.close();
  }

  @Test
  public void createSequentialStagingFiles_when_multipleFilesRequested() {
    // When we call prepareStagingFile() the first time, it should create exactly one upload manager
    final String firstFile = copier.prepareStagingFile();
    assertTrue(firstFile.startsWith("fake-bucketPath/fake-namespace/fake-stream/"), "Object path was actually " + firstFile);
    assertEquals("fake-bucket", streamTransferManagerConstructorArguments.get(0).bucket);
    assertEquals("arst", streamTransferManagerConstructorArguments.get(0).object);
    final List<StreamTransferManager> firstManagers = streamTransferManagerMockedConstruction.constructed();
    final StreamTransferManager firstManager = firstManagers.get(0);
    verify(firstManager).partSize(PART_SIZE);
    verify(firstManager).numUploadThreads(UPLOAD_THREADS);
    verify(firstManager).queueCapacity(QUEUE_CAPACITY);
    assertEquals(1, firstManagers.size(), "There were actually " + firstManagers.size() + " upload managers");

    // Each file will contain multiple parts, so the first MAX_PARTS_PER_FILE will all go into the same file (i.e. we should not start more uploads)
    // We've already called prepareStagingFile() once, so only go to MAX_PARTS_PER_FILE - 1
    for (var i = 0; i < S3StreamCopier.MAX_PARTS_PER_FILE - 1; i++) {
      final String existingFile = copier.prepareStagingFile();
      assertEquals("fake-staging-folder/fake-schema/fake-stream_00000", existingFile, "preparing file number " + i);
      final int streamManagerCount = streamTransferManagerMockedConstruction.constructed().size();
      assertEquals(1, streamManagerCount, "There were actually " + streamManagerCount + " upload managers");
    }

    // Now that we've hit the MAX_PARTS_PER_FILE, we should start a new upload
    final String secondFile = copier.prepareStagingFile();
    assertEquals("fake-staging-folder/fake-schema/fake-stream_00001", secondFile);
    assertEquals("fake-bucket", streamTransferManagerConstructorArguments.get(1).bucket);
    assertEquals("arst", streamTransferManagerConstructorArguments.get(1).object);
    final List<StreamTransferManager> secondManagers = streamTransferManagerMockedConstruction.constructed();
    final StreamTransferManager secondManager = secondManagers.get(1);
    verify(secondManager).partSize(PART_SIZE);
    verify(secondManager).numUploadThreads(UPLOAD_THREADS);
    verify(secondManager).queueCapacity(QUEUE_CAPACITY);
    assertEquals(2, secondManagers.size(), "There were actually " + secondManagers.size() + " upload managers");
  }

  @Test
  public void closesS3Upload_when_stagingUploaderClosedSuccessfully() throws Exception {
    copier.prepareStagingFile();

    copier.closeStagingUploader(false);

    final List<StreamTransferManager> managers = streamTransferManagerMockedConstruction.constructed();
    final StreamTransferManager manager = managers.get(0);
    verify(manager).complete();
  }

  @Test
  public void closesS3Upload_when_stagingUploaderClosedFailingly() throws Exception {
    copier.prepareStagingFile();

    copier.closeStagingUploader(true);

    final List<StreamTransferManager> managers = streamTransferManagerMockedConstruction.constructed();
    final StreamTransferManager manager = managers.get(0);
    verify(manager).abort();
  }

  @Test
  public void deletesStagingFiles() throws Exception {
    final String file = copier.prepareStagingFile();
    doReturn(true).when(s3Client).doesObjectExist("fake-bucket", file);

    copier.removeFileAndDropTmpTable();

    verify(s3Client).deleteObject("fake-bucket", file);
  }
}
