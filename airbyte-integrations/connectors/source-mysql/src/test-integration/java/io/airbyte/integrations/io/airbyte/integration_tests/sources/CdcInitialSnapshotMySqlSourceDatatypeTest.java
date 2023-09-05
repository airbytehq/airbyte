/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import static io.airbyte.integrations.io.airbyte.integration_tests.sources.utils.TestConstants.INITIAL_CDC_WAITING_SECONDS;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Database;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.integrations.util.HostPortResolver;
import java.nio.file.Path;
import java.sql.SQLException;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;
import org.testcontainers.containers.MySQLContainer;
import org.testcontainers.utility.DockerImageName;

public class CdcInitialSnapshotMySqlSourceDatatypeTest extends AbstractMySqlSourceDatatypeTest {

  @Override
  protected Path getConfigFilePath() {
    return Path.of("secrets/cdc-initial-snapshot-mysql-datatype-test-config.json");
  }

  @Override
  public boolean testCatalog() {
    return true;
  }

}
