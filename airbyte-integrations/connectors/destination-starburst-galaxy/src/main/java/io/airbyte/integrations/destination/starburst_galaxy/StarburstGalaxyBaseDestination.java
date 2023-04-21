/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.starburst_galaxy;

import static io.airbyte.db.factory.DatabaseDriver.STARBURST;
import static io.airbyte.integrations.destination.jdbc.copy.CopyConsumerFactory.create;
import static io.airbyte.integrations.destination.starburst_galaxy.StarburstGalaxyConstants.CATALOG_SCHEMA;
import static io.airbyte.integrations.destination.starburst_galaxy.StarburstGalaxyConstants.STARBURST_GALAXY_DRIVER_CLASS;
import static io.airbyte.integrations.destination.starburst_galaxy.StarburstGalaxyDestinationConfig.get;
import static java.lang.String.format;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.destination.StandardNameTransformer;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.copy.CopyDestination;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.util.function.Consumer;
import javax.sql.DataSource;

public abstract class StarburstGalaxyBaseDestination
    extends CopyDestination {

  public StarburstGalaxyBaseDestination() {
    super(CATALOG_SCHEMA);
  }

  @Override
  public void checkPersistence(JsonNode config) {
    checkPersistence(get(config).storageConfig());
  }

  protected abstract void checkPersistence(StarburstGalaxyStagingStorageConfig galaxyStorageConfig);

  @Override
  public AirbyteMessageConsumer getConsumer(final JsonNode config,
                                            final ConfiguredAirbyteCatalog catalog,
                                            final Consumer<AirbyteMessage> outputRecordCollector) {
    final StarburstGalaxyDestinationConfig starburstGalaxyConfig = get(config);
    final DataSource dataSource = getDataSource(config);
    return create(
        outputRecordCollector,
        dataSource,
        getDatabase(dataSource),
        getSqlOperations(),
        getNameTransformer(),
        starburstGalaxyConfig,
        catalog,
        getStreamCopierFactory(),
        starburstGalaxyConfig.galaxyCatalogSchema());
  }

  protected abstract StarburstGalaxyStreamCopierFactory getStreamCopierFactory();

  @Override
  public StandardNameTransformer getNameTransformer() {
    return new StarburstGalaxyNameTransformer();
  }

  @Override
  public DataSource getDataSource(final JsonNode config) {
    final StarburstGalaxyDestinationConfig galaxyDestinationConfig = get(config);
    return DataSourceFactory.create(
        galaxyDestinationConfig.galaxyUsername(),
        galaxyDestinationConfig.galaxyPassword(),
        STARBURST_GALAXY_DRIVER_CLASS,
        getGalaxyConnectionString(galaxyDestinationConfig));
  }

  @Override
  public JdbcDatabase getDatabase(final DataSource dataSource) {
    return new DefaultJdbcDatabase(dataSource);
  }

  @Override
  public SqlOperations getSqlOperations() {
    return new StarburstGalaxySqlOperations();
  }

  public static String getGalaxyConnectionString(final StarburstGalaxyDestinationConfig galaxyDestinationConfig) {
    return format(STARBURST.getUrlFormatString(),
        galaxyDestinationConfig.galaxyServerHostname(),
        galaxyDestinationConfig.galaxyPort(),
        galaxyDestinationConfig.galaxyCatalog());
  }

}
