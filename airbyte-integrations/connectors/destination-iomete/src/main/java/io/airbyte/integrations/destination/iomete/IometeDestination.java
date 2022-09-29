/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iomete;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.copy.CopyConsumerFactory;
import io.airbyte.integrations.destination.jdbc.copy.CopyDestination;
import io.airbyte.integrations.destination.s3.S3BaseChecks;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.integrations.destination.s3.S3StorageOperations;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;

import javax.sql.DataSource;
import java.util.Locale;
import java.util.function.Consumer;

public class IometeDestination extends CopyDestination {

  public IometeDestination() {
    super("database_schema");
  }

  public static void main(String[] args) throws Exception {
    new IntegrationRunner(new IometeDestination()).run(args);
  }

  @Override
  public AirbyteMessageConsumer getConsumer(final JsonNode config,
                                            final ConfiguredAirbyteCatalog catalog,
                                            final Consumer<AirbyteMessage> outputRecordCollector) {
    final IometeDestinationConfig iometeConfig = IometeDestinationConfig.get(config);
    final DataSource dataSource = getDataSource(config);
    return CopyConsumerFactory.create(
            outputRecordCollector,
            dataSource,
            getDatabase(dataSource),
            getSqlOperations(),
            getNameTransformer(),
            iometeConfig,
            catalog,
            new IometeStreamCopierFactory(),
            iometeConfig.getDatabaseSchema());
  }

  @Override
  public void checkPersistence(final JsonNode config) {
    final IometeDestinationConfig iometeConfig = IometeDestinationConfig.get(config);
    final S3DestinationConfig s3Config = iometeConfig.getS3DestinationConfig();
    S3BaseChecks.attemptS3WriteAndDelete(
            new S3StorageOperations(getNameTransformer(), s3Config.getS3Client(), s3Config),
            s3Config, "");
  }

  @Override
  public ExtendedNameTransformer getNameTransformer() {
    return new IometeNameTransformer();
  }

  @Override
  public DataSource getDataSource(final JsonNode config) {
    final IometeDestinationConfig iometeConfig = IometeDestinationConfig.get(config);
    return DataSourceFactory.create(
            iometeConfig.getIometeUsername(),
            iometeConfig.getIometePassword(),
            IometeConstants.IOMETE_DRIVER_CLASS,
            getIometeConnectionString(iometeConfig)
    );
  }

  @Override
  public JdbcDatabase getDatabase(DataSource dataSource) {
    return new DefaultJdbcDatabase(dataSource);
  }

  @Override
  public SqlOperations getSqlOperations() {
    return new IometeSqlOperations();
  }

  static String getIometeConnectionString(final IometeDestinationConfig iometeConfig) {
    return String.format(IometeConstants.IOMETE_URL_FORMAT_STRING,
            iometeConfig.getLakehouseHostname(),
            iometeConfig.getLakehousePort(),
            Boolean.toString(iometeConfig.isSSL()).toLowerCase(Locale.ROOT),
            iometeConfig.getAccountNumber(),
            iometeConfig.getLakehouseName());
  }

}