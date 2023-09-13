package io.airbyte.integrations.destination.jdbc;

import java.sql.SQLType;
public record CustomSqlType(String name, String vendor, Integer vendorTypeNumber) implements SQLType {

  @Override
  public String getName() {
    return this.name;
  }

  @Override
  public String getVendor() {
    return this.vendor;
  }

  @Override
  public Integer getVendorTypeNumber() {
    return this.vendorTypeNumber;
  }
}
