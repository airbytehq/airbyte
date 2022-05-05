/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.init;

import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.persistence.test.BaseDatabaseConfigPersistenceTest;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

public class YamlSeedDependantTest extends BaseDatabaseConfigPersistenceTest {

  @Test
  @DisplayName("When an unused connector has missing fields, add the missing fields, do not update its version")
  public void testNoUpdateOnConnectors() throws Exception {
    final StandardSourceDefinition currentSource = getSource().withDockerImageTag("0.1000.0").withDocumentationUrl(null).withSourceType(null);
    final StandardSourceDefinition latestSource = getSource().withDockerImageTag("0.99.0");
    final StandardSourceDefinition currentSourceWithNewFields = getSource().withDockerImageTag("0.1000.0");
    /*
     * final ConfigPersistence seedConfigPersistence = database.query(ctx -> {
     * configPersistence.updateConnectorDefinitions( ctx, ConfigSchema.STANDARD_SOURCE_DEFINITION,
     * YamlSeedConfigPersistence.getDefault() ) })
     *
     *
     * assertUpdateConnectorDefinition( Collections.singletonList(currentSource),
     * Collections.emptyList(), Collections.singletonList(latestSource),
     * Collections.singletonList(currentSourceWithNewFields));
     */
  }

}
