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

package io.airbyte.integrations.source.druid;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.integrations.standardtest.source.SourceAcceptanceTest;
import io.airbyte.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.Database;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.io.FileWriter;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import com.google.common.collect.ImmutableMap;
import io.airbyte.integrations.source.druid.DruidSource;

public class DruidSourceAcceptanceTest extends SourceAcceptanceTest {

  private static final String MODEL_FILE = "druid-model.json";
  private static final Logger LOGGER = LoggerFactory.getLogger(DruidSourceAcceptanceTest.class);
  private JsonNode config;

  @Override
  protected void setupEnvironment(TestDestinationEnv testEnv) {
    // TODO create new container. Ex: "new OracleContainer("epiclabs/docker-oracle-xe-11g");"
    // TODO make container started. Ex: "container.start();"
    // TODO init JsonNode config
    // TODO crete airbyte Database object "Databases.createJdbcDatabase(...)"
    // TODO insert test data to DB. Ex: "database.execute(connection-> ...)"

    FileWriter modelFile = null;
    // String model = "{ \"version\": \"1.0\", \"defaultSchema\": \"ecom\", \"schemas\": [ { \"type\": \"custom\", \"name\": \"ecom\", \"factory\": \"org.apache.calcite.adapter.druid.DruidSchemaFactory\", \"operand\": { \"url\": \"http://localhost:8082\", \"coordinatorUrl\": \"http://localhost:8081\" } } ] }" ;
    String model = "";

    try {
      modelFile = new FileWriter(MODEL_FILE);
      modelFile.write(model);
      modelFile.close();
    } catch (Exception e) {
      LOGGER.warn("Could not write model file \n");
    } finally {
      LOGGER.info("Created model file \n");
    }

    config = Jsons.jsonNode(ImmutableMap.builder()
        .put("username", "admin")
        .put("password", "admin")
        .put("jdbc_url", "jdbc:calcite:model=./druid-model-ecom.json")
        .build());

    final JdbcDatabase database = DruidSource.createDruidDatabase("admin", "admin", "jdbc:calcite:model=./druid-model-ecom.json", "org.apache.calcite.jdbc.Driver");

    // database.query(ctx -> {
    //   ctx.fetch("SELECT * FROM wikiticker;");
    //  return null;
    // });

    try {
      database.query("SELECT * FROM wikiticker;");
    } catch (Exception e) {
      LOGGER.warn("Query failed\n");
    } finally {
      LOGGER.warn("Query Successful\n");
    }
    // TODO close Database. Ex: "database.close();"
  }

  @Override
  protected void tearDown(TestDestinationEnv testEnv) {
    // TODO close container that was initialized in setup() method. Ex: "container.close();"
  }

  @Override
  protected String getImageName() {
    return "airbyte/source-druid:dev";
  }

  @Override
  protected ConnectorSpecification getSpec() throws Exception {
    return Jsons.deserialize(MoreResources.readResource("spec.json"), ConnectorSpecification.class);
  }

  @Override
  protected JsonNode getConfig() {
    return config;
  }

  @Override
  protected ConfiguredAirbyteCatalog getConfiguredCatalog() {
    // TODO Return the ConfiguredAirbyteCatalog with ConfiguredAirbyteStream objects
    return null;
  }

  @Override
  protected List<String> getRegexTests() {
    return Collections.emptyList();
  }

  @Override
  protected JsonNode getState() {
    return Jsons.jsonNode(new HashMap<>());
  }

}
