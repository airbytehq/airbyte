package io.airbyte.integrations.destination.snowflake;

import com.azure.storage.blob.specialized.AppendBlobClient;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.StagingFilenameGenerator;
import io.airbyte.integrations.destination.jdbc.copy.StreamCopier;
import io.airbyte.integrations.destination.jdbc.copy.azure.AzureBlobStorageConfig;
import io.airbyte.integrations.destination.jdbc.copy.azure.AzureBlobStorageStreamCopier;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.DestinationSyncMode;
import java.sql.SQLException;
import java.util.UUID;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SnowflakeAzureBlobStorageStreamCopier extends AzureBlobStorageStreamCopier {

  private static final Logger LOGGER = LoggerFactory.getLogger(SnowflakeAzureBlobStorageStreamCopier.class);

  public SnowflakeAzureBlobStorageStreamCopier(String stagingFolder,
      DestinationSyncMode destSyncMode,
      String schema,
      String streamName,
      AppendBlobClient appendBlobClient,
      JdbcDatabase db,
      AzureBlobStorageConfig azureBlobConfig,
      ExtendedNameTransformer nameTransformer,
      SqlOperations sqlOperations,
      StagingFilenameGenerator stagingFilenameGenerator) {
    super(stagingFolder, destSyncMode, schema, streamName, appendBlobClient, db, azureBlobConfig, nameTransformer, sqlOperations);
    this.filenameGenerator = stagingFilenameGenerator;
  }

  @Override
  public void copyAzureBlobCsvFileIntoTable(
      JdbcDatabase database,
      String snowflakeAzureExternalStageName,
      String schema,
      String tableName,
      AzureBlobStorageConfig config
  )
      throws SQLException {

    /*
      Due to the complex, brittle, and all around kludgy behavior to generate a Sas Token for the Blob / Container in question (I tried more than a few different ways)
      this seemed the simplest approach to implement this functionality.
      I believe it has the added benefit of following Snowflake's preferred method (best practice) for managing Azure Blob Integration.
      However, it does feel a little disjointed since the Account Key is still required and used to load data into the Blob. I tried to make up for this in the
      descriptions of the UI fields 'Azure Blob Storage Container Name' and 'Snowflake Azure External Stage'.
    */
//    final var copyQuery = String.format(
//        "COPY INTO %s.%s FROM '@%s/%s' "
//            + "file_format = (type = csv field_delimiter = ',' skip_header = 0 FIELD_OPTIONALLY_ENCLOSED_BY = '\"');",
//        schema,
//        tableName,
//        snowflakeAzureExternalStageName,
//        config
//    );
    LOGGER.error("COPY QUERY WITH SAS: ");
//    database.execute(copyQuery);
//    copy into mytable
//    from 'azure://myaccount.blob.core.windows.net/mycontainer/data/files'
//    credentials=(azure_sas_token='?sv=2016-05-31&ss=b&srt=sco&sp=rwdl&se=2018-06-27T10:05:50Z&st=2017-06-27T02:05:50Z&spr=https,http&sig=bgqQwoXwxzuD2GJfagRg7VOS8hzNr3QLT7rhS8OFRLQ%3D')
//    encryption=(type='AZURE_CSE' master_key = 'kPxX0jzYfIamtnJEUTHwq80Au6NbSgPH5r4BDDwOaO8=')
//    file_format = (format_name = my_csv_format);
//    String token ="?sv=2020-08-04&ss=bfqt&srt=co&sp=rwdlacupitfx&se=2022-02-23T19:23:04Z&st=2022-02-22T11:23:04Z&spr=https,http&sig=uEIQvD3sL804oJmiPRn7Qgu56Qb9LK4pyepfuPVOIK4%3D";
    String bucketPath = generateBucketPath(config);
    final var copyQuery = String.format(
        "COPY INTO %s.%s FROM '%s'"
            + " credentials=(azure_sas_token='%s')"
            + " file_format = (type = csv field_delimiter = ',' skip_header = 0 FIELD_OPTIONALLY_ENCLOSED_BY = '\"') ;",
        schema,
        tableName,
        bucketPath,
        config.getSasToken());
    LOGGER.error("COPY QUERY :"+ copyQuery);

    Exceptions.toRuntime(() -> database.execute(copyQuery));
  }
//               'azure://<account name>.<endpiont domain name>/<container name>' needs to be added to the 'allowed path' of the Storage Integration AND 'azure://<account name>.<endpiont domain name>/<container name>/' needs to be set as the 'url' of the Stage.  See Snowflake details for creating a Storage Integration and External Stage here: https://docs.snowflake.com/en/user-guide/data-load-azure-config.html",

  private String generateBucketPath(AzureBlobStorageConfig config) {
    return "azure://"+config.getAccountName()+"."+config.getEndpointDomainName()+"/"+config.getContainerName()+"/";
  }

}
