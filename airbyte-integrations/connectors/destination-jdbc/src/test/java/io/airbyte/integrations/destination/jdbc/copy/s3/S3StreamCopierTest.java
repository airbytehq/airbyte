/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.jdbc.copy.s3;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.RETURNS_DEEP_STUBS;
import static org.mockito.Mockito.clearInvocations;
import static org.mockito.Mockito.doReturn;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;

import com.amazonaws.services.s3.AmazonS3Client;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.DestinationSyncMode;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.platform.commons.util.ExceptionUtils;

/**
 * Somewhat sketchily verifies what the AmazonS3Client does, even though the stream copier only actually interacts with it via StreamTransferManager
 * instances. The interactions are mostly obvious enough that this feels fine.
 */
public class S3StreamCopierTest {

  private AmazonS3Client s3Client;
  private JdbcDatabase db;
  private SqlOperations sqlOperations;
  private S3StreamCopier copier;

  @BeforeEach
  public void setup() {
    s3Client = mock(AmazonS3Client.class, RETURNS_DEEP_STUBS);
    db = mock(JdbcDatabase.class);
    sqlOperations = mock(SqlOperations.class);

    copier = new S3StreamCopier(
        "fake-staging-folder",
        DestinationSyncMode.OVERWRITE,
        "fake-schema",
        "fake-stream",
        s3Client,
        db,
        new S3DestinationConfig(
            "fake-endpoint",
            "fake-bucket",
            null,
            "fake-region",
            "fake-access-key-id",
            "fake-secret-access-key",
            null
        ),
        new ExtendedNameTransformer(),
        sqlOperations
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

  @Test
  public void createSequentialStagingFiles_when_multipleFilesRequested() {
    // Each file will contain multiple parts, so the first MAX_PARTS_PER_FILE will all go into the same file
    for (var i = 0; i < S3StreamCopier.MAX_PARTS_PER_FILE; i++) {
      final String file1 = copier.prepareStagingFile();
      assertEquals("fake-staging-folder/fake-schema/fake-stream_00000", file1, "preparing file number " + i);
    }
    verify(s3Client).initiateMultipartUpload(any());
    clearInvocations(s3Client);

    final String file2 = copier.prepareStagingFile();
    assertEquals("fake-staging-folder/fake-schema/fake-stream_00001", file2);
    verify(s3Client).initiateMultipartUpload(any());
  }

  @Test
  public void closesS3Upload_when_stagingUploaderClosedSuccessfully() throws Exception {
    final String file = copier.prepareStagingFile();
    copier.write(UUID.randomUUID(), new AirbyteRecordMessage().withEmittedAt(84L), file);

    copier.closeStagingUploader(false);

    verify(s3Client).completeMultipartUpload(any());
  }

  @Test
  public void closesS3Upload_when_stagingUploaderClosedFailingly() throws Exception {
    final String file = copier.prepareStagingFile();
    copier.write(UUID.randomUUID(), new AirbyteRecordMessage().withEmittedAt(84L), file);

    // TODO why does this throw an interruptedexception
    final RuntimeException exception = assertThrows(RuntimeException.class, () -> copier.closeStagingUploader(true));

    // the wrapping chain is RuntimeException -> ExecutionException -> RuntimeException -> InterruptedException
    assertEquals(InterruptedException.class, exception.getCause().getCause().getCause().getClass(), "Original exception: " + ExceptionUtils.readStackTrace(exception));
  }

  @Test
  public void deletesStagingFiles() throws Exception {
    final String file = copier.prepareStagingFile();
    doReturn(true).when(s3Client).doesObjectExist("fake-bucket", file);

    copier.removeFileAndDropTmpTable();

    verify(s3Client).deleteObject("fake-bucket", file);
  }
}
