/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.jdbc.dto;

import com.google.common.base.Objects;

/**
 * The class to store values from privileges table
 */
public class JdbcPrivilegeDto {

  private String grantee;
  private String tableName;
  private String schemaName;
  private String privilege;

  public JdbcPrivilegeDto(String grantee, String tableName, String schemaName, String privilege) {
    this.grantee = grantee;
    this.tableName = tableName;
    this.schemaName = schemaName;
    this.privilege = privilege;
  }

  public String getGrantee() {
    return grantee;
  }

  public String getTableName() {
    return tableName;
  }

  public String getSchemaName() {
    return schemaName;
  }

  public String getPrivilege() {
    return privilege;
  }

  public static JdbcPrivilegeDtoBuilder builder() {
    return new JdbcPrivilegeDtoBuilder();
  }

  public static class JdbcPrivilegeDtoBuilder {

    private String grantee;
    private String tableName;
    private String schemaName;
    private String privilege;

    public JdbcPrivilegeDtoBuilder grantee(String grantee) {
      this.grantee = grantee;
      return this;
    }

    public JdbcPrivilegeDtoBuilder tableName(String tableName) {
      this.tableName = tableName;
      return this;
    }

    public JdbcPrivilegeDtoBuilder schemaName(String schemaName) {
      this.schemaName = schemaName;
      return this;
    }

    public JdbcPrivilegeDtoBuilder privilege(String privilege) {
      this.privilege = privilege;
      return this;
    }

    public JdbcPrivilegeDto build() {
      return new JdbcPrivilegeDto(grantee, tableName, schemaName, privilege);
    }

  }

  @Override
  public boolean equals(Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    JdbcPrivilegeDto that = (JdbcPrivilegeDto) o;
    return Objects.equal(grantee, that.grantee) && Objects.equal(tableName, that.tableName)
        && Objects.equal(schemaName, that.schemaName) && Objects.equal(privilege, that.privilege);
  }

  @Override
  public int hashCode() {
    return Objects.hashCode(grantee, tableName, schemaName, privilege);
  }

  @Override
  public String toString() {
    return "JdbcPrivilegeDto{" +
        "grantee='" + grantee + '\'' +
        ", columnName='" + tableName + '\'' +
        ", schemaName='" + schemaName + '\'' +
        ", privilege='" + privilege + '\'' +
        '}';
  }

}
