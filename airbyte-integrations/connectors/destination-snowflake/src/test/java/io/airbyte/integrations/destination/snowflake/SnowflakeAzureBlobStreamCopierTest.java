/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import static io.airbyte.integrations.destination.jdbc.copy.gcs.GcsStreamCopier.MAX_PARTS_PER_FILE;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;

import com.azure.storage.blob.specialized.SpecializedBlobClientBuilder;
import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Lists;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.StagingFilenameGenerator;
import io.airbyte.integrations.destination.jdbc.copy.azure.AzureBlobStorageConfig;
import io.airbyte.protocol.models.DestinationSyncMode;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

public class SnowflakeAzureBlobStreamCopierTest {

  private JdbcDatabase db;
  private SnowflakeAzureBlobStorageStreamCopier copier;
  private AzureBlobStorageConfig azureBlobConfig;

  @BeforeEach
  public void setup() {
    final JsonNode copyConfig = Jsons.deserialize(IOs.readFile(Path.of("secrets/copy_azure_blob_config.json")));
    JsonNode config = copyConfig.get("loading_method");
    azureBlobConfig = AzureBlobStorageConfig.getAzureBlobConfig(config);
    final SpecializedBlobClientBuilder specializedBlobClientBuilder = new SpecializedBlobClientBuilder()
        .endpoint(azureBlobConfig.getEndpointUrl())
        .sasToken(azureBlobConfig.getSasToken())
        .containerName(azureBlobConfig.getContainerName());

    db = mock(JdbcDatabase.class);
    SqlOperations sqlOperations = mock(SqlOperations.class);

    copier = new SnowflakeAzureBlobStorageStreamCopier(
        "fake-staging-folder",
        DestinationSyncMode.OVERWRITE,
        "fake-schema",
        "fake-stream",
        specializedBlobClientBuilder,
        db,
        new AzureBlobStorageConfig(azureBlobConfig.getEndpointDomainName(), azureBlobConfig.getAccountName(), azureBlobConfig.getContainerName(),
            azureBlobConfig.getSasToken()),
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
          azureBlobConfig.getSasToken()));
    }
  }

}
