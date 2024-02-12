/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import com.google.cloud.bigquery.BigQueryException;
import io.airbyte.cdk.integrations.base.AirbyteExceptionHandler;
import io.airbyte.cdk.integrations.base.IntegrationCommand;
import io.airbyte.cdk.integrations.base.context.AirbyteConnectorRunner;

public class BigQueryDestination {

  public static void main(final String[] args) {
    AirbyteExceptionHandler.addThrowableForDeinterpolation(BigQueryException.class);
    AirbyteConnectorRunner.run(IntegrationCommand.class, args);
  }

}
