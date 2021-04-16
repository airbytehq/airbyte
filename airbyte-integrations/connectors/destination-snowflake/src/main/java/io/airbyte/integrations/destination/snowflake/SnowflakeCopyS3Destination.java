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

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.destination.jdbc.AbstractJdbcDestination;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConnectorSpecification;
import java.util.UUID;
import net.snowflake.client.jdbc.internal.amazonaws.auth.AWSStaticCredentialsProvider;
import net.snowflake.client.jdbc.internal.amazonaws.auth.BasicAWSCredentials;
import net.snowflake.client.jdbc.internal.amazonaws.services.s3.AmazonS3;
import net.snowflake.client.jdbc.internal.amazonaws.services.s3.AmazonS3ClientBuilder;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SnowflakeCopyS3Destination implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(SnowflakeCopyS3Destination.class);
  private static final SnowflakeSQLNameTransformer nameTransformer = new SnowflakeSQLNameTransformer();

  @Override
  public AirbyteMessageConsumer getConsumer(JsonNode config, ConfiguredAirbyteCatalog catalog) throws Exception {
    return new SnowflakeCopyS3Consumer(config, catalog);
  }

  @Override
  public ConnectorSpecification spec() throws Exception {
    return AbstractJdbcDestination.getSpec();
  }

  @Override
  public AirbyteConnectionStatus check(JsonNode config) throws Exception {
    // todo: dry
    try {
      final String outputTableName = "_airbyte_connection_test_" + UUID.randomUUID().toString().replaceAll("-", "");
      final S3Config s3Config = new S3Config(config);
      attemptWriteAndDeleteS3Object(s3Config, outputTableName);

      var outputSchema = nameTransformer.convertStreamName(config.get("schema").asText());
      JdbcDatabase database = SnowflakeDatabase.getDatabase(config);
      AbstractJdbcDestination.attemptSQLCreateAndDropTableOperations(outputSchema, database, nameTransformer, new SnowflakeSqlOperations());

      return new AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.SUCCEEDED);
    } catch (Exception e) {
      LOGGER.debug("Exception while checking connection: ", e);
      return new AirbyteConnectionStatus()
          .withStatus(AirbyteConnectionStatus.Status.FAILED)
          .withMessage("Could not connect with provided configuration. \n" + e.getMessage());
    }
  }

  private void attemptWriteAndDeleteS3Object(S3Config s3Config, String outputTableName) {
    var s3 = getAmazonS3(s3Config);
    var s3Bucket = s3Config.bucketName;
    s3.putObject(s3Bucket, outputTableName, "check-content");
    s3.deleteObject(s3Bucket, outputTableName);
  }

  public static AmazonS3 getAmazonS3(S3Config s3Config) {
    var accessKeyId = s3Config.accessKeyId;
    var secretAccessKey = s3Config.secretAccessKey;
    var awsCreds = new BasicAWSCredentials(accessKeyId, secretAccessKey);
    return AmazonS3ClientBuilder.standard()
        .withCredentials(new AWSStaticCredentialsProvider(awsCreds))
        .build();
  }

}
