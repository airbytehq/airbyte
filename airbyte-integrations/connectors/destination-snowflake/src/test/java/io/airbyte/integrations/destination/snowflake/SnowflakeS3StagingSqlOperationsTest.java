/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.amazonaws.services.s3.AmazonS3;
import io.airbyte.integrations.destination.s3.NoEncryption;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.integrations.destination.s3.credential.S3AccessKeyCredentialConfig;
import java.util.List;
import org.junit.jupiter.api.Test;

class SnowflakeS3StagingSqlOperationsTest {

  private static final String SCHEMA_NAME = "schemaName";
  private static final String STAGE_PATH = "stagePath/2022/";
  private static final String TABLE_NAME = "tableName";
  private static final String BUCKET_NAME = "bucket_name";

  private final AmazonS3 s3Client = mock(AmazonS3.class);
  private final S3DestinationConfig s3Config = mock(S3DestinationConfig.class);
  private final S3AccessKeyCredentialConfig credentialConfig = mock(S3AccessKeyCredentialConfig.class);

  private final SnowflakeS3StagingSqlOperations snowflakeStagingSqlOperations =
      new SnowflakeS3StagingSqlOperations(new SnowflakeSQLNameTransformer(), s3Client, s3Config, new NoEncryption());

  @Test
  void copyIntoTmpTableFromStage() {
    final String expectedQuery = "COPY INTO " + SCHEMA_NAME + "." + TABLE_NAME + " FROM 's3://" + BUCKET_NAME + "/" + STAGE_PATH + "' " +
        "CREDENTIALS=(aws_key_id='aws_access_key_id' aws_secret_key='aws_secret_access_key') file_format = (type = csv compression = auto " +
        "field_delimiter = ',' skip_header = 0 FIELD_OPTIONALLY_ENCLOSED_BY = '\"') files = ('filename1','filename2');";
    when(s3Config.getBucketName()).thenReturn(BUCKET_NAME);
    when(s3Config.getS3CredentialConfig()).thenReturn(credentialConfig);
    when(credentialConfig.getAccessKeyId()).thenReturn("aws_access_key_id");
    when(credentialConfig.getSecretAccessKey()).thenReturn("aws_secret_access_key");
    final String actualCopyQuery =
        snowflakeStagingSqlOperations.getCopyQuery(STAGE_PATH, List.of("filename1", "filename2"), TABLE_NAME, SCHEMA_NAME);
    assertEquals(expectedQuery, actualCopyQuery);
  }

}
