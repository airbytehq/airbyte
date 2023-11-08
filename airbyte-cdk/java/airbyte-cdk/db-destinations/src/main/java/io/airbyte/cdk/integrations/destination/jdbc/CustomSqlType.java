/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.jdbc;

import java.sql.SQLType;

//TODO: Change it to something 
public record CustomSqlType(String name, String vendor, Integer vendorTypeNumber) implements SQLType {

  @Override
  public String getName() {
    return null;
  }

  @Override
  public String getVendor() {
    return null;
  }

  @Override
  public Integer getVendorTypeNumber() {
    return null;
  }

}
