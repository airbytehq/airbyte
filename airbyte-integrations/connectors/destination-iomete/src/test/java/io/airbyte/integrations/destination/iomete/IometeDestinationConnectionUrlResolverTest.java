/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iomete;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

class IometeDestinationConnectionUrlResolverTest {


  @Test
  public void testIncorrectConnectionUrls() {
    final String withIncorrectPrefix = "irbyte://iomete.com/12312421312/default";
    final String withoutHostname = "airbyte://12312421312/default";
    final String withoutAccountNumber = "airbyte://iomete.com/default";
    final String withoutLakehouseName = "airbyte://iomete.com/12312421312/";

    final IometeDestinationConnectionUrlResolver config = IometeDestinationConnectionUrlResolver.create(withIncorrectPrefix);
    assertEquals(IometeConstants.LAKEHOUSE_HOSTNAME_EXAMPLE, config.lakehouseHostname);

    final IometeDestinationConnectionUrlResolver config1 = IometeDestinationConnectionUrlResolver.create(withoutHostname);
    assertEquals(IometeConstants.ACCOUNT_NUMBER_EXAMPLE, config1.accountNumber);

    final IometeDestinationConnectionUrlResolver config2 = IometeDestinationConnectionUrlResolver.create(withoutAccountNumber);
    assertEquals(IometeConstants.DEFAULT_LAKEHOUSE_NAME, config2.lakehouseName);

    final IometeDestinationConnectionUrlResolver config3 = IometeDestinationConnectionUrlResolver.create(withoutLakehouseName);
    assertEquals(IometeConstants.LAKEHOUSE_HOSTNAME_EXAMPLE, config3.lakehouseHostname);
    assertEquals(IometeConstants.DEFAULT_LAKEHOUSE_NAME, config3.lakehouseName);
  }

  @Test
  public void TestCorrectConnectionUrl() {
    final String completeString = "airbyte://iomete.com/12312421312/default";

    final IometeDestinationConnectionUrlResolver config = IometeDestinationConnectionUrlResolver.create(completeString);
    assertEquals("iomete.com", config.lakehouseHostname);
    assertEquals("12312421312", config.accountNumber);
    assertEquals("default", config.lakehouseName);
  }

}
