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

package io.airbyte.integrations.destination.databricks;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.integrations.destination.s3.parquet.S3ParquetFormatConfig;

/**
 * Currently only S3 is supported. So the data source config is always {@link S3DestinationConfig}.
 */
public class DatabricksDestinationConfig {

  static final String DEFAULT_DATABRICKS_PORT = "443";
  static final String DEFAULT_DATABASE_SCHEMA = "public";
  static final boolean DEFAULT_PURGE_STAGING_DATA = true;

  private final String databricksServerHostname;
  private final String databricksHttpPath;
  private final String databricksPort;
  private final String databricksPersonalAccessToken;
  private final String databaseSchema;
  private final boolean purgeStagingData;
  private final S3DestinationConfig s3DestinationConfig;

  public DatabricksDestinationConfig(String databricksServerHostname,
                                     String databricksHttpPath,
                                     String databricksPort,
                                     String databricksPersonalAccessToken,
                                     String databaseSchema,
                                     boolean purgeStagingData,
                                     S3DestinationConfig s3DestinationConfig) {
    this.databricksServerHostname = databricksServerHostname;
    this.databricksHttpPath = databricksHttpPath;
    this.databricksPort = databricksPort;
    this.databricksPersonalAccessToken = databricksPersonalAccessToken;
    this.databaseSchema = databaseSchema;
    this.purgeStagingData = purgeStagingData;
    this.s3DestinationConfig = s3DestinationConfig;
  }

  public static DatabricksDestinationConfig get(JsonNode config) {
    return new DatabricksDestinationConfig(
        config.get("databricks_server_hostname").asText(),
        config.get("databricks_http_path").asText(),
        config.has("databricks_port") ? config.get("databricks_port").asText() : DEFAULT_DATABRICKS_PORT,
        config.get("databricks_personal_access_token").asText(),
        config.has("database_schema") ? config.get("database_schema").asText() : DEFAULT_DATABASE_SCHEMA,
        config.has("purge_staging_data") ? config.get("purge_staging_data").asBoolean() : DEFAULT_PURGE_STAGING_DATA,
        getDataSource(config.get("data_source")));
  }

  public static S3DestinationConfig getDataSource(JsonNode dataSource) {
    return new S3DestinationConfig(
        "",
        dataSource.get("s3_bucket_name").asText(),
        dataSource.get("s3_bucket_path").asText(),
        dataSource.get("s3_bucket_region").asText(),
        dataSource.get("s3_access_key_id").asText(),
        dataSource.get("s3_secret_access_key").asText(),
        getDefaultParquetConfig());
  }

  public String getDatabricksServerHostname() {
    return databricksServerHostname;
  }

  private static S3ParquetFormatConfig getDefaultParquetConfig() {
    return new S3ParquetFormatConfig(new ObjectMapper().createObjectNode());
  }

  public String getDatabricksHttpPath() {
    return databricksHttpPath;
  }

  public String getDatabricksPort() {
    return databricksPort;
  }

  public String getDatabricksPersonalAccessToken() {
    return databricksPersonalAccessToken;
  }

  public String getDatabaseSchema() {
    return databaseSchema;
  }

  public boolean isPurgeStagingData() {
    return purgeStagingData;
  }

  public S3DestinationConfig getS3DestinationConfig() {
    return s3DestinationConfig;
  }

}
