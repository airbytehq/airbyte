/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import static io.airbyte.integrations.destination.jdbc.copy.gcs.GcsStreamCopier.MAX_PARTS_PER_FILE;
import static org.mockito.Mockito.RETURNS_DEEP_STUBS;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;

import com.azure.storage.blob.specialized.SpecializedBlobClientBuilder;
import com.google.common.collect.Lists;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.StagingFilenameGenerator;
import io.airbyte.integrations.destination.jdbc.copy.azure.AzureBlobStorageConfig;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import java.util.ArrayList;
import java.util.List;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

public class SnowflakeAzureBlobStreamCopierTest {

  private final AzureBlobStorageConfig mockedAzureBlobConfig = new AzureBlobStorageConfig(
      "fake-endpoint",
      "fake-account",
      "fake-container-name",
      "fake-sas-token");

  private JdbcDatabase db;
  private SnowflakeAzureBlobStorageStreamCopier copier;

  @BeforeEach
  public void setup() {
    SpecializedBlobClientBuilder specializedBlobClientBuilder = mock(SpecializedBlobClientBuilder.class, RETURNS_DEEP_STUBS);

    db = mock(JdbcDatabase.class);
    SqlOperations sqlOperations = mock(SqlOperations.class);

    copier = new SnowflakeAzureBlobStorageStreamCopier(
        "fake-staging-folder",
        DestinationSyncMode.OVERWRITE,
        "fake-schema",
        "fake-stream",
        specializedBlobClientBuilder,
        db,
        mockedAzureBlobConfig,
        new ExtendedNameTransformer(),
        sqlOperations,
        new StagingFilenameGenerator("fake-stream", 256L));
  }

  @Test
  public void copiesCorrectFilesToTable() throws Exception {
    for (int i = 0; i < MAX_PARTS_PER_FILE + 1; i++) {
      copier.prepareStagingFile();
    }
    copier.copyStagingFileToTemporaryTable();
    List<List<String>> partition = Lists.partition(new ArrayList<>(copier.getAzureStagingFiles()), 1000);
    for (List<String> files : partition) {
      verify(db).execute(String.format(
          "COPY INTO fake-schema.%s FROM '%s'"
              + " credentials=(azure_sas_token='%s')"
              + " file_format = (type = csv field_delimiter = ',' skip_header = 0 FIELD_OPTIONALLY_ENCLOSED_BY = '\"')"
              + " files = (" + copier.generateFilesList(files) + " );",
          copier.getTmpTableName(),
          copier.generateBucketPath(),
          mockedAzureBlobConfig.getSasToken()));
    }
  }

}
