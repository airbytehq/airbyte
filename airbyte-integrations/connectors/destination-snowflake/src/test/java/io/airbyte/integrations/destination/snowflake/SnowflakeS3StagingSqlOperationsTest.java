/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.amazonaws.services.s3.AmazonS3;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import java.util.List;
import org.junit.jupiter.api.Test;

class SnowflakeS3StagingSqlOperationsTest {

  public static final String SCHEMA_NAME = "schemaName";
  public static final String STAGE_NAME = "stageName";
  private final AmazonS3 s3Client = mock(AmazonS3.class);
  private final S3DestinationConfig s3Config = mock(S3DestinationConfig.class);

  private final SnowflakeS3StagingSqlOperations snowflakeStagingSqlOperations =
      new SnowflakeS3StagingSqlOperations(new SnowflakeSQLNameTransformer(), s3Client, s3Config);

  @Test
  void copyIntoTmpTableFromStage() {
    final String expectedQuery = "COPY INTO schemaName.tableName FROM 's3://bucket_name/stageName' " +
        "CREDENTIALS=(aws_key_id='aws_access_key_id' aws_secret_key='aws_secret_access_key') file_format = (type = csv compression = auto " +
        "field_delimiter = ',' skip_header = 0 FIELD_OPTIONALLY_ENCLOSED_BY = '\"') files = ('filename1','filename2') ;";
    when(s3Config.getBucketName()).thenReturn("bucket_name");
    when(s3Config.getAccessKeyId()).thenReturn("aws_access_key_id");
    when(s3Config.getSecretAccessKey()).thenReturn("aws_secret_access_key");
    final String actualCopyQuery = snowflakeStagingSqlOperations.getCopyQuery(STAGE_NAME, List.of("filename1", "filename2"), "tableName", SCHEMA_NAME);
    assertEquals(expectedQuery, actualCopyQuery);
  }
}
