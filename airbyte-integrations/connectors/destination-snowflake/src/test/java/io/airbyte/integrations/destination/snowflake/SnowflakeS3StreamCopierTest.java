/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import static io.airbyte.integrations.destination.snowflake.SnowflakeS3StreamCopier.MAX_PARTS_PER_FILE;
import static org.mockito.Mockito.RETURNS_DEEP_STUBS;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;

import com.amazonaws.services.s3.AmazonS3Client;
import com.google.common.collect.Lists;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.copy.s3.S3CopyConfig;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.SyncMode;
import java.sql.Timestamp;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Set;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class SnowflakeS3StreamCopierTest {

  // equivalent to Thu, 09 Dec 2021 19:17:54 GMT
  private static final Timestamp UPLOAD_TIME = Timestamp.from(Instant.ofEpochMilli(1639077474000L));

  private AmazonS3Client s3Client;
  private JdbcDatabase db;
  private SqlOperations sqlOperations;
  private SnowflakeS3StreamCopier copier;

  @BeforeEach
  public void setup() throws Exception {
    s3Client = mock(AmazonS3Client.class, RETURNS_DEEP_STUBS);
    db = mock(JdbcDatabase.class);
    sqlOperations = mock(SqlOperations.class);

    final S3DestinationConfig s3Config = S3DestinationConfig.create(
        "fake-bucket",
        "fake-bucketPath",
        "fake-region")
        .withEndpoint("fake-endpoint")
        .withAccessKeyCredential("fake-access-key-id", "fake-secret-access-key")
        .get();

    copier = (SnowflakeS3StreamCopier) new SnowflakeS3StreamCopierFactory().create(
        // In reality, this is normally a UUID - see CopyConsumerFactory#createWriteConfigs
        "fake-staging-folder",
        "fake-schema",
        s3Client,
        db,
        new S3CopyConfig(true, s3Config),
        new ExtendedNameTransformer(),
        sqlOperations,
        new ConfiguredAirbyteStream()
            .withDestinationSyncMode(DestinationSyncMode.APPEND)
            .withStream(new AirbyteStream()
                .withName("fake-stream")
                .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH))
                .withNamespace("fake-namespace")));
  }

  @Test
  public void copiesCorrectFilesToTable() throws Exception {
    // Generate two files
    for (int i = 0; i < MAX_PARTS_PER_FILE + 1; i++) {
      copier.prepareStagingFile();
    }

    copier.copyStagingFileToTemporaryTable();
    final Set<String> stagingFiles = copier.getStagingFiles();
    // check the use of all files for staging
    Assertions.assertTrue(stagingFiles.size() > 1);

    final List<List<String>> partition = Lists.partition(new ArrayList<>(stagingFiles), 1000);
    for (final List<String> files : partition) {
      verify(db).execute(String.format(
          "COPY INTO fake-schema.%s FROM '%s' "
              + "CREDENTIALS=(aws_key_id='fake-access-key-id' aws_secret_key='fake-secret-access-key') "
              + "file_format = (type = csv field_delimiter = ',' skip_header = 0 FIELD_OPTIONALLY_ENCLOSED_BY = '\"') "
              + "files = (" + copier.generateFilesList(files) + " );",
          copier.getTmpTableName(),
          copier.generateBucketPath()));
    }

  }

}
