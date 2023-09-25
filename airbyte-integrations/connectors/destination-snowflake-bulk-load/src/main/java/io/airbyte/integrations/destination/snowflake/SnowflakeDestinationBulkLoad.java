/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.spec_modification.SpecModifyingDestination;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.v0.ConnectorSpecification;
import java.util.Set;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import io.airbyte.integrations.destination.jdbc.AbstractJdbcDestination;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.SerializedAirbyteMessageConsumer;
import io.airbyte.integrations.base.TypingAndDedupingFlag;
import io.airbyte.integrations.base.destination.typing_deduping.CatalogParser;
import io.airbyte.integrations.base.destination.typing_deduping.DefaultTyperDeduper;
import io.airbyte.integrations.base.destination.typing_deduping.NoopTyperDeduper;
import io.airbyte.integrations.base.destination.typing_deduping.ParsedCatalog;
import io.airbyte.integrations.base.destination.typing_deduping.TypeAndDedupeOperationValve;
import io.airbyte.integrations.base.destination.typing_deduping.TyperDeduper;
import io.airbyte.integrations.destination.NamingConventionTransformer;
import io.airbyte.integrations.destination.jdbc.AbstractJdbcDestination;
import io.airbyte.integrations.destination.snowflake.typing_deduping.SnowflakeDestinationHandler;
import io.airbyte.integrations.destination.snowflake.typing_deduping.SnowflakeSqlGenerator;
import io.airbyte.integrations.destination.snowflake.typing_deduping.SnowflakeV1V2Migrator;
import io.airbyte.integrations.destination.staging.StagingConsumerFactory;
import io.airbyte.integrations.destination.staging.StagingOperations;
import io.airbyte.protocol.models.v0.*;
import java.util.Collections;
import java.util.Map;
import java.util.function.Consumer;
import javax.sql.DataSource;
import org.apache.commons.lang3.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import static io.airbyte.integrations.destination.snowflake.OssCloudEnvVarConsts.AIRBYTE_CLOUD;
import static io.airbyte.integrations.destination.snowflake.OssCloudEnvVarConsts.AIRBYTE_OSS;

public class SnowflakeDestinationBulkLoad extends AbstractJdbcDestination implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(SnowflakeDestinationBulkLoad.class);
  private static final String PROPERTIES = "properties";
  public static final String TUNNEL_METHOD = "tunnel_method";
  public static final String NO_TUNNEL = "NO_TUNNEL";
  public static final String SSL_MODE = "ssl_mode";
  public static final String MODE = "mode";
  public static final String SSL_MODE_ALLOW = "allow";
  public static final String SSL_MODE_PREFER = "prefer";
  public static final String SSL_MODE_DISABLE = "disable";

  private static final String RAW_SCHEMA_OVERRIDE = "raw_data_schema";
  private static final String BULK_LOAD_FILE_FORMAT = "bulk_load_file_format";
  private static final String BULK_LOAD_S3_STAGES = "bulk_load_s3_stages";

  private final String airbyteEnvironment;

  // public SnowflakeDestinationBulkLoad(final String airbyteEnvironment) {
  //   this(new SnowflakeSQLNameTransformer(), airbyteEnvironment);
  // }

  public SnowflakeDestinationBulkLoad() {
    this(new SnowflakeSQLNameTransformer());
  }

  public SnowflakeDestinationBulkLoad(final NamingConventionTransformer nameTransformer) {
    super("", nameTransformer, new SnowflakeBulkLoadSqlOperations(nameTransformer));
    this.airbyteEnvironment = AIRBYTE_CLOUD;
    // this.airbyteEnvironment = airbyteEnvironment;
  }

  // @Override
  // public ConnectorSpecification modifySpec(final ConnectorSpecification originalSpec) {
  //   final ConnectorSpecification spec = Jsons.clone(originalSpec);
  //   ((ObjectNode) spec.getConnectionSpecification().get(PROPERTIES)).remove(JdbcUtils.SSL_KEY);
  //   return spec;
  // }

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) {
    final NamingConventionTransformer nameTransformer = getNamingResolver();
    final SnowflakeBulkLoadSqlOperations snowflakeBulkLoadSqlOperations = new SnowflakeBulkLoadSqlOperations(nameTransformer);
    final DataSource dataSource = getDataSource(config);
    try {
      final JdbcDatabase database = getDatabase(dataSource);
      final String outputSchema = nameTransformer.getIdentifier(config.get("schema").asText());
      attemptTableOperations(outputSchema, database, nameTransformer,
          snowflakeBulkLoadSqlOperations, true);
      return new AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.SUCCEEDED);
    } catch (final Exception e) {
      LOGGER.error("Exception while checking connection: ", e);
      return new AirbyteConnectionStatus()
          .withStatus(AirbyteConnectionStatus.Status.FAILED)
          .withMessage("Could not connect with provided configuration. \n" + e.getMessage());
    } finally {
      try {
        DataSourceFactory.close(dataSource);
      } catch (final Exception e) {
        LOGGER.warn("Unable to close data source.", e);
      }
    }
  }

  public static void main(final String[] args) throws Exception {
    final Destination destination = new SnowflakeDestinationBulkLoad();
    LOGGER.info("starting destination: {}", SnowflakeDestinationBulkLoad.class);
    new IntegrationRunner(destination).run(args);
    LOGGER.info("completed destination: {}", SnowflakeDestinationBulkLoad.class);
  }


  public static class StageNotFoundException extends Exception {

    public StageNotFoundException(String message) {
      super(message);
    }

  }

  public static class InvalidValueException extends Exception {

    public InvalidValueException(String message) {
      super(message);
    }

  }

  public static String findMatchingStageName(Map<String, String> s3StageMap, String s3Path) throws StageNotFoundException {
    for (Map.Entry<String, String> entry : s3StageMap.entrySet()) {
      if (s3Path.startsWith(entry.getValue())) {
        return entry.getKey();
      }
    }
    throw new StageNotFoundException("No matching Snowflake stage name found for S3 path: " + s3Path);
  }

  public static String getRelativePath(String rootPath, String fullS3Path) throws InvalidValueException {
    if (fullS3Path.startsWith(rootPath)) {
      return fullS3Path.substring(rootPath.length());
    }
    throw new InvalidValueException("S3 path " + fullS3Path + " does not start with root path " + rootPath);
  }

  @Override
  public ConnectorSpecification spec() throws Exception {
    return null;
  }

  @Override
  protected DataSource getDataSource(final JsonNode config) {
    return SnowflakeDatabase.createDataSource(config, airbyteEnvironment);
  }

  @Override
  protected JdbcDatabase getDatabase(final DataSource dataSource) {
    return SnowflakeDatabase.getDatabase(dataSource);
  }

  @Override
  protected Map<String, String> getDefaultConnectionProperties(final JsonNode config) {
    return Collections.emptyMap();
  }

  // this is a no op since we override getDatabase.
  @Override
  public JsonNode toJdbcConfig(final JsonNode config) {
    return Jsons.emptyObject();
  }

  // @Override
  // public AirbyteMessageConsumer getConsumer(JsonNode config, ConfiguredAirbyteCatalog catalog, Consumer<AirbyteMessage> outputRecordCollector) {
  //   return (AirbyteMessageConsumer) getSerializedMessageConsumer(config, catalog, outputRecordCollector);
  // }

}
