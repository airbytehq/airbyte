/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.integrations.destination.snowflake;

import com.azure.storage.common.sas.SasProtocol;
import com.azure.storage.common.sas.SasIpRange;
import com.azure.storage.blob.specialized.AppendBlobClient;
import com.azure.storage.blob.sas.BlobServiceSasSignatureValues;
import com.azure.storage.blob.sas.BlobContainerSasPermission;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.copy.azureblob.AzureBlobConfig;
import io.airbyte.integrations.destination.jdbc.copy.azureblob.AzureBlobStreamCopier;
import io.airbyte.protocol.models.DestinationSyncMode;
import java.sql.SQLException;
import java.time.OffsetDateTime;
import java.time.temporal.ChronoUnit;


public class SnowflakeAzureBlobStreamCopier extends AzureBlobStreamCopier {

  public SnowflakeAzureBlobStreamCopier(String stagingFolder,
                                 DestinationSyncMode destSyncMode,
                                 String schema,
                                 String streamName,
                                 AppendBlobClient appendBlobClient,
                                 JdbcDatabase db,
                                 AzureBlobConfig azureBlobConfig,
                                 ExtendedNameTransformer nameTransformer,
                                 SqlOperations sqlOperations) {
    super(stagingFolder, destSyncMode, schema, streamName, appendBlobClient, db, azureBlobConfig, nameTransformer, sqlOperations);
  }

  @Override
  public void copyAzureBlobCsvFileIntoTable(
    JdbcDatabase database, 
    String snowflakeAzureExternalStageName, 
    String schema, 
    String tableName, 
    AppendBlobClient aappendBlobClient
  )
    throws SQLException {

    /* 
      Due to the complex, brittle, and all around kludgy behavior to generate a Sas Token for the Blob / Container in question (I tried more than a few different ways)
      this seemed the simplest approach to implement this functionality.

      I believe it has the added benefit of following Snowflake's preferred method (best practice) for managing Azure Blob Integration.

      However, it does feel a little disjointed since the Account Key is still required and used to load data into the Blob. I tried to make up for this in the 
      descriptions of the UI fields 'Azure Blob Storage Container Name' and 'Snowflake Azure External Stage'.
    */    
    final var copyQuery = String.format(
        "COPY INTO %s.%s FROM '@%s/%s' "
            + "file_format = (type = csv field_delimiter = ',' skip_header = 0 FIELD_OPTIONALLY_ENCLOSED_BY = '\"');",
        schema,
        tableName,
        snowflakeAzureExternalStageName,
        aappendBlobClient.getBlobName()
    );
    
    database.execute(copyQuery);
  }

}
