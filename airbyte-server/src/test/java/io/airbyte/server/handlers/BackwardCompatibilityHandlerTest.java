/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.handlers;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.Collections;
import java.util.Set;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class BackwardCompatibilityHandlerTest {

  private ConfigRepository configRepository;
  private SourceConnection sourceConnection;
  private final BackwardCompatibilityHandler handler = new BackwardCompatibilityHandler();

  @SuppressWarnings("unchecked")
  @BeforeEach
  void setUp() throws IOException {
    configRepository = mock(ConfigRepository.class);
  }

  @Test
  void testModifyMySqlReplicationMethodConfig() throws JsonValidationException, IOException {

    final JsonNode mySqlConfig =
        Jsons.deserialize(Files.readString(Paths.get("../airbyte-server/src/test/resources/json/backwardComp/mysql_repl_method_config.json")));
    final JsonNode mySqlSpec =
        Jsons.deserialize(Files.readString(Paths.get("../airbyte-server/src/test/resources/json/backwardComp/mysql_repl_method_spec.json")));

    sourceConnection = new SourceConnection().withConfiguration(mySqlConfig);

    handler.updateSourceConnectionForBackwardCompatibility("airbyte/source-mysql-strict-encrypt",
        sourceConnection,
        mySqlConfig,
        mySqlSpec,
        Set.of("$.replication_method: string found, object expected"),
        configRepository);
    assertEquals(Jsons.deserialize(Files.readString(
        Paths.get("../airbyte-server/src/test/resources/json/backwardComp/mysql_repl_method_modified_config.json"))),
        sourceConnection.getConfiguration());
  }

  @Test
  void testModifyMsSqlReplicationMethodConfig() throws JsonValidationException, IOException {

    final JsonNode msSqlConfig =
        Jsons.deserialize(Files.readString(Paths.get("../airbyte-server/src/test/resources/json/backwardComp/mssql_repl_method_config.json")));
    final JsonNode msSqlSpec =
        Jsons.deserialize(Files.readString(Paths.get("../airbyte-server/src/test/resources/json/backwardComp/mssql_repl_method_spec.json")));

    sourceConnection = new SourceConnection().withConfiguration(msSqlConfig);

    handler.updateSourceConnectionForBackwardCompatibility("airbyte/source-mssql-strict-encrypt",
        sourceConnection,
        msSqlConfig,
        msSqlSpec,
        Collections.emptySet(),
        configRepository);
    assertEquals(Jsons.deserialize(Files.readString(
        Paths.get("../airbyte-server/src/test/resources/json/backwardComp/mssql_repl_method_modified_config.json"))),
        sourceConnection.getConfiguration());
  }

}
