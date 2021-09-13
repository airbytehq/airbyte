package io.airbyte.integrations.destination.databricks;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.integrations.destination.s3.parquet.S3ParquetFormatConfig;

public class DatabricksDestinationConfig {

  static final String DEFAULT_DATABRICKS_PORT = "443";
  static final String DEFAULT_DATABASE_SCHEMA = "public";

  private final String databricksServerHostname;
  private final String databricksHttpPath;
  private final String databricksPort;
  private final String databricksPersonalAccessToken;
  private final String databaseSchema;
  private final S3DestinationConfig s3DestinationConfig;

  public DatabricksDestinationConfig(String databricksServerHostname,
                                     String databricksHttpPath,
                                     String databricksPort,
                                     String databricksPersonalAccessToken,
                                     String databaseSchema,
                                     String s3BucketName,
                                     String s3BucketPath,
                                     String s3BucketRegion,
                                     String s3AccessKeyId,
                                     String s3SecretAccessKey) {
    this.databricksServerHostname = databricksServerHostname;
    this.databricksHttpPath = databricksHttpPath;
    this.databricksPort = databricksPort;
    this.databricksPersonalAccessToken = databricksPersonalAccessToken;
    this.databaseSchema = databaseSchema;
    this.s3DestinationConfig = new S3DestinationConfig(
        "",
        s3BucketName,
        s3BucketPath,
        s3BucketRegion,
        s3AccessKeyId,
        s3SecretAccessKey,
        getDefaultParquetConfig());
  }

  public static DatabricksDestinationConfig get(JsonNode config) {
    return new DatabricksDestinationConfig(
        config.get("databricks_server_hostname").asText(),
        config.get("databricks_http_path").asText(),
        config.has("databricks_port") ? config.get("databricks_port").asText() : DEFAULT_DATABRICKS_PORT,
        config.get("databricks_personal_access_token").asText(),
        config.has("database_schema") ? config.get("database_schema").asText() : DEFAULT_DATABASE_SCHEMA,
        config.get("s3_bucket_name").asText(),
        config.get("s3_bucket_path").asText(),
        config.get("s3_bucket_region").asText(),
        config.get("s3_access_key_id").asText(),
        config.get("s3_secret_access_key").asText());
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

  public S3DestinationConfig getS3DestinationConfig() {
    return s3DestinationConfig;
  }
}
