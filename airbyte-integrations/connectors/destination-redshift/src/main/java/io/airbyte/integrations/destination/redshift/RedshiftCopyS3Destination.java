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

package io.airbyte.integrations.destination.redshift;

import com.amazonaws.auth.AWSStaticCredentialsProvider;
import com.amazonaws.auth.BasicAWSCredentials;
import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.AmazonS3ClientBuilder;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Databases;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.FailureTrackingAirbyteMessageConsumer;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.jdbc.AbstractJdbcDestination;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.copy.Copier;
import io.airbyte.integrations.destination.jdbc.copy.CopyConsumer;
import io.airbyte.integrations.destination.jdbc.copy.CopyDestination;
import io.airbyte.integrations.destination.jdbc.copy.s3.S3Config;
import io.airbyte.integrations.destination.jdbc.copy.s3.S3Copier;
import io.airbyte.integrations.destination.jdbc.copy.s3.S3CopierSupplier;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

import io.airbyte.protocol.models.DestinationSyncMode;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * A more efficient Redshift Destination than the sql-based {@link RedshiftDestination}. Instead of
 * inserting data as batched SQL INSERTs, we follow Redshift best practices and, 1) Stream the data
 * to S3. One compressed file is created per table. 2) Copy the S3 file to Redshift. See
 * https://docs.aws.amazon.com/redshift/latest/dg/c_best-practices-use-copy.html for more info.
 *
 * Although Redshift recommends splitting the file for more efficient copying, this introduces
 * complexity around file partitioning that should be handled by a file destination connector. The
 * single file approach is orders of magnitude faster than batch inserting and 'good-enough' for
 * now.
 */
public class RedshiftCopyS3Destination extends CopyDestination {

  public AirbyteMessageConsumer getConsumer(JsonNode config, ConfiguredAirbyteCatalog catalog) throws Exception {
    return new CopyConsumer(getConfiguredSchema(config), getS3Config(config), catalog, getDatabase(config), this::getCopier, getSqlOperations(), getNameTransformer());
  }

  @Override
  public void attemptWriteToPersistence(JsonNode config) throws Exception {
    S3Copier.attemptWriteToPersistence(getS3Config(config));
  }

  @Override
  public ExtendedNameTransformer getNameTransformer() {
    return new RedshiftSQLNameTransformer();
  }

  @Override
  public JdbcDatabase getDatabase(JsonNode config) throws Exception {
    var jdbcConfig = RedshiftInsertDestination.getJdbcConfig(config);
    return Databases.createJdbcDatabase(
            jdbcConfig.get("username").asText(),
            jdbcConfig.has("password") ? jdbcConfig.get("password").asText() : null,
            jdbcConfig.get("jdbc_url").asText(),
            RedshiftInsertDestination.DRIVER_CLASS);
  }

  @Override
  public SqlOperations getSqlOperations() {
    return new RedshiftSqlOperations();
  }

  private String getConfiguredSchema(JsonNode config) {
    return config.get("schema").asText();
  }

  private S3Config getS3Config(JsonNode config) {
    return new S3Config(
            config.get("s3_bucket_name").asText(),
            config.get("access_key_id").asText(),
            config.get("secret_access_key").asText(),
            config.get("s3_bucket_region").asText()
    );
  }

  private Copier getCopier(String configuredSchema,
                           S3Config s3Config,
                           String stagingFolder,
                           DestinationSyncMode destinationSyncMode,
                           AirbyteStream airbyteStream,
                           ExtendedNameTransformer nameTransformer,
                           JdbcDatabase jdbcDatabase,
                           SqlOperations sqlOperations) {
    return new S3CopierSupplier(RedshiftCopier::new).get(configuredSchema, s3Config, stagingFolder, destinationSyncMode, airbyteStream, nameTransformer,
            jdbcDatabase, sqlOperations);
  }

  public static boolean isPresent(JsonNode config) {
    var bucketNode = config.get("s3_bucket_name");
    var regionNode = config.get("s3_bucket_region");
    var accessKeyIdNode = config.get("access_key_id");
    var secretAccessKeyNode = config.get("secret_access_key");

    // Since region is a Json schema enum with an empty string default, we consider the empty string an
    // unset field.
    var emptyRegion = regionNode == null || regionNode.asText().equals("");

    if (bucketNode == null && emptyRegion && accessKeyIdNode == null && secretAccessKeyNode == null) {
      return false;
    }

    if (bucketNode == null || regionNode == null || accessKeyIdNode == null || secretAccessKeyNode == null) {
      throw new RuntimeException("Error: Partially missing S3 Configuration.");
    }
    return true;
  }

}
