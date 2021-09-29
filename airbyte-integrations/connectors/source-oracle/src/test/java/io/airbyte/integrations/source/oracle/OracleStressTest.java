/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.oracle;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.OracleJdbcStreamingQueryConfiguration;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.source.jdbc.AbstractJdbcSource;
import io.airbyte.integrations.source.jdbc.test.JdbcStressTest;
import java.util.Optional;
import java.util.Set;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Disabled;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.testcontainers.containers.OracleContainer;

/**
 * Runs the stress tests in the source-jdbc test module. We want this module to run these tests
 * itself as a sanity check. The trade off here is that this class is duplicated from the one used
 * in source-postgres.
 */
@Disabled
class OracleStressTest extends JdbcStressTest {

  private static OracleContainer ORACLE_DB;

  private JsonNode config;

  @BeforeAll
  static void init() {
    ORACLE_DB = new OracleContainer("epiclabs/docker-oracle-xe-11g");
    ORACLE_DB.start();
  }

  @BeforeEach
  public void setup() throws Exception {
    TABLE_NAME = "ID_AND_NAME";
    COL_ID = "ID";
    COL_NAME = "NAME";
    COL_ID_TYPE = "NUMBER(38,0)";
    INSERT_STATEMENT = "INTO id_and_name (id, name) VALUES (%s,'picard-%s')";

    config = Jsons.jsonNode(ImmutableMap.builder()
        .put("host", ORACLE_DB.getHost())
        .put("port", ORACLE_DB.getFirstMappedPort())
        .put("sid", ORACLE_DB.getSid())
        .put("username", ORACLE_DB.getUsername())
        .put("password", ORACLE_DB.getPassword())
        .build());

    super.setup();
  }

  @Override
  public Optional<String> getDefaultSchemaName() {
    return Optional.of("SYSTEM");
  }

  @Override
  public AbstractJdbcSource getSource() {
    return new OracleTestSource();
  }

  @Override
  public JsonNode getConfig() {
    return config;
  }

  @Override
  public String getDriverClass() {
    return OracleTestSource.DRIVER_CLASS;
  }

  @AfterAll
  static void cleanUp() {
    ORACLE_DB.close();
  }

  private static class OracleTestSource extends AbstractJdbcSource implements Source {

    private static final Logger LOGGER = LoggerFactory.getLogger(OracleTestSource.class);

    static final String DRIVER_CLASS = "oracle.jdbc.OracleDriver";

    public OracleTestSource() {
      super(DRIVER_CLASS, new OracleJdbcStreamingQueryConfiguration());
    }

    @Override
    public JsonNode toDatabaseConfig(JsonNode config) {
      final ImmutableMap.Builder<Object, Object> configBuilder = ImmutableMap.builder()
          .put("username", config.get("username").asText())
          .put("jdbc_url", String.format("jdbc:oracle:thin:@//%s:%s/xe",
              config.get("host").asText(),
              config.get("port").asText(),
              config.get("sid").asText()));

      if (config.has("password")) {
        configBuilder.put("password", config.get("password").asText());
      }

      return Jsons.jsonNode(configBuilder.build());
    }

    @Override
    public Set<String> getExcludedInternalNameSpaces() {
      // need to add SYSTEM too but for that need create another user when creating the container.
      return Set.of("APEX_040000", "CTXSYS", "FLOWS_FILES", "HR", "MDSYS", "OUTLN", "SYS", "XDB");
    }

    public static void main(String[] args) throws Exception {
      final Source source = new OracleTestSource();
      LOGGER.info("starting source: {}", OracleTestSource.class);
      new IntegrationRunner(source).run(args);
      LOGGER.info("completed source: {}", OracleTestSource.class);
    }

  }

}
