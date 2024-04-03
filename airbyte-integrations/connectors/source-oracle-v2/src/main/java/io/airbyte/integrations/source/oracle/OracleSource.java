/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.oracle;

import io.airbyte.cdk.AirbyteConnectorRunner;
import io.airbyte.cdk.IntegrationCommand;

public class OracleSource {

  static public void main(String[] args) {
    AirbyteConnectorRunner.run(AirbyteConnectorRunner.ConnectorType.SOURCE, IntegrationCommand.class, args);
  }

}
