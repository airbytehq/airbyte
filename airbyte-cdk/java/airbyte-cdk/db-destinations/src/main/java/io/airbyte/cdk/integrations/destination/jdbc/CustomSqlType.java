/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.jdbc;

import java.sql.SQLType;

/**
 * Custom SqlType definition when there is no mapping in {@link java.sql.JDBCType}
 *
 * @param name
 * @param vendor
 * @param vendorTypeNumber
 */
public record CustomSqlType(String name, String vendor, Integer vendorTypeNumber) implements SQLType {

  @Override
  public String getName() {
    return name;
  }

  @Override
  public String getVendor() {
    return vendor;
  }

  @Override
  public Integer getVendorTypeNumber() {
    return vendorTypeNumber;
  }

}
