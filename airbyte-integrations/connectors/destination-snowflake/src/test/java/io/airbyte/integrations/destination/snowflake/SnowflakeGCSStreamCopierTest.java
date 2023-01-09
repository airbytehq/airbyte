/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import static io.airbyte.integrations.destination.snowflake.SnowflakeS3StreamCopier.MAX_PARTS_PER_FILE;
import static org.mockito.Mockito.RETURNS_DEEP_STUBS;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;

import com.google.cloud.storage.Storage;
import com.google.common.collect.Lists;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.copy.gcs.GcsConfig;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import java.util.ArrayList;
import java.util.List;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

public class SnowflakeGCSStreamCopierTest {

  private JdbcDatabase db;
  private SnowflakeGcsStreamCopier copier;

  @BeforeEach
  public void setup() throws Exception {
    Storage storageClient = mock(Storage.class, RETURNS_DEEP_STUBS);
    db = mock(JdbcDatabase.class);
    SqlOperations sqlOperations = mock(SqlOperations.class);

    copier = (SnowflakeGcsStreamCopier) new SnowflakeGcsStreamCopierFactory().create(
        "fake-staging-folder",
        DestinationSyncMode.OVERWRITE,
        "fake-schema",
        "fake-stream",
        storageClient,
        db,
        new GcsConfig("fake-project-id", "fake-bucket-name", "fake-credentials"),
        new ExtendedNameTransformer(),
        sqlOperations);
  }

  @Test
  public void copiesCorrectFilesToTable() throws Exception {
    for (int i = 0; i < MAX_PARTS_PER_FILE + 1; i++) {
      copier.prepareStagingFile();
    }

    copier.copyStagingFileToTemporaryTable();
    final List<List<String>> partition = Lists.partition(new ArrayList<>(copier.getGcsStagingFiles()), 1000);
    for (final List<String> files : partition) {
      verify(db).execute(String.format(
          "COPY INTO fake-schema.%s FROM '%s' storage_integration = gcs_airbyte_integration "
              + " file_format = (type = csv field_delimiter = ',' skip_header = 0 FIELD_OPTIONALLY_ENCLOSED_BY = '\"') "
              + "files = (" + copier.generateFilesList(files) + " );",
          copier.getTmpTableName(),
          copier.generateBucketPath()));
    }

  }

}
