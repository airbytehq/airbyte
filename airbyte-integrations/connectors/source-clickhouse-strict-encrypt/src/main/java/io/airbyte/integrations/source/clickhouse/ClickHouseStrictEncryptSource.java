/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.clickhouse;

import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.base.spec_modification.SpecModifyingSource;
import io.airbyte.protocol.models.v0.ConnectorSpecification;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ClickHouseStrictEncryptSource extends SpecModifyingSource implements Source {

  private static final Logger LOGGER = LoggerFactory.getLogger(ClickHouseStrictEncryptSource.class);

  public ClickHouseStrictEncryptSource() {
    super(ClickHouseSource.getWrappedSource());
  }

  @Override
  public ConnectorSpecification modifySpec(final ConnectorSpecification originalSpec) {
    final ConnectorSpecification spec = Jsons.clone(originalSpec);
    // SSL property should be enabled by default for secure versions of connectors
    // that can be used in the Airbyte cloud. User should not be able to change this property.
    ((ObjectNode) spec.getConnectionSpecification().get("properties")).remove(JdbcUtils.SSL_KEY);
    return spec;
  }

  public static void main(final String[] args) throws Exception {
    final Source source = new ClickHouseStrictEncryptSource();
    LOGGER.info("starting source: {}", ClickHouseStrictEncryptSource.class);
    new IntegrationRunner(source).run(args);
    LOGGER.info("completed source: {}", ClickHouseStrictEncryptSource.class);
  }

}
