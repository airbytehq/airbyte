/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.glue;

import static io.airbyte.integrations.destination.iceberg.IcebergIntegrationTestUtil.ICEBERG_IMAGE_NAME;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.cdk.integrations.standardtest.destination.DestinationAcceptanceTest;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.iceberg.IcebergIntegrationTestUtil;
import io.airbyte.integrations.destination.iceberg.config.catalog.IcebergCatalogConfig;
import io.airbyte.integrations.destination.iceberg.config.catalog.IcebergCatalogConfigFactory;
import io.airbyte.integrations.destination.iceberg.config.format.DataFileFormat;
import java.nio.file.Path;
import java.util.HashSet;
import java.util.List;
import org.apache.commons.lang.RandomStringUtils;
import org.apache.iceberg.aws.glue.GlueCatalog;
import org.apache.iceberg.catalog.Namespace;
import org.apache.iceberg.catalog.TableIdentifier;
import org.jetbrains.annotations.NotNull;
import org.jetbrains.annotations.Nullable;
import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.Test;

public abstract class BaseIcebergGlueCatalogS3IntegrationTest extends DestinationAcceptanceTest {

  private JsonNode config;
  private GlueCatalog glueCatalog;
  private String database;

  public abstract DataFileFormat getFormat();

  @Override
  protected void setup(final @NotNull TestDestinationEnv testEnv, final @NotNull HashSet<String> TEST_SCHEMAS) {
    final JsonNode baseConfig = Jsons.deserialize(IOs.readFile(Path.of("secrets/s3_glue_config.json")));
    database = "ab_iceberg_tests_" + RandomStringUtils.randomAlphabetic(4).toLowerCase();
    config = Jsons.clone(baseConfig);
    final JsonNode formatConfigJson = config.get("format_config");
    if (formatConfigJson instanceof ObjectNode) {
      ((ObjectNode) formatConfigJson).put("format", getFormat().getConfigValue());
    }
    final JsonNode catalogConfigJson = config.get("catalog_config");
    if (catalogConfigJson instanceof ObjectNode) {
      ((ObjectNode) catalogConfigJson).put("database", database);
    }
    IcebergCatalogConfig catalogConfig = IcebergCatalogConfigFactory.fromJsonNodeConfig(config);
    glueCatalog = (GlueCatalog) catalogConfig.genCatalog();
    glueCatalog.createNamespace(Namespace.of(database));
  }

  @Override
  protected void tearDown(final @NotNull TestDestinationEnv testEnv) {
    List<TableIdentifier> tables = glueCatalog.listTables(Namespace.of(database));
    // Clean up tables since Glue will refuse to drop namespace (no cascade option in catalog API)
    for (TableIdentifier table : tables) {
      glueCatalog.dropTable(table, true);
    }
    glueCatalog.dropNamespace(Namespace.of(database));
  }

  @Override
  protected @NotNull String getImageName() {
    return ICEBERG_IMAGE_NAME;
  }

  @Override
  protected @NotNull JsonNode getConfig() {
    return config;
  }

  @Override
  protected JsonNode getFailCheckConfig() {
    final JsonNode badConfig = Jsons.clone(config);
    final JsonNode storageConfig = badConfig.get("storage_config");
    if (storageConfig instanceof ObjectNode) {
      ((ObjectNode) storageConfig).put("access_key_id", "badAccessKey");
      ((ObjectNode) storageConfig).put("secret_access_key", "uselessSecret");
    }
    return badConfig;
  }

  @Override
  protected @NotNull List<JsonNode> retrieveRecords(final TestDestinationEnv testEnv,
                                                    final @NotNull String streamName,
                                                    final @NotNull String namespace,
                                                    final @NotNull JsonNode streamSchema)
      throws Exception {
    return IcebergIntegrationTestUtil.retrieveRecords(config, namespace, streamName);
  }

  @Nullable
  @Override
  protected String getDefaultSchema(@NotNull JsonNode config) throws Exception {
    return database;
  }

  @Test
  @Disabled("Existing connector does not support flattened rows yet")
  @Override
  public void testAirbyteFields() throws Exception {}

}
