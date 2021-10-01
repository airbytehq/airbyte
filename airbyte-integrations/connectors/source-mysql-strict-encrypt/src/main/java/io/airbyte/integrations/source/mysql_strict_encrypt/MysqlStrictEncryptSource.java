/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql_strict_encrypt;

import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.base.spec_modification.SpecModifyingSource;
import io.airbyte.integrations.source.mysql.MySqlSource;
import io.airbyte.protocol.models.ConnectorSpecification;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MysqlStrictEncryptSource extends SpecModifyingSource implements Source {

  private static final Logger LOGGER = LoggerFactory.getLogger(MysqlStrictEncryptSource.class);

  MysqlStrictEncryptSource() {
    super(MySqlSource.sshWrappedSource());
  }

  @Override
  public ConnectorSpecification modifySpec(final ConnectorSpecification originalSpec) {
    final ConnectorSpecification spec = Jsons.clone(originalSpec);
    ((ObjectNode) spec.getConnectionSpecification().get("properties")).remove("ssl");
    return spec;
  }

  public static void main(String[] args) throws Exception {
    final Source source = new MysqlStrictEncryptSource();
    LOGGER.info("starting source: {}", MysqlStrictEncryptSource.class);
    new IntegrationRunner(source).run(args);
    LOGGER.info("completed source: {}", MysqlStrictEncryptSource.class);
  }

}
