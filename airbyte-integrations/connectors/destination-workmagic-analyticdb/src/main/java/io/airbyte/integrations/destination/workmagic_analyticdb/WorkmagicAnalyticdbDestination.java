/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.workmagic_analyticdb;

import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.base.Destination;
import io.airbyte.cdk.integrations.base.IntegrationRunner;
import io.airbyte.cdk.integrations.base.spec_modification.SpecModifyingDestination;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.mysql.MySQLDestination;
import io.airbyte.integrations.destination.mysql.MySQLNameTransformer;
import io.airbyte.integrations.destination.mysql.MySQLSqlOperations;
import io.airbyte.protocol.models.v0.ConnectorSpecification;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.sql.SQLException;
import java.util.List;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class WorkmagicAnalyticdbDestination extends SpecModifyingDestination implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(WorkmagicAnalyticdbDestination.class);

  public WorkmagicAnalyticdbDestination() {
    super(new MySQLDestinationHack());
  }

  @Override
  public ConnectorSpecification modifySpec(final ConnectorSpecification originalSpec) {
    final ConnectorSpecification spec = Jsons.clone(originalSpec);
    return spec;
  }

  public static void main(final String[] args) throws Exception {
    final Destination destination = new WorkmagicAnalyticdbDestination();
    LOGGER.info("starting destination: {}", WorkmagicAnalyticdbDestination.class);
    new IntegrationRunner(destination).run(args);
    LOGGER.info("completed destination: {}", WorkmagicAnalyticdbDestination.class);
  }

  public static class MySQLDestinationHack extends MySQLDestination {

    public MySQLDestinationHack() {
      super(DRIVER_CLASS, new MySQLNameTransformer(), new MySQLSqlOperationsHack());
    }

  }

  public static class MySQLSqlOperationsHack extends MySQLSqlOperations {

    @Override
    public void insertRecordsInternal(final JdbcDatabase database,
        final List<PartialAirbyteMessage> records,
        final String schemaName,
        final String tmpTableName)
        throws SQLException {
      // todo add tenant to records
      super.insertRecordsInternal(database, records, schemaName, tmpTableName);
    }

    VersionCompatibility isCompatibleVersion(final JdbcDatabase database) throws SQLException {
      final double version = getVersion(database);
      return new VersionCompatibility(version, true);
    }

  }

}
